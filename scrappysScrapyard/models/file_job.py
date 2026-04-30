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


class FileJob(Base):
    __tablename__ = "file_job"
    __table_args__ = (
        Index("ix_file_job_file_id", "file_id"),
        Index("ix_file_job_status", "status"),
        Index("ix_file_job_job_type", "job_type"),
        Index("ix_file_job_created_at", "created_at"),
        {"schema": "app"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        default=uuid.uuid4,
        unique=True,
    )
    file_id: Mapped[int] = mapped_column(
        ForeignKey("app.user_file.id", ondelete="CASCADE"),
        nullable=False,
    )
    job_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    # examples:
    # "parse"
    # "chunk"
    # "embed"
    # "finalize"
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )
    # examples:
    # "pending"
    # "queued"
    # "running"
    # "completed"
    # "failed"
    # "cancelled"
    attempt_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    max_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3,
    )
    queue_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    worker_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    queued_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
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
