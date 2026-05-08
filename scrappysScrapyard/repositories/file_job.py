import uuid

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.file_job import FileJob
from models.user_file import UserFile
from schemas.file_job import FileJobCreate, FileJobUpdate, FileJobRead


def _user_scoped_file_job_query(user_id: str | None = None):
    stmt = select(FileJob).join(UserFile, FileJob.file_id == UserFile.file_id)

    if user_id:
        stmt = stmt.where(UserFile.user_id == user_id)

    return stmt


async def create_file_job(
    user_id: str,
    file_job: FileJobCreate,
    session: AsyncSession,
) -> FileJob | None:
    user_file = await session.scalar(
        select(UserFile).where(
            UserFile.id == file_job.file_id,
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
    user_id: str | None = None,
    file_id: uuid.UUID | None = None,
    status: str | None = None,
    job_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[FileJobRead]:
    stmt = _user_scoped_file_job_query(user_id)

    if file_id is not None:
        stmt = stmt.where(FileJob.file_id == file_id)
    if status is not None:
        stmt = stmt.where(FileJob.status == status)
    if job_type is not None:
        stmt = stmt.where(FileJob.job_type == job_type)

    stmt = stmt.order_by(FileJob.created_at.desc()).limit(limit).offset(offset)

    result = await session.scalars(stmt)

    file_job_reads = [FileJobRead.model_validate(file_job) for file_job in result]

    return file_job_reads


async def get_file_job(
    user_id: str,
    job_id: uuid.UUID,
    session: AsyncSession,
) -> FileJob | None:
    return await session.scalar(
        _user_scoped_file_job_query(user_id).where(FileJob.job_id == job_id)
    )


async def update_file_job(
    user_id: str,
    job_id: uuid.UUID,
    file_job_update: FileJobUpdate,
    session: AsyncSession,
) -> FileJob | None:
    existing_file_job = await get_file_job(
        user_id=user_id,
        job_id=job_id,
        session=session,
    )

    if existing_file_job is None:
        return None

    update_values = file_job_update.model_dump(exclude_unset=True)
    if not update_values:
        return existing_file_job

    updated_file_job = await session.scalar(
        update(FileJob)
        .where(FileJob.id == existing_file_job.id)
        .values(**update_values)
        .returning(FileJob)
    )
    await session.commit()

    return updated_file_job


async def delete_file_job(
    user_id: str,
    job_id: uuid.UUID,
    session: AsyncSession,
) -> bool:
    existing_file_job = await get_file_job(
        user_id=user_id,
        job_id=job_id,
        session=session,
    )

    if existing_file_job is None:
        return False

    await session.execute(delete(FileJob).where(FileJob.id == existing_file_job.id))
    await session.commit()

    return True
