import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import require_admin_user
from cache.app_cache import ADMIN_CACHE_TTL_SECONDS, CACHE_PREFIX, app_cache
from db.dependencies import get_session
from repositories.user_file import (
    get_user_files,
    update_user_file,
    delete_user_file,
)
from schemas.user_file import UserFileRead, UserFileUpdate, ReadUserFiles

router = APIRouter(tags=["data_files"])

@router.get("", response_model=ReadUserFiles, dependencies=[Depends(require_admin_user)])
@router.get("/{file_id}", response_model=ReadUserFiles, dependencies=[Depends(require_admin_user)])
@router.get("/user/{user_id}", response_model=ReadUserFiles, dependencies=[Depends(require_admin_user)])
async def get_file_route(
    user_id: uuid.UUID | None = None,
    file_id: uuid.UUID | None= None,
    session: AsyncSession = Depends(get_session),
) -> ReadUserFiles:
    cache_key = (
        f"{CACHE_PREFIX}:admin:data-files:"
        f"user:{user_id or 'all'}:file:{file_id or 'all'}"
    )
    cached_files = await app_cache.get_json(cache_key)
    if cached_files is not None:
        return ReadUserFiles.model_validate(cached_files)

    files = await get_user_files(
        file_id=file_id,
        user_id=user_id,
        session=session,
    )

    if files is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User file not found",
        )

    response = ReadUserFiles.model_validate({"files": files})
    await app_cache.set_json(cache_key, response.model_dump(mode="json"), ADMIN_CACHE_TTL_SECONDS)
    return response


@router.patch("/{file_id}", response_model=UserFileRead, dependencies=[Depends(require_admin_user)])
async def update_file_route(
    file_id: uuid.UUID,
    file_update: UserFileUpdate,
    session: AsyncSession = Depends(get_session),
) -> UserFileRead:

    updated_file = await update_user_file(
        file_id=file_id,
        file_update=file_update,
        session=session,
    )

    if updated_file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User file not found or update violates a database constraint",
        )

    await app_cache.invalidate_admin()
    return_user_file = UserFileRead.model_validate(updated_file)

    return return_user_file


@router.delete("/{file_id}", dependencies=[Depends(require_admin_user)])
async def delete_file_route(
    file_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict[str, bool]:

    deleted = await delete_user_file(
        file_id=file_id,
        session=session,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User file not found",
        )

    await app_cache.invalidate_admin()
    return {"ok": True}
