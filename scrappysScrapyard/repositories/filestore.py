import uuid
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy import update, select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from models.user_filestore import UserFileStore
from models.user_file import UserFile
from schemas.file_job import FileJobCreate, FileJobUpdate
from schemas.user_file import UserFileCreate
from repositories.minio import create_bucket, get_bucket_structure, upload_file_to_minio, delete_path_from_minio
from repositories.file_job import create_file_job, update_file_job
from repositories.user_file import get_user_file, delete_user_file, create_user_file, list_user_files
from repositories.task_queue import enqueue_file_ingestion_task


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
        assert create_bucket_status["ok"], f"Failed to create bucket for user ID {user_id}: {create_bucket_status}"

        create_filestore_status = await create_user_bucketstore(
            user_id=user_id,
            bucket_name=bucket_name,
            session=session,
        )
        assert create_filestore_status["ok"], f"Failed to create UserFileStore for user ID {user_id}: {create_filestore_status}"

        # sync_filestore_status = await sync_user_bucketstore(user_id=user_id, session=session)
        # assert sync_filestore_status["ok"], f"Failed to sync UserFileStore for user ID {user_id}: {sync_filestore_status}"

        result = await session.execute(select(UserFileStore).where(UserFileStore.user_id == user_id))
        user_filestore = result.scalar_one()


    # bucket_structure = user_filestore.bucket_structure # type: ignore

    # user_files = await session.scalars(
    #     select(UserFile).where(
    #         UserFile.user_id == user_id,
    #         UserFile.status != "deleted",
    #     )
    # )

    # file_metadata: dict[str, dict[str, Any]] = {
    #     f"/{user_file.storage_key.removeprefix('home/').lstrip('/')}": {
    #         "created_at": user_file.created_at.isoformat(),
    #         "updated_at": user_file.updated_at.isoformat(),
    #         "uploaded_at": user_file.uploaded_at.isoformat(),
    #         "file_size_bytes": user_file.file_size_bytes,
    #         "status": user_file.status,
    #     }
    #     for user_file in user_files
    # }

    # return {"bucket_structure": bucket_structure, "file_metadata": file_metadata}
    return user_filestore


async def sync_user_bucketstore(user_id: uuid.UUID, session: AsyncSession) -> dict[str, str | bool]:
    user_bucket_store = await get_user_bucketstore(user_id=user_id, session=session)
    assert user_bucket_store is not None, f"No UserFileStore found for user ID {user_id}"

    new_bucket_structure = await get_bucket_structure(bucket_name=f"user-{user_id}-bucket")

    updated_user_bucketstore = await update_user_bucketstore(
        user_id=user_id,
        bucket_structure=new_bucket_structure,
        session=session,
    )
    assert updated_user_bucketstore is not None, f"Failed to update UserFileStore for user ID {user_id}"

    return {"message": f"UserFileStore updated for user ID {user_id}", "ok": True}


async def add_file_to_bucketstore(
    user_id: uuid.UUID,
    file_path: str,
    file: UploadFile,
    session: AsyncSession
) -> dict[str, str | bool]:
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

    user_file = await get_user_file(storage_key=storage_key, user_id=user_id, session=session)

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
        uploaded_at=datetime.now()
    )

    new_user_file = await create_user_file(new_user_file = new_user_file_data, session=session)
    assert new_user_file is not None, f"Failed to create UserFile for storage key '{storage_key}' and user ID {user_id}"

    sync_user_bucketstore_status = await sync_user_bucketstore(user_id=user_id, session=session)
    assert sync_user_bucketstore_status["ok"], f"Failed to sync UserFileStore after file upload: {sync_user_bucketstore_status}"

    new_file_job = FileJobCreate(
        file_id=new_user_file.file_id,
        job_type="ingest",
        max_attempts=3,
    )

    new_file_job = await create_file_job(user_id=user_id, file_job=new_file_job, session=session)
    assert new_file_job and new_file_job.job_id is not None, f"Failed to create file job for file ID {new_user_file.file_id} and user ID {user_id}"
    newely_enqueued_task = await enqueue_file_ingestion_task(file_job_ids=[new_file_job.job_id],)

    queued_at = datetime.now()
    updated_file_job = await update_file_job(
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


async def get_user_bucketstore_structure(user_id: uuid.UUID, session: AsyncSession) -> dict[str, Any]:
    user_bucketstore = await get_user_bucketstore(user_id=user_id, session=session)
    assert user_bucketstore is not None, f"No UserFileStore found for user ID {user_id}"
    bucket_structure = user_bucketstore.bucket_structure # type: ignore

    user_files = await list_user_files(user_id=user_id, session=session)

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
    print(f"Downloading file '{file_path}' for user ID {user_id} from bucketstore")

    return {"ok": True}


async def delete_file_from_bucketstore(user_id: uuid.UUID, file_path: str, session: AsyncSession) -> dict[str, Any]:
    storage_key = f"home/{file_path.strip('/')}".replace("//", "/")
    delete_file_from_minio_status = await delete_path_from_minio(
        bucket_name=f"user-{user_id}-bucket",
        path=storage_key,
    )
    assert delete_file_from_minio_status["ok"], f"Failed to delete file from MinIO: {delete_file_from_minio_status}"

    await delete_user_file(user_id=user_id, storage_key=storage_key, session=session)

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
