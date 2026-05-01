import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from db.dependencies import get_session
from repositories.file_job import (
    create_file_job,
    delete_file_job,
    get_file_job,
    list_file_jobs,
    update_file_job,
)
from schemas.file_job import FileJobCreate, FileJobRead, FileJobUpdate
from schemas.user import AuthorizedUser

router = APIRouter(tags=["file_jobs"])


@router.post("", response_model=FileJobRead, status_code=status.HTTP_201_CREATED)
async def create_file_job_route(
    file_job: FileJobCreate,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> FileJobRead:
    created_file_job = await create_file_job(
        user_id=current_user.id,
        file_job=file_job,
        session=session,
    )

    if created_file_job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    return created_file_job


@router.get("", response_model=list[FileJobRead])
async def list_file_jobs_route(
    file_id: int | None = None,
    job_status: str | None = Query(default=None, alias="status"),
    job_type: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[FileJobRead]:
    return await list_file_jobs(
        user_id=current_user.id,
        session=session,
        file_id=file_id,
        status=job_status,
        job_type=job_type,
        limit=limit,
        offset=offset,
    )


@router.get("/{job_id}", response_model=FileJobRead)
async def get_file_job_route(
    job_id: uuid.UUID,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> FileJobRead:
    file_job = await get_file_job(
        user_id=current_user.id,
        job_id=job_id,
        session=session,
    )

    if file_job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File job not found",
        )

    return file_job


@router.patch("/{job_id}", response_model=FileJobRead)
async def update_file_job_route(
    job_id: uuid.UUID,
    file_job_update: FileJobUpdate,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> FileJobRead:
    updated_file_job = await update_file_job(
        user_id=current_user.id,
        job_id=job_id,
        file_job_update=file_job_update,
        session=session,
    )

    if updated_file_job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File job not found",
        )

    return updated_file_job


@router.delete("/{job_id}")
async def delete_file_job_route(
    job_id: uuid.UUID,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, bool]:
    deleted = await delete_file_job(
        user_id=current_user.id,
        job_id=job_id,
        session=session,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File job not found",
        )

    return {"ok": True}

