from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import AuthorizedUser

from auth.dependencies import get_current_user
from db.dependencies import get_session
from repositories.filestore import (
    sync_user_bucketstore,
    get_user_bucketstore_structure,
    add_file_to_bucketstore,
    create_folder_in_bucketstore,
    delete_file_from_bucketstore,
    delete_folder_from_bucketstore,
    rename_path_in_bucketstore,
)

router = APIRouter(tags=["blob"])


@router.get("")
async def fetch_bucket_structure(
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> dict[str, Any]:
    bucket_structure: dict[str, Any] = await get_user_bucketstore_structure(user_id=current_user.id, session=session)

    return bucket_structure


@router.post("/sync")
async def sync_bucket_structure(
    session: AsyncSession = Depends(get_session),
    current_user: AuthorizedUser = Depends(get_current_user)
) -> dict[str, Any]:

    await sync_user_bucketstore(user_id=current_user.id, session=session)

    return {"ok": True}


@router.post("/folder")
async def create_folder(
    folder_path: str,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    return await create_folder_in_bucketstore(
        user_id=current_user.id,
        folder_path=folder_path,
        session=session,
    )


@router.post("/rename")
async def rename_path(
    source_path: str,
    destination_path: str,
    is_folder: bool = False,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, Any]:
    return await rename_path_in_bucketstore(
        user_id=current_user.id,
        source_path=source_path,
        destination_path=destination_path,
        is_folder=is_folder,
        session=session,
    )


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

    insert_status = await add_file_to_bucketstore(
        user_id=current_user.id,
        file_path=file_path,
        file=file,
        session=session,
    )
    if not insert_status.get("ok"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=insert_status.get("message", "File upload failed"),
        )

    return {
        "ok": True,
    }


@router.delete("/delete")
async def delete_file(
    file_path: str,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> dict[str, Any]:
    await delete_file_from_bucketstore(
        user_id=current_user.id,
        file_path=file_path,
        session=session,
    )

    return {"ok": True}


@router.delete("/bulk-delete")
async def bulk_delete_files(
    folder_path: str,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> dict[str, Any]:
    await delete_folder_from_bucketstore(
        user_id=current_user.id,
        file_path=folder_path,
        session=session,
        is_folder=True,
    )

    return {"ok": True}
