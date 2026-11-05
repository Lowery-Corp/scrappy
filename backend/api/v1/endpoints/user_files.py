import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from cache.app_cache import CACHE_PREFIX, USER_CACHE_TTL_SECONDS, app_cache
from db.dependencies import get_session
from repositories.user_file import (
    get_user_files,
)
from schemas.user import AuthorizedUser
from schemas.user_file import ReadUserFiles

router = APIRouter(tags=["user_files"])

@router.get("", response_model=ReadUserFiles)
@router.get("/{file_id}", response_model=ReadUserFiles)
async def get_user_file(
    file_id: uuid.UUID | None = None,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    cache_suffix = "all" if file_id is None else str(file_id)
    cache_key = f"{CACHE_PREFIX}:user:{current_user.id}:files:{cache_suffix}"
    cached_files = await app_cache.get_json(cache_key)
    if cached_files is not None:
        cached_response = ReadUserFiles.model_validate(cached_files)
        if file_id is not None and not cached_response.files:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User file not found",
            )
        return cached_response

    user_files = await get_user_files(
        user_id=current_user.id,
        file_id=file_id,
        session=session
    )

    if file_id is not None and not user_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User file not found",
        )

    response = ReadUserFiles.model_validate({"files": user_files or []})
    await app_cache.set_json(
        cache_key,
        response.model_dump(mode="json"),
        USER_CACHE_TTL_SECONDS,
    )
    return response

