"""updating jobs table to use file uuid

Revision ID: bd6b157ce350
Revises: 86b07f781b51
Create Date: 2026-05-08 20:05:15.656618
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = "bd6b157ce350"
down_revision: Union[str, Sequence[str], None] = "86b07f781b51"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Make file_chunk.embedding non-nullable.
    op.alter_column(
        "file_chunk",
        "embedding",
        existing_type=Vector(1536),
        nullable=False,
        schema="app",
    )

    # Drop the old FK from file_job.file_id -> user_file.id.
    op.drop_constraint(
        "file_job_file_id_fkey",
        "file_job",
        schema="app",
        type_="foreignkey",
    )

    # Add temporary UUID column.
    op.add_column(
        "file_job",
        sa.Column("file_uuid_tmp", postgresql.UUID(as_uuid=True), nullable=True),
        schema="app",
    )

    # Backfill UUIDs from app.user_file.file_id using the old integer ID relationship.
    op.execute(
        """
        UPDATE app.file_job AS fj
        SET file_uuid_tmp = uf.file_id
        FROM app.user_file AS uf
        WHERE fj.file_id = uf.id
        """
    )

    # Ensure there are no unmapped rows before making the column non-null.
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM app.file_job
                WHERE file_uuid_tmp IS NULL
            ) THEN
                RAISE EXCEPTION 'Cannot migrate app.file_job.file_id: some rows could not be mapped to app.user_file.file_id';
            END IF;
        END $$;
        """
    )

    # Drop old integer file_id.
    op.drop_column("file_job", "file_id", schema="app")

    # Rename temp UUID column to file_id.
    op.alter_column(
        "file_job",
        "file_uuid_tmp",
        new_column_name="file_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
        schema="app",
    )

    # Recreate FK from file_job.file_id -> user_file.file_id.
    op.create_foreign_key(
        "file_job_file_id_fkey",
        "file_job",
        "user_file",
        ["file_id"],
        ["file_id"],
        source_schema="app",
        referent_schema="app",
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Drop UUID FK.
    op.drop_constraint(
        "file_job_file_id_fkey",
        "file_job",
        schema="app",
        type_="foreignkey",
    )

    # Add temporary integer column.
    op.add_column(
        "file_job",
        sa.Column("file_id_int_tmp", sa.Integer(), nullable=True),
        schema="app",
    )

    # Backfill integer IDs from app.user_file.id using UUID relationship.
    op.execute(
        """
        UPDATE app.file_job AS fj
        SET file_id_int_tmp = uf.id
        FROM app.user_file AS uf
        WHERE fj.file_id = uf.file_id
        """
    )

    # Ensure all rows mapped.
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM app.file_job
                WHERE file_id_int_tmp IS NULL
            ) THEN
                RAISE EXCEPTION 'Cannot downgrade app.file_job.file_id: some rows could not be mapped back to app.user_file.id';
            END IF;
        END $$;
        """
    )

    # Drop UUID file_id.
    op.drop_column("file_job", "file_id", schema="app")

    # Rename integer temp column back to file_id.
    op.alter_column(
        "file_job",
        "file_id_int_tmp",
        new_column_name="file_id",
        existing_type=sa.Integer(),
        nullable=False,
        schema="app",
    )

    # Recreate old FK from file_job.file_id -> user_file.id.
    op.create_foreign_key(
        "file_job_file_id_fkey",
        "file_job",
        "user_file",
        ["file_id"],
        ["id"],
        source_schema="app",
        referent_schema="app",
        ondelete="CASCADE",
    )

    # Restore file_chunk.embedding nullable state.
    op.alter_column(
        "file_chunk",
        "embedding",
        existing_type=Vector(1536),
        nullable=True,
        schema="app",
    )