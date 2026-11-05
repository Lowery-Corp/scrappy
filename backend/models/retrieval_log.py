from datetime import datetime, timezone

from sqlalchemy import (
    Integer,
    String,
    DateTime,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class RetrievalLog(Base):
    __tablename__ = "retrieval_log"
    __table_args__ = (
        Index("ix_retrieval_log_query_log_id", "query_log_id"),
        Index("ix_retrieval_log_retrieved_file_id", "retrieved_file_id"),
        Index("ix_retrieval_log_retrieval_score", "retrieval_score"),
        Index("ix_retrieval_log_retrieval_rank", "retrieval_rank"),
        {"schema": "app"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    query_log_id: Mapped[int] = mapped_column(
        ForeignKey("app.user_file.id", ondelete="CASCADE"),
        nullable=False,
    )
    retrieved_file_id: Mapped[int] = mapped_column(
        ForeignKey("app.user_file.id", ondelete="CASCADE"),
        nullable=False,
    )
    retrieved_file_chunk_id: Mapped[int] = mapped_column(
        ForeignKey("app.file_chunk.id", ondelete="CASCADE"),
        nullable=True,
    )
    retrieval_score: Mapped[float] = mapped_column(nullable=False)
    retrieval_rank: Mapped[int] = mapped_column(nullable=False)
    retrieval_name: Mapped[str] = mapped_column(String(255), nullable=True)
    retrieval_strategy: Mapped[str] = mapped_column(String(255), nullable=True)
    filter_json: Mapped[dict] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
