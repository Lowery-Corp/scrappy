from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import AuthorizedUser

from auth.dependencies import get_current_user
from db.dependencies import get_session
from repositories.filestore import (
    sync_user_bucketstore,
    get_user_bucketstore,
    add_file_to_bucketstore,
    delete_file_from_bucketstore,
    delete_folder_from_bucketstore,
)

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


@router.post("/upload")
async def upload_file(
    file_path: str,
    file: UploadFile = File(...),
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> dict[str, Any]:

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing filename",
        )

    insert_status = await add_file_to_bucketstore(user_id=current_user.id, file_path=file_path, file=file, session=session) # type: ignore
    assert insert_status["ok"] == True, f"Failed to add file to bucketstore: {insert_status}"

    return {
        "ok": True,
    }


@router.delete("/delete")
async def delete_file(
    file_path: str,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> dict[str, Any]:
    delete_status = await delete_file_from_bucketstore(user_id=current_user.id, file_path=file_path, session=session)
    assert delete_status["ok"] == True, f"Failed to delete file from bucketstore: {delete_status}"

    return {"ok": True}


@router.delete("/bulk-delete")
async def bulk_delete_files(
    folder_path: str,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> dict[str, Any]:
    delete_status = await delete_folder_from_bucketstore(user_id=current_user.id, file_path=folder_path, session=session, is_folder=True)
    assert delete_status["ok"] == True, f"Failed to bulk delete files from bucketstore: {delete_status}"

    return {"ok": True}