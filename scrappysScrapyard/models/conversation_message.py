from datetime import datetime, timezone
from sqlalchemy import (
    Integer,
    DateTime,
    ForeignKey,
    Text,
    Index,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class ConversationMessage(Base):
    __tablename__ = "conversation_message"
    __table_args__ = (
        Index("ix_conversation_message_user_conversation_id", "user_conversation_id"),
        Index("ix_conversation_message_llm_message_id", "llm_message_id"),
        {"schema": "app"},
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_conversation_id: Mapped[int] = mapped_column(
        ForeignKey("app.user_conversation.id", ondelete="CASCADE"),
        nullable=False,
    )
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    sender_is_agent: Mapped[bool] = mapped_column(nullable=False, default=True)
    llm_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

