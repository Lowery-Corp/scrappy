import uuid

from pydantic import BaseModel, ConfigDict

from schemas.conversation_message import ConversationMessageRead


class UserConversationCreate(BaseModel):
    user_id: uuid.UUID
    conversation_name: str | None = None
    conversation_id: uuid.UUID | None = None
    relevant_file_ids: list[uuid.UUID] | None = None

class UserConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    conversation_id: uuid.UUID
    conversation_name: str

    conversation_messages: list[ConversationMessageRead] = []

    relevant_file_ids: list[uuid.UUID] | None
