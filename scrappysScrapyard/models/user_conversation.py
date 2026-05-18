import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Integer,
    DateTime,
    String,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class UserConversation(Base):
    __tablename__ = "user_conversation"
    __table_args__ = (
        Index("ix_user_file_user_id", "user_id"),
        Index("ix_user_file_created_at", "created_at"),
        UniqueConstraint(
            "user_id",
            "conversation_id",
            name="uq_user_file_user_id_conversation_id",
        ),        {"schema": "app"},
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        default=uuid.uuid4,
        unique=True,
    )

    conversation_name: Mapped[str] = mapped_column(String(255), nullable=False)

    relevant_file_ids: Mapped[list[uuid.UUID] | None] = mapped_column(
        ARRAY(UUID(as_uuid=True)),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
