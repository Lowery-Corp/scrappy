import uuid
from datetime import datetime
from sqlalchemy import update, select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from models.user_conversation import UserConversation
from models.conversation_message import ConversationMessage
from schemas.user_conversation import UserConversationCreate, UserConversationRead
from schemas.conversation_message import ConversationMessageCreate, ConversationMessageRead


async def insert_user_conversation(
    user_id: uuid.UUID,
    session: AsyncSession
) -> UserConversationRead:

    new_user_conversation = UserConversation(
        user_id=user_id,
        title=f"Conversation {datetime.utcnow().isoformat()}",
    )

    get_user_conversation_result = UserConversationRead.model_validate(
        new_user_conversation
    )

    return get_user_conversation_result


async def select_user_conversations(
    user_id: uuid.UUID,
    session: AsyncSession,
    user_conversation_id: uuid.UUID | None = None,
) -> list[UserConversationRead]:

    user_conversation_result = None

    if not user_conversation_id:
        user_conversation_result = await session.execute(
            select(UserConversation)
            .where(UserConversation.user_id == user_id)
            .order_by(UserConversation.created_at.desc()
            )
        )
    else:
        user_conversation_result = await session.execute(
            select(UserConversation)
                .where(
                    UserConversation.user_id == user_id,
                    UserConversation.id == user_conversation_id,
                ).order_by(UserConversation.created_at.desc()
            )
        )

    ret: list[UserConversationRead] = []
    for uc in user_conversation_result.scalars().all():
        conversation_messages = await session.execute(
            select(ConversationMessage)
            .where(ConversationMessage.user_conversation_id == uc.id)
            .order_by(ConversationMessage.created_at.asc())
        )

        message_conversations: list[ConversationMessageRead] = []
        for cm in conversation_messages.scalars().all():
            messaage = ConversationMessageRead.model_validate(cm)
            message_conversations.append(messaage)
        uc_read = UserConversationRead.model_validate(uc)

        uc_read.conversation_messages = message_conversations
        ret.append(uc_read)

    return ret
