from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = "86b07f781b51"
down_revision: Union[str, Sequence[str], None] = "b0c6bec63d5c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.add_column(
        "file_chunk",
        sa.Column("embedding", Vector(1536), nullable=True),
        schema="app",
    )

    op.create_index(
        "ix_file_chunk_embedding_status",
        "file_chunk",
        ["embedding_status"],
        unique=False,
        schema="app",
    )

    op.drop_column("file_chunk", "text", schema="app")

    # only do this after you backfill embeddings
    # op.alter_column("file_chunk", "embedding", nullable=False, schema="app")


def downgrade() -> None:
    op.add_column(
        "file_chunk",
        sa.Column("text", sa.Text(), nullable=False),
        schema="app",
    )

    op.drop_index(
        "ix_file_chunk_embedding_status",
        table_name="file_chunk",
        schema="app",
    )

    op.drop_column("file_chunk", "embedding", schema="app")