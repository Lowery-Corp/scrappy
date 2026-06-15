import json
import uuid
from collections.abc import AsyncIterator
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from db.dependencies import get_session
from repositories.openai import OpenAIRepositoryError
from repositories.user_conversation import (
    create_conversation_message,
    create_user_conversation,
    create_llm_response_conversation_message,
    create_openai_response_conversation_message,
    delete_conversation_message,
    delete_user_conversation,
    get_conversation_message,
    get_user_conversation,
    list_conversation_messages,
    list_user_conversations,
    stream_openai_response_conversation_text,
    update_conversation_message,
    update_user_conversation,
)
from schemas.conversation_message import (
    ConversationMessageCreate,
    ConversationMessageRead,
    ConversationMessageUpdate,
)
from schemas.user import AuthorizedUser
from schemas.user_conversation import (
    UserConversationCreate,
    UserConversationRead,
    UserConversationUpdate,
)


def _sse_event(event: str, data: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def _stream_llm_response_events(
    user_id: uuid.UUID,
    conversation_id: uuid.UUID,
    message_text: str,
    session: AsyncSession,
) -> AsyncIterator[str]:
    response_parts: list[str] = []
    response_id: str | None = None

    try:
        async for event in stream_openai_response_conversation_text(
            user_id=user_id,
            conversation_id=conversation_id,
            message_text=message_text,
            session=session,
        ):
            if event.event_type == "delta":
                response_parts.append(event.text)
                yield _sse_event("delta", {"text": event.text})
            elif event.event_type == "completed":
                response_id = event.response_id
                if not response_parts and event.text:
                    response_parts.append(event.text)
    except OpenAIRepositoryError as exc:
        yield _sse_event("error", {"detail": str(exc)})
        return

    response_text = "".join(response_parts) or "I could not generate a response."
    response_with_llm = await create_llm_response_conversation_message(
        user_id=user_id,
        conversation_id=conversation_id,
        message_text=response_text,
        session=session,
        llm_message_id=response_id,
    )
    if response_with_llm is None:
        yield _sse_event("error", {"detail": "Conversation not found"})
        return

    yield _sse_event("message", response_with_llm.model_dump(mode="json"))
    yield _sse_event("done", {"ok": True})

router = APIRouter(tags=["conversations"])


@router.post("", response_model=UserConversationRead, status_code=status.HTTP_201_CREATED)
async def create_user_conversation_route(
    user_conversation: UserConversationCreate,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserConversationRead:

    created_user_conversation = await create_user_conversation(
        user_id=uuid.UUID(current_user.id),
        user_conversation=user_conversation,
        session=session,
    )

    if created_user_conversation is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conversation already exists or violates a database constraint",
        )

    try:
        response_with_llm = await create_openai_response_conversation_message(
            user_id=uuid.UUID(current_user.id),
            conversation_id=created_user_conversation.conversation_id,
            message_text=user_conversation.user_message.message_text,
            session=session,
        )
    except OpenAIRepositoryError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    if response_with_llm is not None:
        created_user_conversation.conversation_messages.append(response_with_llm)

    return created_user_conversation


@router.post("/stream", status_code=status.HTTP_201_CREATED)
async def create_user_conversation_stream_route(
    user_conversation: UserConversationCreate,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> StreamingResponse:
    user_id = uuid.UUID(current_user.id)
    created_user_conversation = await create_user_conversation(
        user_id=user_id,
        user_conversation=user_conversation,
        session=session,
    )

    if created_user_conversation is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conversation already exists or violates a database constraint",
        )

    async def stream() -> AsyncIterator[str]:
        yield _sse_event(
            "conversation",
            created_user_conversation.model_dump(mode="json"),
        )
        async for event in _stream_llm_response_events(
            user_id=user_id,
            conversation_id=created_user_conversation.conversation_id,
            message_text=user_conversation.user_message.message_text,
            session=session,
        ):
            yield event

    return StreamingResponse(stream(), media_type="text/event-stream")


@router.get("", response_model=list[UserConversationRead])
async def list_user_conversations_route(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[UserConversationRead]:
    return await list_user_conversations(
        user_id=uuid.UUID(current_user.id),
        session=session,
        limit=limit,
        offset=offset,
    )


@router.get("/{conversation_id}", response_model=UserConversationRead)
async def get_user_conversation_route(
    conversation_id: uuid.UUID,
    get_messages: bool = False,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserConversationRead:
    user_conversation = await get_user_conversation(
        user_id=uuid.UUID(current_user.id),
        conversation_id=conversation_id,
        session=session,
        get_messages=get_messages,
    )

    if user_conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return user_conversation


@router.patch("/{conversation_id}", response_model=UserConversationRead)
async def update_user_conversation_route(
    conversation_id: uuid.UUID,
    user_conversation_update: UserConversationUpdate,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserConversationRead:
    updated_user_conversation = await update_user_conversation(
        user_id=uuid.UUID(current_user.id),
        conversation_id=conversation_id,
        user_conversation_update=user_conversation_update,
        session=session,
    )

    if updated_user_conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or update violates a database constraint",
        )

    return updated_user_conversation


@router.delete("/{conversation_id}")
async def delete_user_conversation_route(
    conversation_id: uuid.UUID,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, bool]:
    deleted = await delete_user_conversation(
        user_id=uuid.UUID(current_user.id),
        conversation_id=conversation_id,
        session=session,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return {"ok": True}


@router.post(
    "/{conversation_id}/messages",
    response_model=ConversationMessageRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation_message_route(
    conversation_id: uuid.UUID,
    conversation_message: ConversationMessageCreate,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ConversationMessageRead:

    created_conversation_message = await create_conversation_message(
        user_id=uuid.UUID(current_user.id),
        conversation_id=conversation_id,
        conversation_message=conversation_message,
        session=session,
    )
    if created_conversation_message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    try:
        response_with_llm = await create_openai_response_conversation_message(
            user_id=uuid.UUID(current_user.id),
            conversation_id=conversation_id,
            message_text=created_conversation_message.message_text,
            session=session,
        )
    except OpenAIRepositoryError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    if response_with_llm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return response_with_llm


@router.post(
    "/{conversation_id}/messages/stream",
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation_message_stream_route(
    conversation_id: uuid.UUID,
    conversation_message: ConversationMessageCreate,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> StreamingResponse:
    user_id = uuid.UUID(current_user.id)
    created_conversation_message = await create_conversation_message(
        user_id=user_id,
        conversation_id=conversation_id,
        conversation_message=conversation_message,
        session=session,
    )
    if created_conversation_message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    async def stream() -> AsyncIterator[str]:
        yield _sse_event(
            "user_message",
            created_conversation_message.model_dump(mode="json"),
        )
        async for event in _stream_llm_response_events(
            user_id=user_id,
            conversation_id=conversation_id,
            message_text=created_conversation_message.message_text,
            session=session,
        ):
            yield event

    return StreamingResponse(stream(), media_type="text/event-stream")


@router.get("/{conversation_id}/messages", response_model=list[ConversationMessageRead])
async def list_conversation_messages_route(
    conversation_id: uuid.UUID,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[ConversationMessageRead]:
    return await list_conversation_messages(
        user_id=uuid.UUID(current_user.id),
        conversation_id=conversation_id,
        session=session,
    )


@router.get("/{conversation_id}/messages/{message_id}", response_model=ConversationMessageRead)
async def get_conversation_message_route(
    conversation_id: uuid.UUID,
    message_id: int,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ConversationMessageRead:
    conversation_message = await get_conversation_message(
        user_id=uuid.UUID(current_user.id),
        conversation_id=conversation_id,
        message_id=message_id,
        session=session,
    )

    if conversation_message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation message not found",
        )

    return conversation_message


@router.patch("/{conversation_id}/messages/{message_id}", response_model=ConversationMessageRead)
async def update_conversation_message_route(
    conversation_id: uuid.UUID,
    message_id: int,
    conversation_message_update: ConversationMessageUpdate,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ConversationMessageRead:
    updated_conversation_message = await update_conversation_message(
        user_id=uuid.UUID(current_user.id),
        conversation_id=conversation_id,
        message_id=message_id,
        conversation_message_update=conversation_message_update,
        session=session,
    )

    if updated_conversation_message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation message not found",
        )

    return updated_conversation_message


@router.delete("/{conversation_id}/messages/{message_id}")
async def delete_conversation_message_route(
    conversation_id: uuid.UUID,
    message_id: int,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, bool]:
    deleted = await delete_conversation_message(
        user_id=uuid.UUID(current_user.id),
        conversation_id=conversation_id,
        message_id=message_id,
        session=session,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation message not found",
        )

    return {"ok": True}
