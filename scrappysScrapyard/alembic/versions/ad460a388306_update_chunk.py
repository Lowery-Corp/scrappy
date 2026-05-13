"""update chunk

Revision ID: ad460a388306
Revises: bd6b157ce350
Create Date: 2026-05-13 20:17:57.941244
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ad460a388306"
down_revision: Union[str, Sequence[str], None] = "bd6b157ce350"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # If chunks are derived data, clear them and regenerate after migration.
    op.execute("DELETE FROM app.file_chunk")

    # Drop old FK before changing the column type.
    op.drop_constraint(
        "file_chunk_file_id_fkey",
        "file_chunk",
        schema="app",
        type_="foreignkey",
    )

    # Convert integer column to UUID.
    # Since table is empty now, NULL::uuid is safe during type conversion.
    op.alter_column(
        "file_chunk",
        "file_id",
        existing_type=sa.Integer(),
        type_=sa.UUID(),
        existing_nullable=False,
        schema="app",
        postgresql_using="NULL::uuid",
    )

    # Recreate FK to app.user_file.id.
    op.create_foreign_key(
        "file_chunk_file_id_fkey",
        "file_chunk",
        "user_file",
        ["file_id"],
        ["file_id"],
        source_schema="app",
        referent_schema="app",
        ondelete="CASCADE",
    )

    # One file can have many chunks, but each chunk_index should be unique per file.
    op.create_unique_constraint(
        "uq_file_chunk_file_id_chunk_index",
        "file_chunk",
        ["file_id", "chunk_index"],
        schema="app",
    )

    op.create_index(
        "ix_file_job_file_id",
        "file_job",
        ["file_id"],
        unique=False,
        schema="app",
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index("ix_file_job_file_id", table_name="file_job", schema="app")

    op.drop_constraint(
        "uq_file_chunk_file_id_chunk_index",
        "file_chunk",
        schema="app",
        type_="unique",
    )

    op.drop_constraint(
        "file_chunk_file_id_fkey",
        "file_chunk",
        schema="app",
        type_="foreignkey",
    )

    op.execute("DELETE FROM app.file_chunk")

    op.alter_column(
        "file_chunk",
        "file_id",
        existing_type=sa.UUID(),
        type_=sa.Integer(),
        existing_nullable=False,
        schema="app",
        postgresql_using="NULL::integer",
    )

    op.create_foreign_key(
        "file_chunk_file_id_fkey",
        "file_chunk",
        "user_file",
        ["file_id"],
        ["id"],
        source_schema="app",
        referent_schema="app",
        ondelete="CASCADE",
    )