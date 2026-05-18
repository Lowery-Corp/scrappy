import uuid

from pydantic import BaseModel, ConfigDict

class ConversationMessageCreate(BaseModel):
    conversation_id: uuid.UUID
    message_text: str

class ConversationMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_conversation_id: uuid.UUID
    message_text: str



