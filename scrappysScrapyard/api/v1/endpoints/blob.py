from fastapi import APIRouter, Depends
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import AuthorizedUser

from auth.dependencies import get_current_user
from db.dependencies import get_session
from repositories.filestore import sync_user_bucketstore, get_user_bucketstore
# from repositories.minio import get_bucket_structure

router = APIRouter(tags=["blob"])



@router.get("")
async def fetch_bucket_structure(
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> dict[str, Any]:
    bucket_structure: dict[str, Any] = await get_user_bucketstore(user_id=current_user.id, session=session)

    return bucket_structure


@router.post("/sync")
async def sync_bucket_structiure(
    session: AsyncSession = Depends(get_session),
    current_user: AuthorizedUser = Depends(get_current_user)
) -> dict[str, Any]:

    await sync_user_bucketstore(user_id=current_user.id, session=session)

    return {"ok": True}


