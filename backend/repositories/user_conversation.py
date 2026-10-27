import uuid
import logging
from pathlib import Path
import json as JSON
from typing import Mapping, Any

LLM_INSTRUCTIONS_PATH = (Path(__file__).parent.parent / 'llm_instructions/docs_chat.md').read_text(encoding='utf-8')

from sqlalchemy import and_, delete, func, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.conversation_message import ConversationMessage
from models.user_conversation import UserConversation
from models.user_file import UserFile
from repositories.openai import (
    OpenAIStreamEvent,
    create_openai_conversation,
    create_openai_response,
    get_response_output_text,
    stream_openai_response_text,
    create_llm_embedding,
)
from repositories.file_chunk import (
    list_file_chunks,
)
from schemas.conversation_message import (
    ConversationMessageCreate,
    ConversationMessageRead,
    ConversationMessageUpdate,
)
from schemas.user_conversation import (
    UserConversationCreate,
    UserConversationRead,
    UserConversationUpdate,
)
from core.errors import OwnershipError, ScrappyError

logger = logging.getLogger(__name__)

CHUNKS_PER_RELEVANT_FILE = 5


def _conversation_name_from_message(message_text: str) -> str:
    conversation_name = " ".join(message_text.split()).strip()
    if not conversation_name:
        return "New Conversation"

    max_length = 60
    if len(conversation_name) <= max_length:
        return conversation_name

    return f"{conversation_name[:max_length].rstrip()}..."


async def _conversation_read(
    user_conversation: UserConversation,
    session: AsyncSession,
    include_messages: bool = False,
) -> UserConversationRead:
    conversation_read = UserConversationRead.model_validate(user_conversation)

    if include_messages is True:
        conversation_read.conversation_messages = await list_conversation_messages(
            user_id=user_conversation.user_id,
            conversation_id=user_conversation.conversation_id,
            session=session,
        )

    return conversation_read


async def create_user_conversation(
    user_id: uuid.UUID,
    user_conversation: UserConversationCreate,
    session: AsyncSession,
) -> UserConversationRead | None:
    requested_file_ids = set(user_conversation.relevant_file_ids)
    if requested_file_ids:
        owned_file_ids = set(
            await session.scalars(
                select(UserFile.file_id).where(
                    UserFile.user_id == user_id,
                    UserFile.status != "deleted",
                    UserFile.file_id.in_(requested_file_ids),
                )
            )
        )
        if owned_file_ids != requested_file_ids:
            raise OwnershipError("One or more referenced files are not owned by the current user")

    new_user_conversation: dict[str, str | uuid.UUID | list[uuid.UUID] | None] = {
        "user_id": user_id,
        "conversation_name": _conversation_name_from_message(
            user_conversation.user_message.message_text
        ),
        "relevant_file_ids": user_conversation.relevant_file_ids,
        "openai_conversation_id": user_conversation.openai_conversation_id,
    }

    try:
        created_user_conversation = await session.scalar(
            insert(UserConversation)
            .values(**new_user_conversation)
            .returning(UserConversation)
        )
        await session.commit()
        if created_user_conversation is None:
            raise ScrappyError("Failed to create user conversation")

        user_conversation_id = created_user_conversation.conversation_id

        new_conversation_message = await create_conversation_message(
            user_id=user_id,
            conversation_id=user_conversation_id,
            conversation_message=user_conversation.user_message,
            session=session,
        )
        if new_conversation_message is None:
            raise ScrappyError("Failed to create initial conversation message")

        return await _conversation_read(created_user_conversation, session=session, include_messages=True)
    except IntegrityError:
        await session.rollback()
        return None


async def list_user_conversations(
    user_id: uuid.UUID,
    session: AsyncSession,
    limit: int = 50,
    offset: int = 0,
) -> list[UserConversationRead]:
    latest_messages = (
        select(
            ConversationMessage.user_conversation_id.label("conversation_id"),
            ConversationMessage.message_text.label("preview"),
            func.row_number()
            .over(
                partition_by=ConversationMessage.user_conversation_id,
                order_by=ConversationMessage.created_at.desc(),
            )
            .label("row_number"),
        )
        .subquery()
    )
    result = await session.execute(
        select(UserConversation, latest_messages.c.preview)
        .outerjoin(
            latest_messages,
            and_(
                latest_messages.c.conversation_id == UserConversation.id,
                latest_messages.c.row_number == 1,
            ),
        )
        .where(UserConversation.user_id == user_id)
        .order_by(UserConversation.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    conversation_reads: list[UserConversationRead] = []
    for user_conversation, preview in result.all():
        conversation_read = await _conversation_read(
            user_conversation,
            session=session,
        )
        if preview is not None:
            conversation_read.preview = preview.strip()
        conversation_reads.append(conversation_read)

    return conversation_reads


async def get_user_conversation(
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
    session: AsyncSession,
    get_messages: bool = False,
) -> UserConversationRead | None:
    user_conversation = await session.scalar(
        select(UserConversation).where(
            UserConversation.user_id == user_id,
            UserConversation.conversation_id == conversation_id,
        )
    )

    if user_conversation is None:
        return None

    return await _conversation_read(
        user_conversation,
        session=session,
        include_messages=get_messages,
    )


async def update_user_conversation(
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
    user_conversation_update: UserConversationUpdate,
    session: AsyncSession,
) -> UserConversationRead | None:
    update_values = user_conversation_update.model_dump(exclude_unset=True)
    existing_user_conversation = await session.scalar(
        select(UserConversation).where(
            UserConversation.user_id == user_id,
            UserConversation.conversation_id == conversation_id,
        )
    )

    if existing_user_conversation is None:
        return None

    if not update_values:
        return await _conversation_read(existing_user_conversation, session=session)

    requested_file_ids = set(update_values.get("relevant_file_ids") or [])
    if requested_file_ids:
        owned_file_ids = set(
            await session.scalars(
                select(UserFile.file_id).where(
                    UserFile.user_id == user_id,
                    UserFile.status != "deleted",
                    UserFile.file_id.in_(requested_file_ids),
                )
            )
        )
        if owned_file_ids != requested_file_ids:
            raise OwnershipError("One or more referenced files are not owned by the current user")

    try:
        updated_user_conversation = await session.scalar(
            update(UserConversation)
            .where(UserConversation.id == existing_user_conversation.id)
            .values(**update_values)
            .returning(UserConversation)
        )
        await session.commit()
    except IntegrityError:
        await session.rollback()
        return None

    if updated_user_conversation is None:
        return None

    return await _conversation_read(updated_user_conversation, session=session)


async def check_file_ownership(user_id: uuid.UUID, file_id: uuid.UUID, session: AsyncSession) -> bool:
    result = await session.scalar(
        select(UserFile.file_id).where(
            UserFile.user_id == user_id,
            UserFile.file_id == file_id,
            UserFile.status != "deleted",
        )
    )
    return result is not None


async def update_user_conversation_files(
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
    file_id: uuid.UUID,
    session: AsyncSession,
) -> UserConversationRead | None:
    existing_user_conversation = await session.scalar(
        select(UserConversation).where(
            UserConversation.user_id == user_id,
            UserConversation.conversation_id == conversation_id,
        )
    )

    user_owns_file = await check_file_ownership(user_id, file_id, session)
    if not user_owns_file:
        raise OwnershipError("File is not owned by the current user")

    if existing_user_conversation is None:
        return None

    existing_conversation_files = existing_user_conversation.relevant_file_ids or []

    if file_id in existing_conversation_files:
        existing_conversation_files = [
            existing_file_id
            for existing_file_id in existing_conversation_files
            if existing_file_id != file_id
        ]
    else:
        existing_conversation_files.append(file_id)

    try:
        updated_user_conversation = await session.scalar(
            update(UserConversation)
            .where(UserConversation.id == existing_user_conversation.id)
            .values(relevant_file_ids=existing_conversation_files)
            .returning(UserConversation)
        )
        await session.commit()
    except IntegrityError:
        await session.rollback()
        return None

    if updated_user_conversation is None:
        return None

    return await _conversation_read(updated_user_conversation, session=session)


async def delete_user_conversation(
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
    session: AsyncSession,
) -> bool:
    existing_user_conversation = await session.scalar(
        select(UserConversation).where(
            UserConversation.user_id == user_id,
            UserConversation.conversation_id == conversation_id,
        )
    )

    if existing_user_conversation is None:
        return False

    await session.execute(
        delete(UserConversation).where(UserConversation.id == existing_user_conversation.id)
    )
    await session.commit()

    return True


async def create_llm_response_conversation_message(
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
    message_text: str,
    session: AsyncSession,
    llm_message_id: str | None = None,
) -> ConversationMessageRead | None:
    conversation_message_create = ConversationMessageCreate(
        message_text=message_text,
        sender_is_agent=True,
        llm_message_id=llm_message_id,
    )

    return await create_conversation_message(
        user_id=user_id,
        conversation_id=conversation_id,
        conversation_message=conversation_message_create,
        session=session,
    )


async def get_or_create_openai_conversation_id(
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
    session: AsyncSession,
) -> Mapping[str, Any]:

    ret: dict[str, Any] = {
        "openai_conversation_id": None,
        "relevant_file_ids": None,
    }
    user_conversation = await session.scalar(
        select(UserConversation).where(
            UserConversation.user_id == user_id,
            UserConversation.conversation_id == conversation_id,
        )
    )

    if user_conversation is None:
        return ret

    if user_conversation.openai_conversation_id is not None:
        # return user_conversation.openai_conversation_id
        ret["openai_conversation_id"] = user_conversation.openai_conversation_id
        ret["relevant_file_ids"] = user_conversation.relevant_file_ids
        return ret

    openai_conversation = await create_openai_conversation(
        metadata={
            "user_id": str(user_id),
            "conversation_id": str(conversation_id),
        }
    )
    openai_conversation_id = openai_conversation.get("id")
    if not isinstance(openai_conversation_id, str):
        return ret

    await session.execute(
        update(UserConversation)
        .where(UserConversation.id == user_conversation.id)
        .values(openai_conversation_id=openai_conversation_id)
    )
    await session.commit()

    return {
        "openai_conversation_id": openai_conversation_id,
        "relevant_file_ids": user_conversation.relevant_file_ids
    }


async def _build_relevant_file_instructions(
    user_id: uuid.UUID,
    relevant_file_ids: list[uuid.UUID] | None,
    message_text: str,
    session: AsyncSession,
) -> str:
    relevant_file_chunks_by_file: list[str] = []
    if relevant_file_ids:
        embedding = await create_llm_embedding(message_text)
        for relevant_file_id in relevant_file_ids:
            user_file = await session.scalar(
                select(UserFile).where(
                    UserFile.user_id == user_id,
                    UserFile.file_id == relevant_file_id,
                    UserFile.status != "deleted",
                )
            )
            file_label = (
                f"{user_file.original_filename} ({relevant_file_id})"
                if user_file is not None
                else str(relevant_file_id)
            )
            file_chunks = await list_file_chunks(
                session=session,
                embedding=embedding,
                limit=CHUNKS_PER_RELEVANT_FILE,
                file_id=relevant_file_id,
            )
            relevant_file_chunks_by_file.append(
                f"Data from file {file_label}:\n"
                + "\n\n".join(chunk.chunk_text for chunk in file_chunks)
            )

    return JSON.dumps(
        {
            "instructions": LLM_INSTRUCTIONS_PATH,
            "relevant_file_chunks": relevant_file_chunks_by_file,
        }
    )


async def create_openai_response_conversation_message(
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
    message_text: str,
    session: AsyncSession,
) -> ConversationMessageRead | None:
    conversation_state = await get_or_create_openai_conversation_id(
        user_id=user_id,
        conversation_id=conversation_id,
        session=session,
    )
    openai_conversation_id = conversation_state.get("openai_conversation_id")
    if not isinstance(openai_conversation_id, str):
        return None

    instructions = await _build_relevant_file_instructions(
        user_id=user_id,
        relevant_file_ids=conversation_state.get("relevant_file_ids"),
        message_text=message_text,
        session=session,
    )
    openai_response = await create_openai_response(
        input=message_text,
        conversation=openai_conversation_id,
        instructions=instructions,
        metadata={
            "user_id": str(user_id),
            "conversation_id": str(conversation_id),
        },
    )
    response_text = get_response_output_text(openai_response)
    if not response_text:
        response_text = "I could not generate a response."

    response_id = openai_response.get("id")

    return await create_llm_response_conversation_message(
        user_id=user_id,
        conversation_id=conversation_id,
        message_text=response_text,
        session=session,
        llm_message_id=response_id if isinstance(response_id, str) else None,
    )


async def stream_openai_response_conversation_text(
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
    message_text: str,
    session: AsyncSession,
):
    conversation_state = await get_or_create_openai_conversation_id(
        user_id=user_id,
        conversation_id=conversation_id,
        session=session,
    )
    relevant_file_ids = conversation_state.get("relevant_file_ids")
    openai_conversation_id = conversation_state.get("openai_conversation_id")

    if not openai_conversation_id:
        yield OpenAIStreamEvent(event_type="error", text="Conversation is not ready")
        return

    instructions = await _build_relevant_file_instructions(
        user_id=user_id,
        relevant_file_ids=relevant_file_ids,
        message_text=message_text,
        session=session,
    )

    async for event in stream_openai_response_text(
        input=message_text,
        conversation=openai_conversation_id,
        metadata={
            "user_id": str(user_id),
            "conversation_id": str(conversation_id),
        },
        instructions=instructions,
    ):
        yield event


async def create_conversation_message(
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
    conversation_message: ConversationMessageCreate,
    session: AsyncSession,
) -> ConversationMessageRead | None:
    user_conversation = await session.scalar(
        select(UserConversation).where(
            UserConversation.user_id == user_id,
            UserConversation.conversation_id == conversation_id,
        )
    )

    if user_conversation is None:
        return None

    created_conversation_message = await session.scalar(
        insert(ConversationMessage)
        .values(
            user_conversation_id=user_conversation.id,
            message_text=conversation_message.message_text,
            sender_is_agent=conversation_message.sender_is_agent,
            llm_message_id=conversation_message.llm_message_id,
        )
        .returning(ConversationMessage)
    )
    await session.commit()

    if created_conversation_message is None:
        return None

    return ConversationMessageRead.model_validate(created_conversation_message)


async def list_conversation_messages(
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
    session: AsyncSession,
) -> list[ConversationMessageRead]:
    result = await session.scalars(
        select(ConversationMessage)
        .join(UserConversation, ConversationMessage.user_conversation_id == UserConversation.id)
        .where(
            UserConversation.user_id == user_id,
            UserConversation.conversation_id == conversation_id,
        )
        .order_by(ConversationMessage.created_at.asc())
    )

    return [ConversationMessageRead.model_validate(message) for message in result]


async def get_conversation_message(
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
    message_id: int,
    session: AsyncSession,
) -> ConversationMessageRead | None:
    conversation_message = await session.scalar(
        select(ConversationMessage)
        .join(UserConversation, ConversationMessage.user_conversation_id == UserConversation.id)
        .where(
            UserConversation.user_id == user_id,
            UserConversation.conversation_id == conversation_id,
            ConversationMessage.id == message_id,
        )
    )

    if conversation_message is None:
        return None

    return ConversationMessageRead.model_validate(conversation_message)


async def update_conversation_message(
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
    message_id: int,
    conversation_message_update: ConversationMessageUpdate,
    session: AsyncSession,
) -> ConversationMessageRead | None:
    existing_conversation_message = await session.scalar(
        select(ConversationMessage)
        .join(UserConversation, ConversationMessage.user_conversation_id == UserConversation.id)
        .where(
            UserConversation.user_id == user_id,
            UserConversation.conversation_id == conversation_id,
            ConversationMessage.id == message_id,
        )
    )

    if existing_conversation_message is None:
        return None

    update_values = conversation_message_update.model_dump(exclude_unset=True)
    if not update_values:
        return ConversationMessageRead.model_validate(existing_conversation_message)

    updated_conversation_message = await session.scalar(
        update(ConversationMessage)
        .where(ConversationMessage.id == existing_conversation_message.id)
        .values(**update_values)
        .returning(ConversationMessage)
    )
    await session.commit()

    if updated_conversation_message is None:
        return None

    return ConversationMessageRead.model_validate(updated_conversation_message)


async def delete_conversation_message(
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
    message_id: int,
    session: AsyncSession,
) -> bool:
    existing_conversation_message = await session.scalar(
        select(ConversationMessage)
        .join(UserConversation, ConversationMessage.user_conversation_id == UserConversation.id)
        .where(
            UserConversation.user_id == user_id,
            UserConversation.conversation_id == conversation_id,
            ConversationMessage.id == message_id,
        )
    )

    if existing_conversation_message is None:
        return False

    await session.execute(
        delete(ConversationMessage).where(
            ConversationMessage.id == existing_conversation_message.id
        )
    )
    await session.commit()

    return True
