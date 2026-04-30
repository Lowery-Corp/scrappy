from fastapi import UploadFile
from sqlalchemy import update, select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from models.user_filestore import UserFileStore
from models.user_file import UserFile
from repositories.minio import get_bucket_structure, upload_file_to_minio, delete_path_from_minio
from repositories.offload_task import offload_file_ingestion_task


async def create_user_bucketstore(user_id: int, bucket_name: str, session: AsyncSession) -> dict[str, str]:
    new_user_filestore = UserFileStore(user_id=user_id, bucket_name=bucket_name, bucket_structure={})
    session.add(new_user_filestore)
    await session.commit()
    return {"message": f"UserFilestore created for user ID {user_id}"}


async def sync_user_bucketstore(
    user_id: str,
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


async def get_user_bucketstore(user_id: str, session: AsyncSession) -> dict[str, Any]:
    result = await session.execute(
        select(UserFileStore).where(UserFileStore.user_id == user_id)
    )
    user_filestore: UserFileStore | None = result.scalar_one_or_none()

    bucket_structure: dict[str, Any] = user_filestore.bucket_structure if user_filestore else {} # type: ignore

    if user_filestore is None:
        return {"message": f"No UserFileStore found for user ID {user_id}"}

    return {"bucket_structure": bucket_structure}


async def add_file_to_bucketstore(user_id: str, file_path: str, file: UploadFile, session: AsyncSession) -> dict[str, str | bool]:
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


    offload_status = await offload_file_ingestion_task(user_id=user_id, user_file=user_file, session=session)
    assert offload_status["ok"], f"Failed to offload file ingestion task: {offload_status}"

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
