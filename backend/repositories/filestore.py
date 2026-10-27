import uuid
from datetime import datetime, timezone
from fastapi import UploadFile
from pathlib import PurePosixPath
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from models.user_filestore import UserFileStore
from models.user_file import UserFile
from schemas.file_job import FileJobCreate, FileJobUpdate
from schemas.user_file import UserFileCreate
from repositories.minio import (
    create_bucket,
    create_folder_in_minio,
    delete_path_from_minio,
    get_bucket_structure,
    rename_path_in_minio,
    upload_file_to_minio,
)
from repositories.file_job import create_file_job, update_file_job
from repositories.user_file import get_user_files, delete_user_file, create_user_file
from repositories.task_queue import TaskQueueError, enqueue_file_ingestion_task
from core.config import settings
from core.errors import StorageOperationError


async def create_user_bucketstore(user_id: uuid.UUID, bucket_name: str, session: AsyncSession) -> dict[str, str | bool]:
    existing_filestore = await session.scalar(
        select(UserFileStore).where(UserFileStore.user_id == user_id)
    )
    if existing_filestore is not None:
        return {"message": f"UserFilestore already exists for user ID {user_id}", "ok": True}

    new_user_filestore = UserFileStore(user_id=user_id, bucket_name=bucket_name, bucket_structure={})
    session.add(new_user_filestore)
    await session.commit()
    return {"message": f"UserFilestore created for user ID {user_id}", "ok": True}


async def update_user_bucketstore(user_id: uuid.UUID, bucket_structure: dict[str, Any], session: AsyncSession) -> UserFileStore | None:
    result = await session.execute(
        update(UserFileStore)
        .where(UserFileStore.user_id == user_id)
        .values(bucket_structure=bucket_structure)
        .returning(UserFileStore)
    )
    await session.commit()
    return result.scalar_one_or_none()


async def get_user_bucketstore(user_id: uuid.UUID, session: AsyncSession) -> UserFileStore:
    result = await session.execute(
        select(UserFileStore).where(UserFileStore.user_id == user_id)
    )
    user_filestore: UserFileStore | None = result.scalar_one_or_none()

    if user_filestore is None:
        bucket_name = f"user-{user_id}-bucket"
        create_bucket_status = await create_bucket(bucket_name)
        if not create_bucket_status.get("ok"):
            raise StorageOperationError(f"Failed to create bucket for user ID {user_id}")

        create_filestore_status = await create_user_bucketstore(
            user_id=user_id,
            bucket_name=bucket_name,
            session=session,
        )
        if not create_filestore_status.get("ok"):
            raise StorageOperationError(f"Failed to create UserFileStore for user ID {user_id}")

        result = await session.execute(select(UserFileStore).where(UserFileStore.user_id == user_id))
        user_filestore = result.scalar_one()

    return user_filestore


async def sync_user_bucketstore(user_id: uuid.UUID, session: AsyncSession) -> dict[str, str | bool]:
    user_bucket_store = await get_user_bucketstore(user_id=user_id, session=session)
    if user_bucket_store is None:
        raise StorageOperationError(f"No UserFileStore found for user ID {user_id}")

    new_bucket_structure = await get_bucket_structure(bucket_name=f"user-{user_id}-bucket")

    updated_user_bucketstore = await update_user_bucketstore(
        user_id=user_id,
        bucket_structure=new_bucket_structure,
        session=session,
    )
    if updated_user_bucketstore is None:
        raise StorageOperationError(f"Failed to update UserFileStore for user ID {user_id}")

    return {"message": f"UserFileStore updated for user ID {user_id}", "ok": True}


async def create_folder_in_bucketstore(
    user_id: uuid.UUID,
    folder_path: str,
    session: AsyncSession,
) -> dict[str, str | bool]:
    user_bucketstore = await get_user_bucketstore(user_id=user_id, session=session)
    storage_path = f"home/{folder_path.strip('/')}"
    result = await create_folder_in_minio(
        bucket_name=user_bucketstore.bucket_name,
        folder_path=storage_path,
    )
    if not result.get("ok"):
        raise StorageOperationError("Failed to create folder in object storage")

    await sync_user_bucketstore(user_id=user_id, session=session)
    return {"ok": True, "message": "Folder created"}


async def rename_path_in_bucketstore(
    user_id: uuid.UUID,
    source_path: str,
    destination_path: str,
    session: AsyncSession,
    is_folder: bool = False,
) -> dict[str, str | bool]:
    result = await rename_path_in_minio(
        bucket_name=f"user-{user_id}-bucket",
        source_path=f"home/{source_path.strip('/')}",
        destination_path=f"home/{destination_path.strip('/')}",
        is_folder=is_folder,
    )
    if not result.get("ok"):
        raise StorageOperationError("Failed to rename object in storage")

    if is_folder:
        source_prefix = f"home/{source_path.strip('/')}/"
        destination_prefix = f"home/{destination_path.strip('/')}/"
        await session.execute(
            update(UserFile)
            .where(
                UserFile.user_id == user_id,
                UserFile.storage_key.startswith(source_prefix),
            )
            .values(
                storage_key=func.replace(
                    UserFile.storage_key,
                    source_prefix,
                    destination_prefix,
                ),
            )
        )
    else:
        source_key = f"home/{source_path.strip('/')}"
        destination_key = f"home/{destination_path.strip('/')}"
        await session.execute(
            update(UserFile)
            .where(UserFile.user_id == user_id, UserFile.storage_key == source_key)
            .values(storage_key=destination_key)
        )
    await session.commit()
    await sync_user_bucketstore(user_id=user_id, session=session)
    return {"ok": True, "message": "Path renamed"}


async def add_file_to_bucketstore(
    user_id: uuid.UUID,
    file_path: str,
    file: UploadFile,
    session: AsyncSession
) -> dict[str, str | bool]:
    user_bucketstore = await get_user_bucketstore(user_id=user_id, session=session)
    bucket_name = user_bucketstore.bucket_name
    if not file.filename:
        return {"message": "Missing filename", "ok": False}
    if file.size is None:
        return {"message": "Unable to determine upload size", "ok": False}
    if file.size > settings.max_upload_size_bytes:
        return {
            "message": f"File exceeds the {settings.max_upload_size_bytes} byte upload limit",
            "ok": False,
        }

    raw_path_parts = file_path.replace("\\", "/").split("/")
    if any(part == ".." for part in raw_path_parts):
        return {"message": "Invalid file path", "ok": False}

    safe_path = PurePosixPath(*[part for part in raw_path_parts if part not in ("", ".")])
    safe_filename = PurePosixPath(file.filename.replace("\\", "/")).name
    if safe_filename in ("", ".", ".."):
        return {"message": "Invalid filename", "ok": False}

    parsed_file_path: str = f"{safe_path}/{safe_filename}" if str(safe_path) != "." else safe_filename
    storage_key: str = f"home/{parsed_file_path}".replace("//", "/").lower()

    await file.seek(0)
    upload_file = await upload_file_to_minio(
        bucket_name=bucket_name,
        file_path=storage_key,
        file_data=file.file,
        content_length=file.size,
    )
    if not upload_file["ok"]:
        return {"message": f"Failed to upload file '{file_path}' to bucketstore for user ID {user_id}", "ok": False}

    storage_key = upload_file["uploaded_file"]["object_name"]

    new_user_file = None
    try:
        user_files = await get_user_files(storage_key=storage_key, user_id=user_id, session=session)
        user_file = user_files[0] if user_files else None

        if user_file:
            await delete_user_file(file_id=user_file.file_id, session=session)

        file_name: str = str(file.filename).lower().strip()
        mime_type: str | None = file.content_type if file.content_type else None

        new_user_file_data: UserFileCreate = UserFileCreate(
            user_id=user_id,
            original_filename=file_name,
            storage_key=storage_key,
            mime_type=mime_type,
            file_size_bytes=file.size,
            status="uploaded",
            uploaded_at=datetime.now(timezone.utc),
        )

        new_user_file = await create_user_file(new_user_file=new_user_file_data, session=session)
        if new_user_file is None:
            raise RuntimeError(f"Failed to create UserFile for storage key '{storage_key}' and user ID {user_id}")

        sync_user_bucketstore_status = await sync_user_bucketstore(user_id=user_id, session=session)
        if not sync_user_bucketstore_status.get("ok"):
            raise RuntimeError(f"Failed to sync UserFileStore after file upload: {sync_user_bucketstore_status}")

        file_job = FileJobCreate(
            file_id=new_user_file.file_id,
            job_type="ingest",
            max_attempts=3,
        )

        new_file_job = await create_file_job(user_id=user_id, file_job=file_job, session=session)
        if new_file_job is None or new_file_job.job_id is None:
            raise RuntimeError(f"Failed to create file job for file ID {new_user_file.file_id} and user ID {user_id}")

        try:
            queued_task = await enqueue_file_ingestion_task(file_job_ids=[new_file_job.job_id])
        except TaskQueueError as exc:
            await update_file_job(
                job_id=new_file_job.job_id,
                file_job_update=FileJobUpdate(
                    status="pending",
                    error_message=f"Ingestion queue unavailable: {exc}",
                ),
                session=session,
            )
            return {
                "ok": True,
                "message": f"File '{storage_key}' uploaded; ingestion is pending queue availability",
            }

        queued_at = datetime.now(timezone.utc)
        await update_file_job(
            job_id=new_file_job.job_id,
            file_job_update=FileJobUpdate(
                status="queued",
                queued_at=queued_at,
                queue_name=queued_task.queue_name,
                started_at=queued_at,
                worker_id=queued_task.celery_task_id,
            ),
            session=session,
        )
    except Exception:
        await delete_path_from_minio(bucket_name=bucket_name, path=storage_key)
        if new_user_file is not None:
            await delete_user_file(file_id=new_user_file.file_id, session=session)
        raise

    return {
        "ok": True,
        "message": f"File '{storage_key}' added to UserFileStore for user ID {user_id}",
    }


async def get_user_bucketstore_structure(user_id: uuid.UUID, session: AsyncSession) -> dict[str, Any]:
    user_bucketstore = await get_user_bucketstore(user_id=user_id, session=session)
    if user_bucketstore is None:
        raise StorageOperationError(f"No UserFileStore found for user ID {user_id}")
    bucket_structure = user_bucketstore.bucket_structure # type: ignore

    user_files = await get_user_files(user_id=user_id, session=session)
    if user_files is None:
        return {"bucket_structure": bucket_structure, "file_metadata": {}}

    file_metadata: dict[str, dict[str, Any]] = {
        f"/{user_file.storage_key.removeprefix('home/').lstrip('/')}": {
            "created_at": user_file.created_at.isoformat(),
            "updated_at": user_file.updated_at.isoformat(),
            "uploaded_at": user_file.uploaded_at.isoformat(),
            "file_size_bytes": user_file.file_size_bytes,
            "status": user_file.status,
        }
        for user_file in user_files
    }

    return {"bucket_structure": bucket_structure, "file_metadata": file_metadata}


async def download_file_from_bucketstore(user_id: str, file_path: str, session: AsyncSession) -> dict[str, Any]:
    return {"ok": True}


async def delete_file_from_bucketstore(user_id: uuid.UUID, file_path: str, session: AsyncSession) -> dict[str, Any]:
    storage_key = f"home/{file_path.strip('/')}".replace("//", "/")
    delete_file_from_minio_status = await delete_path_from_minio(
        bucket_name=f"user-{user_id}-bucket",
        path=storage_key,
    )
    if not delete_file_from_minio_status.get("ok"):
        raise StorageOperationError("Failed to delete file from object storage")

    await delete_user_file(user_id=user_id, storage_key=storage_key, session=session)

    return {"ok": True}


async def delete_folder_from_bucketstore(user_id: str, file_path: str, session: AsyncSession, is_folder: bool = False) -> dict[str, Any]:
    storage_key_prefix = f"home/{file_path.strip('/')}".replace("//", "/").lower()
    if is_folder and not storage_key_prefix.endswith("/"):
        storage_key_prefix += "/"

    delete_file_from_minio_status = await delete_path_from_minio(
        bucket_name=f"user-{user_id}-bucket",
        path=storage_key_prefix,
    )
    if not delete_file_from_minio_status.get("ok"):
        raise StorageOperationError("Failed to delete folder from object storage")

    stmt = update(UserFile).where(
        UserFile.user_id == user_id,
        UserFile.storage_key.startswith(storage_key_prefix)
    ).values(status="deleted")

    await session.execute(stmt)
    await session.commit()

    sync_user_bucketstore_status = await sync_user_bucketstore(user_id=user_id, session=session)
    if not sync_user_bucketstore_status.get("ok"):
        raise StorageOperationError("Failed to sync UserFileStore after folder deletion")

    return {"ok": True}
