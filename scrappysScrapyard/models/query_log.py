import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class AgentQueryLog(Base):
    __tablename__ = "agent_query_log"
    __table_args__ = (
        Index("ix_agent_query_log_user_id", "user_id"),
        Index("ix_agent_query_log_user_conversation_id", "user_conversation_id"),
        Index("ix_agent_query_log_conversation_message_id", "conversation_message_id"),
        {"schema": "app"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    user_conversation_id: Mapped[int] = mapped_column(
        ForeignKey("app.user_conversation.id", ondelete="CASCADE"),
        nullable=False,
    )
    conversation_message_id: Mapped[int] = mapped_column(
        ForeignKey("app.conversation_message.id", ondelete="CASCADE"),
        nullable=False,
    )
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_query_text: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(255), nullable=False)
    response_text: Mapped[str] = mapped_column(Text, nullable=False)
    response_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )