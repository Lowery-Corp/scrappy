from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ConversationMessageCreate(BaseModel):
    message_text: str
    sender_is_agent: bool = False
    llm_message_id: str | None = None


class ConversationMessageUpdate(BaseModel):
    message_text: str | None = None
    sender_is_agent: bool | None = None
    llm_message_id: str | None = None


class ConversationMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_conversation_id: int
    message_text: str
    sender_is_agent: bool
    llm_message_id: str | None = None
    created_at: datetime
