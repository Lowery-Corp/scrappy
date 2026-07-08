import uuid
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy import update, select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from models.user_filestore import UserFileStore
from models.user_file import UserFile
from schemas.file_job import FileJobCreate, FileJobUpdate
from repositories.minio import get_bucket_structure, upload_file_to_minio, delete_path_from_minio
from repositories.file_job import create_file_job, update_file_job
from repositories.task_queue import enqueue_file_ingestion_task


async def create_user_bucketstore(user_id: uuid.UUID, bucket_name: str, session: AsyncSession) -> dict[str, str | bool]:
    new_user_filestore = UserFileStore(user_id=user_id, bucket_name=bucket_name, bucket_structure={})
    session.add(new_user_filestore)
    await session.commit()
    return {"message": f"UserFilestore created for user ID {user_id}", "ok": True}


async def sync_user_bucketstore(
    user_id: uuid.UUID,
    session: AsyncSession,
) -> dict[str, str | bool]:

    new_bucket_structure = await get_bucket_structure(bucket_name=f"user-{user_id}-bucket")
    stmt = (
        update(UserFileStore)
        .where(UserFileStore.user_id == user_id)
        .values(bucket_structure=new_bucket_structure)
    )

    result = await session.execute(stmt)
    rowcount: int = int(result.rowcount) or 0

    assert rowcount > 0, f"No UserFileStore found for user ID {user_id}"

    await session.commit()
    return {"message": f"UserFileStore updated for user ID {user_id}", "ok": True}


async def get_user_bucketstore(user_id: uuid.UUID, session: AsyncSession) -> dict[str, Any]:
    result = await session.execute(
        select(UserFileStore).where(UserFileStore.user_id == user_id)
    )
    user_filestore: UserFileStore | None = result.scalar_one_or_none()

    bucket_structure: dict[str, Any] = user_filestore.bucket_structure if user_filestore else {} # type: ignore

    if user_filestore is None:
        return {"message": f"No UserFileStore found for user ID {user_id}"}

    user_files = await session.scalars(
        select(UserFile).where(
            UserFile.user_id == user_id,
            UserFile.status != "deleted",
        )
    )
    file_metadata = {
        f"/{user_file.storage_key.removeprefix('home/').lstrip('/')}": {
            "created_at": user_file.created_at.isoformat(),
            "updated_at": user_file.updated_at.isoformat(),
            "uploaded_at": user_file.uploaded_at.isoformat(),
            "status": user_file.status,
        }
        for user_file in user_files
    }

    return {"bucket_structure": bucket_structure, "file_metadata": file_metadata}


async def add_file_to_bucketstore(user_id: uuid.UUID, file_path: str, file: UploadFile, session: AsyncSession) -> dict[str, str | bool]:
    bucket_name: str = f"user-{user_id}-bucket"
    parsed_file_path: str = f"""{file_path.strip("/")}/{file.filename}"""
    storage_key: str = f"home/{parsed_file_path}".replace("//", "/").lower()

    upload_file = await upload_file_to_minio(
        bucket_name=bucket_name,
        file_path=storage_key,
        file_data=await file.read()
    )
    assert upload_file["ok"], f"File upload failed: {upload_file}"

    if not upload_file["ok"]:
        return {"message": f"Failed to upload file '{file_path}' to bucketstore for user ID {user_id}", "ok": False}

    storage_key = upload_file["uploaded_file"]["object_name"]

    result = await session.execute(
        select(UserFile).where(
            UserFile.user_id == user_id,
            UserFile.storage_key == storage_key,
        )
    )
    user_file: UserFile | None = result.scalar_one_or_none()

    if user_file is not None:
        return {
            "message": f"File '{file.filename}' already exists.",
            "ok": False,
        }
    else:
        file_name: str = str(file.filename).lower()
        mime_type: str | None = file.content_type if file.content_type else None

        insert_stmt = (
            insert(UserFile)
            .values(
                user_id=user_id,
                original_filename=file_name,
                storage_key=storage_key,
                mime_type=mime_type,
                file_size_bytes=file.size,
                status="uploaded",
            )
            .returning(UserFile)
        )

        user_file = (await session.execute(insert_stmt)).scalar_one()
        await session.commit()

    get_user_bucketstore_status = await get_user_bucketstore(user_id=user_id, session=session)
    if "message" in get_user_bucketstore_status and "No UserFileStore found" in get_user_bucketstore_status["message"]:
        create_user_bucketstore_status = await create_user_bucketstore(user_id=user_id, bucket_name=bucket_name, session=session)
        assert create_user_bucketstore_status["ok"], f"Failed to sync UserFileStore after file upload: {create_user_bucketstore_status}"

    sync_user_bucketstore_status = await sync_user_bucketstore(user_id=user_id, session=session)
    assert sync_user_bucketstore_status["ok"], f"Failed to sync UserFileStore after file upload: {sync_user_bucketstore_status}"

    new_file_job = FileJobCreate(
        file_id=user_file.file_id,
        job_type="ingest",
        max_attempts=3,
    )

    new_file_job = await create_file_job(
        user_id=str(user_id),
        file_job=new_file_job,
        session=session,
    )
    assert new_file_job is not None, f"Failed to create file job for file ID {user_file.file_id} and user ID {user_id}"

    newely_enqueued_task = None

    try:
        newely_enqueued_task = await enqueue_file_ingestion_task(
            file_id=user_file.file_id,
            storage_key=storage_key,
            user_id=uuid.UUID(user_id),
            file_job_id=new_file_job.job_id if new_file_job else None,
        )
    except Exception as exc:
        print(f"Failed to enqueue file ingestion task for file ID {user_file.file_id} and user ID {user_id}: {exc}", flush=True)

    if newely_enqueued_task is None:
        return {"message": f"Failed to enqueue file ingestion task for file ID {user_file.file_id} and user ID {user_id}", "ok": False}

    queued_at = datetime.now()
    updated_file_job = await update_file_job(
        user_id=user_id,
        job_id=new_file_job.job_id,
        file_job_update=FileJobUpdate(
            status="queued",
            queued_at=queued_at,
            queue_name=newely_enqueued_task.queue_name,
            started_at=queued_at,
            worker_id=newely_enqueued_task.celery_task_id,
        ),
        session=session,
    )
    if updated_file_job is None:
        return {"message": f"Failed to update file job status to 'queued' for file ID {user_file.file_id} and user ID {user_id}", "ok": False}

    # TODO: Return bucket structure with new file added
    return {
        "ok": True,
        "message": f"File '{storage_key}' added to UserFileStore for user ID {user_id}",
    }


async def download_file_from_bucketstore(user_id: str, file_path: str, session: AsyncSession) -> dict[str, Any]:
    print(f"Downloading file '{file_path}' for user ID {user_id} from bucketstore")

    return {"ok": True}


async def delete_file_from_bucketstore(user_id: str, file_path: str, session: AsyncSession) -> dict[str, Any]:
    print(f"Deleting file '{file_path}' for user ID {user_id} from bucketstore")

    storage_key = f"home/{file_path.strip('/')}".replace("//", "/")
    delete_file_from_minio_status = await delete_path_from_minio(
        bucket_name=f"user-{user_id}-bucket",
        path=storage_key,
    )
    assert delete_file_from_minio_status["ok"], f"Failed to delete file from MinIO: {delete_file_from_minio_status}"

    select_stmt = select(UserFile).where(UserFile.user_id == user_id, UserFile.storage_key == storage_key)
    result = await session.execute(select_stmt)
    user_file: UserFile | None = result.scalar_one_or_none()

    if user_file is None:
        return {"message": f"No UserFile found for user ID {user_id} and file path '{storage_key}'", "ok": False}

    stmt = delete(UserFile).where(UserFile.id == user_file.id)
    await session.execute(stmt)
    await session.commit()

    return {"ok": True}


async def delete_folder_from_bucketstore(user_id: str, file_path: str, session: AsyncSession, is_folder: bool = False) -> dict[str, Any]:
    print(f"Deleting folder '{file_path}' for user ID {user_id} from bucketstore")

    storage_key_prefix = f"home/{file_path.strip('/')}".replace("//", "/").lower()
    if is_folder and not storage_key_prefix.endswith("/"):
        storage_key_prefix += "/"

    delete_file_from_minio_status = await delete_path_from_minio(
        bucket_name=f"user-{user_id}-bucket",
        path=storage_key_prefix,
    )
    assert delete_file_from_minio_status["ok"], f"Failed to delete folder from MinIO: {delete_file_from_minio_status}"
    print(f"Deleted folder with storage key prefix '{storage_key_prefix}' from MinIO for user ID {user_id}", flush=True)

    stmt = update(UserFile).where(
        UserFile.user_id == user_id,
        UserFile.storage_key.startswith(storage_key_prefix)
    ).values(status="deleted")

    await session.execute(stmt)
    await session.commit()

    sync_user_bucketstore_status = await sync_user_bucketstore(user_id=user_id, session=session)
    assert sync_user_bucketstore_status["ok"], f"Failed to sync UserFileStore after folder deletion: {sync_user_bucketstore_status}"

    return {"ok": True}
