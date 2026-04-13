from fastapi import UploadFile
from sqlalchemy import update, select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from models.user_filestore import UserFileStore
from models.user_file import UserFile
from repositories.minio import get_bucket_structure, upload_file_to_minio, delete_file_from_minio


async def create_user_bucketstore(user_id: int, bucket_name: str, session: AsyncSession) -> dict[str, str]:
    new_user_filestore = UserFileStore(user_id=user_id, bucket_name=bucket_name, bucket_structure={})
    session.add(new_user_filestore)
    await session.commit()
    return {"message": f"UserFilestore created for user ID {user_id}"}


async def sync_user_bucketstore(
    user_id: str,
    session: AsyncSession,
) -> dict[str, str]:

    new_bucket_structure = await get_bucket_structure(bucket_name=f"user-{user_id}-bucket")
    stmt = (
        update(UserFileStore)
        .where(UserFileStore.user_id == user_id)
        .values(bucket_structure=new_bucket_structure)
    )

    result = await session.execute(stmt)
    rowcount: int = int(result.rowcount or 0)

    assert rowcount > 0, f"No UserFileStore found for user ID {user_id}"

    await session.commit()
    return {"message": f"UserFileStore updated for user ID {user_id}"}


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

    if not file.filename:
        return {"message": "Missing filename", "ok": False}

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
        select(UserFile).where(UserFile.user_id == user_id, UserFile.storage_key == storage_key)
    )
    user_file: UserFile | None = result.scalar_one_or_none()

    if user_file is not None:
        if user_file.status == "deleted":
            stmt = update(UserFile).where(UserFile.id == user_file.id).values(status="uploaded")
            await session.execute(stmt)
            await session.commit()
            return {"message": f"File '{file.filename}' re-uploaded to UserFileStore for user ID {user_id}", "ok": True}
        else:
            return {"message": f"File '{file.filename}' already exists in UserFileStore for user ID {user_id}", "ok": False}
    else:
        file_name: str = file.filename.lower()
        mime_type: str | None = file.content_type if file.content_type else None
        insert_stmt = insert(UserFile).values(
            user_id=user_id,
            original_filename=file_name,
            storage_key=storage_key,
            mime_type=mime_type,
            file_size_bytes=file.size,
            status="uploaded",
        )

        await session.execute(insert_stmt)
        await session.commit()

    return {"message": f"File '{storage_key}' added to UserFileStore for user ID {user_id}", "ok": True}


async def download_file_from_bucketstore(user_id: str, file_path: str, session: AsyncSession) -> dict[str, Any]:
    print(f"Downloading file '{file_path}' for user ID {user_id} from bucketstore")

    return {"ok": True}


async def delete_file_from_bucketstore(user_id: str, file_path: str, session: AsyncSession) -> dict[str, Any]:
    print(f"Deleting file '{file_path}' for user ID {user_id} from bucketstore")

    storage_key = f"home/{file_path.strip('/')}".replace("//", "/")
    delete_file_from_minio_status = await delete_file_from_minio(
        bucket_name=f"user-{user_id}-bucket",
        file_path=storage_key,
    )
    assert delete_file_from_minio_status["ok"], f"Failed to delete file from MinIO: {delete_file_from_minio_status}"

    select_stmt = select(UserFile).where(UserFile.user_id == user_id, UserFile.storage_key == storage_key)
    result = await session.execute(select_stmt)
    user_file: UserFile | None = result.scalar_one_or_none()

    if user_file is None:
        return {"message": f"No UserFile found for user ID {user_id} and file path '{storage_key}'", "ok": False}

    stmt = update(UserFile).where(UserFile.id == user_file.id).values(status="deleted")
    await session.execute(stmt)
    await session.commit()

    return {"ok": True}
