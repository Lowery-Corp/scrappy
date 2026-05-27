from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ConversationMessageCreate(BaseModel):
    message_text: str
    sender_is_agent: bool = False


class ConversationMessageUpdate(BaseModel):
    message_text: str | None = None
    sender_is_agent: bool | None = None


class ConversationMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_conversation_id: int
    message_text: str
    sender_is_agent: bool
    created_at: datetime
