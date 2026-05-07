import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user, require_admin_user
from db.dependencies import get_session
from repositories.user_file import (
    create_user_file,
    delete_user_file,
    get_user_file,
    get_user_file_by_file_id,
    list_user_files,
    update_user_file,
)
from schemas.user import AuthorizedUser
from schemas.user_file import UserFileCreate, UserFileRead, UserFileUpdate

router = APIRouter(tags=["user_files"])


@router.post("", response_model=UserFileRead, status_code=status.HTTP_201_CREATED)
async def create_user_file_route(
    user_file: UserFileCreate,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserFileRead:
    require_admin_user(current_user)

    created_user_file = await create_user_file(
        user_file=user_file,
        session=session,
    )

    if created_user_file is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User file already exists or violates a database constraint",
        )

    return created_user_file


@router.get("", response_model=list[UserFileRead])
async def list_user_files_route(
    user_id: uuid.UUID | None = None,
    file_status: str | None = Query(default=None, alias="status"),
    storage_key: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[UserFileRead]:
    require_admin_user(current_user)

    user_files = await list_user_files(
        session=session,
        user_id=user_id,
        status=file_status,
        storage_key=storage_key,
        limit=limit,
        offset=offset,
    )

    return user_files


@router.get("/file-id/{file_id}", response_model=UserFileRead)
async def get_user_file_by_file_id_route(
    file_id: uuid.UUID,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserFileRead:
    require_admin_user(current_user)

    user_file = await get_user_file_by_file_id(
        file_id=file_id,
        session=session,
    )

    if user_file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User file not found",
        )

    return user_file


@router.get("/{user_file_id}", response_model=UserFileRead)
async def get_user_file_route(
    user_file_id: int,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserFileRead:
    require_admin_user(current_user)

    user_file = await get_user_file(
        user_file_id=user_file_id,
        session=session,
    )

    if user_file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User file not found",
        )

    return user_file


@router.patch("/{user_file_id}", response_model=UserFileRead)
async def update_user_file_route(
    user_file_id: int,
    user_file_update: UserFileUpdate,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserFileRead:
    require_admin_user(current_user)

    updated_user_file = await update_user_file(
        user_file_id=user_file_id,
        user_file_update=user_file_update,
        session=session,
    )

    if updated_user_file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User file not found or update violates a database constraint",
        )

    return updated_user_file


@router.delete("/{user_file_id}")
async def delete_user_file_route(
    user_file_id: int,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, bool]:
    require_admin_user(current_user)

    deleted = await delete_user_file(
        user_file_id=user_file_id,
        session=session,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User file not found",
        )

    return {"ok": True}
