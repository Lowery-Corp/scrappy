import uuid
from datetime import datetime
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.file_job import FileJob
from models.user_file import UserFile
from schemas.file_job import FileJobCreate, FileJobUpdate, FileJobRead

async def create_file_job(
    user_id: uuid.UUID,
    file_job: FileJobCreate,
    session: AsyncSession,
) -> FileJob | None:
    user_file = await session.scalar(
        select(UserFile).where(
            UserFile.file_id == file_job.file_id,
            UserFile.user_id == user_id,
        )
    )

    if user_file is None:
        return None

    created_file_job = await session.scalar(
        insert(FileJob)
        .values(
            file_id=file_job.file_id,
            job_type=file_job.job_type,
            max_attempts=file_job.max_attempts,
            queue_name=file_job.queue_name,
        )
        .returning(FileJob)
    )
    await session.commit()

    return created_file_job


async def list_file_jobs(
    session: AsyncSession,
    status: list[str] | None = None,
    job_type: str | None = None,
    created_at: float | None = None,
    limit: int = 50,
    offset: int = 0,
)-> list[str]:
    stmt = select(FileJob.job_id)

    if status:
        stmt = stmt.where(FileJob.status.in_(status))
    if job_type:
        stmt = stmt.where(FileJob.job_type == job_type)
    if created_at:
        created_at_dt = datetime.fromtimestamp(created_at)
        stmt = stmt.where(FileJob.created_at >= created_at_dt)
    stmt = stmt.where(FileJob.attempt_count < FileJob.max_attempts)
    stmt = stmt.order_by(FileJob.created_at.desc()).limit(limit).offset(offset)

    result = await session.execute(stmt)
    file_jobs = result.scalars().all()

    return [str(job_id) for job_id in file_jobs]


async def get_file_job(
    job_id: uuid.UUID,
    session: AsyncSession,
) -> FileJobRead | None:
    file_job = await session.scalar(
        select(FileJob).where(FileJob.job_id == job_id)
    )

    file_job_read = FileJobRead.model_validate(file_job) if file_job else None
    return file_job_read


async def update_file_job(
    job_id: uuid.UUID,
    file_job_update: FileJobUpdate,
    session: AsyncSession,
) -> FileJob:
    existing_file_job = await get_file_job(
        job_id=job_id,
        session=session,
    )

    if existing_file_job is None:
        raise ValueError(f"File job with ID {job_id} not found")

    update_values = file_job_update.model_dump(exclude_unset=True)
    if not update_values:
        raise ValueError("No fields to update provided")

    updated_file_job = await session.scalar(
        update(FileJob)
        .where(FileJob.file_id == existing_file_job.file_id)
        .values(**update_values)
        .returning(FileJob)
    )
    await session.commit()

    if not updated_file_job:
        raise ValueError(f"Failed to update file job with ID {job_id}")

    return updated_file_job


async def increment_attempt_count(
    job_id: uuid.UUID,
    session: AsyncSession,
) -> FileJob:
    existing_file_job = await get_file_job(
        job_id=job_id,
        session=session,
    )

    if existing_file_job is None:
        raise ValueError(f"File job with ID {job_id} not found")

    updated_file_job = await session.scalar(
        update(FileJob)
        .where(FileJob.file_id == existing_file_job.file_id)
        .values(attempt_count=existing_file_job.attempt_count + 1)
        .returning(FileJob)
    )
    await session.commit()

    if not updated_file_job:
        raise ValueError(f"Failed to increment attempt count for file job with ID {job_id}")

    return updated_file_job


async def delete_file_job(
    job_id: uuid.UUID,
    session: AsyncSession,
) -> bool:
    existing_file_job = await get_file_job(
        job_id=job_id,
        session=session,
    )

    if existing_file_job is None:
        return True

    await session.execute(delete(FileJob).where(FileJob.id == existing_file_job.id))
    await session.commit()

    return True
