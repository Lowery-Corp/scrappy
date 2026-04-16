from sqlalchemy import (
    Integer,
    String,
    ForeignKey,
    Text,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from db.base import Base


class FileChunk(Base):
    __tablename__ = "file_chunk"
    __table_args__ = (
        Index("ix_file_chunk_file_id", "file_id"),
        Index("ix_file_chunk_embedding_status", "embedding_status"),
        {"schema": "app"},
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    file_id: Mapped[int] = mapped_column(
        ForeignKey("app.user_file.id", ondelete="CASCADE"),
        nullable=False,
    )

    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)

    embedding: Mapped[list[float]] = mapped_column(
        Vector(1536),
        nullable=False,
    )

    token_count: Mapped[int] = mapped_column(Integer, nullable=False)

    embedding_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        server_default="pending",
    )