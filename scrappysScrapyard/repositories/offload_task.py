from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from models.user_file import UserFile
from models.file_job import FileJob


async def offload_file_ingestion_task(
    user_id: str,
    user_file: UserFile,
    session: AsyncSession,
) -> dict[str, str | bool]:
    file_metadata: dict[str, str] = {
        "file_id": str(user_file.id),
        "storage_key": user_file.storage_key,
    }

    print(file_metadata, flush=True)

    file_job_id = await session.scalar(
        insert(FileJob).values(
            file_id=user_file.file_id,
            job_type="ingest",
        ).returning(FileJob.id)
    )
    await session.commit()

    print(f"Created new FileJob with ID {file_job_id} for file ID {user_file.id}", flush=True)

    ret: dict[str, str | bool] = {
        "ok": True,
        "message": "File ingestion task offloaded successfully.",
    }

    return ret
