import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import require_admin_user
<<<<<<< HEAD:scrappysScrapyard/api/v1/endpoints/data_files.py
=======
from cache.app_cache import ADMIN_CACHE_TTL_SECONDS, CACHE_PREFIX, app_cache
>>>>>>> ebdfb1dfaa5fc5a8d958258ef2a71bb15e1fc440:backend/api/v1/endpoints/data_files.py
from db.dependencies import get_session
from repositories.user_file import (
    get_user_files,
    update_user_file,
    delete_user_file,
)
from schemas.user_file import UserFileRead, UserFileUpdate, ReadUserFiles

router = APIRouter(tags=["data_files"])

<<<<<<< HEAD:scrappysScrapyard/api/v1/endpoints/data_files.py
@router.get("", response_model=list[ReadUserFiles], dependencies=[Depends(require_admin_user)])
=======
@router.get("", response_model=ReadUserFiles, dependencies=[Depends(require_admin_user)])
>>>>>>> ebdfb1dfaa5fc5a8d958258ef2a71bb15e1fc440:backend/api/v1/endpoints/data_files.py
@router.get("/{file_id}", response_model=ReadUserFiles, dependencies=[Depends(require_admin_user)])
@router.get("/user/{user_id}", response_model=ReadUserFiles, dependencies=[Depends(require_admin_user)])
async def get_file_route(
    user_id: uuid.UUID | None = None,
    file_id: uuid.UUID | None= None,
    session: AsyncSession = Depends(get_session),
) -> ReadUserFiles:
<<<<<<< HEAD:scrappysScrapyard/api/v1/endpoints/data_files.py
=======
    cache_key = (
        f"{CACHE_PREFIX}:admin:data-files:"
        f"user:{user_id or 'all'}:file:{file_id or 'all'}"
    )
    cached_files = await app_cache.get_json(cache_key)
    if cached_files is not None:
        return ReadUserFiles.model_validate(cached_files)
>>>>>>> ebdfb1dfaa5fc5a8d958258ef2a71bb15e1fc440:backend/api/v1/endpoints/data_files.py

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

<<<<<<< HEAD:scrappysScrapyard/api/v1/endpoints/data_files.py
    return_files: ReadUserFiles = ReadUserFiles(files=[])
    if files:
        return_files.files = files

    return return_files
=======
    response = ReadUserFiles.model_validate({"files": files})
    await app_cache.set_json(cache_key, response.model_dump(mode="json"), ADMIN_CACHE_TTL_SECONDS)
    return response
>>>>>>> ebdfb1dfaa5fc5a8d958258ef2a71bb15e1fc440:backend/api/v1/endpoints/data_files.py


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

<<<<<<< HEAD:scrappysScrapyard/api/v1/endpoints/data_files.py
=======
    await app_cache.invalidate_admin()
>>>>>>> ebdfb1dfaa5fc5a8d958258ef2a71bb15e1fc440:backend/api/v1/endpoints/data_files.py
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

<<<<<<< HEAD:scrappysScrapyard/api/v1/endpoints/data_files.py
=======
    await app_cache.invalidate_admin()
>>>>>>> ebdfb1dfaa5fc5a8d958258ef2a71bb15e1fc440:backend/api/v1/endpoints/data_files.py
    return {"ok": True}
