import uuid

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
