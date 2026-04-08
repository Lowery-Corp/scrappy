from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from models.user_filestore import UserFileStore
from repositories.minio import get_bucket_structure


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
