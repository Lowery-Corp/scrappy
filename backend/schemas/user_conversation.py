import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from schemas.conversation_message import ConversationMessageRead, ConversationMessageCreate


class UserConversationCreate(BaseModel):
    user_message: ConversationMessageCreate
    relevant_file_ids: list[uuid.UUID] = Field(default_factory=list)
    openai_conversation_id: str | None = None


class UserConversationUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    conversation_name: str | None = None
    relevant_file_ids: list[uuid.UUID] | None = Field(default=None, alias="file_ids")
    openai_conversation_id: str | None = None


class UserConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: uuid.UUID
    conversation_id: uuid.UUID
    conversation_name: str
    preview: str | None = None
    openai_conversation_id: str | None = None
    conversation_messages: list[ConversationMessageRead] = Field(default_factory=list)
    relevant_file_ids: list[uuid.UUID] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    @field_validator("relevant_file_ids", mode="before")
    @classmethod
    def default_relevant_file_ids(cls, value: list[uuid.UUID] | None) -> list[uuid.UUID]:
        return value or []
