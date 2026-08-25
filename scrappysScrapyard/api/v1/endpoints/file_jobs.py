import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user, require_admin_user
from db.dependencies import get_session
from repositories.file_job import (
    create_file_job,
    get_file_job,
    list_file_jobs,
    increment_attempt_count,
    update_file_job,
    delete_file_job,
)
from schemas.file_job import FileJobCreate, FileJobRead, FileJobUpdate, FileJobListRead
from schemas.user import AuthorizedUser

router = APIRouter(tags=["jobs"])

@router.post("", response_model=FileJobRead, status_code=status.HTTP_201_CREATED)
async def create_file_job_route(
    file_job: FileJobCreate,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> FileJobRead:
    require_admin_user(current_user)

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


@router.get("/list", dependencies=[Depends(require_admin_user)])
async def list_file_jobs_route(
    params: FileJobListRead = Query(),
    session: AsyncSession = Depends(get_session),
) -> list[str]:
    file_jobs = await list_file_jobs(
        session=session,
        status=params.status,
        job_type=params.job_type,
        created_at=params.created_at,
        limit=params.limit,
        offset=params.offset,
    )

    return file_jobs


@router.get("/{job_id}", response_model=FileJobRead, dependencies=[Depends(require_admin_user)])
async def get_file_job_route(
    job_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> FileJobRead:

    file_job = await get_file_job(
        job_id=job_id,
        session=session,
    )

    if file_job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File job not found",
        )

    return file_job


@router.patch("/{job_id}", response_model=FileJobRead, dependencies=[Depends(require_admin_user)])
async def update_file_job_route(
    job_id: uuid.UUID,
    file_job_update: FileJobUpdate,
    session: AsyncSession = Depends(get_session),
) -> FileJobRead:

    updated_file_job = await update_file_job(
        job_id=job_id,
        file_job_update=file_job_update,
        session=session,
    )
    if not updated_file_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File job not found or update violates a database constraint",
        )

    updated_file_job_read = FileJobRead.model_validate(updated_file_job)

    return updated_file_job_read


@router.patch("/{job_id}/increment_attempts", response_model=FileJobRead, dependencies=[Depends(require_admin_user)])
async def increment_attempt_count_route(
    job_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> FileJobRead:
    updated_file_job = await increment_attempt_count(
        job_id=job_id,
        session=session,
    )
    if not updated_file_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File job not found",
        )

    updated_file_job_read = FileJobRead.model_validate(updated_file_job)

    return updated_file_job_read


# @router.delete("/{job_id}", response_model=dict[str, bool], dependencies=[Depends(require_admin_user)])
# async def delete_file_job_route(
#     job_id: uuid.UUID,
#     session: AsyncSession = Depends(get_session),
# ) -> dict[str, bool]:

#     deleted = await delete_file_job(
#         job_id=job_id,
#         session=session,
#     )

#     if not deleted:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="File job not found",
#         )

#     return {"ok": True}
