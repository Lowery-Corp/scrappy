import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user, require_admin_user
from cache.app_cache import ADMIN_CACHE_TTL_SECONDS, CACHE_PREFIX, app_cache
from db.dependencies import get_session
from repositories.file_job import (
    create_file_job,
    get_file_job,
    list_file_jobs,
    increment_attempt_count,
    update_file_job,
)
from schemas.file_job import FileJobCreate, FileJobRead, FileJobUpdate, FileJobListRead
from schemas.user import AuthorizedUser

router = APIRouter(tags=["jobs"])

@router.post("", response_model=FileJobRead, status_code=status.HTTP_201_CREATED)
async def create_file_job_route(
    file_job: FileJobCreate,
    current_user: AuthorizedUser = Depends(require_admin_user),
    session: AsyncSession = Depends(get_session),
) -> FileJobRead:
    created_file_job = await create_file_job(
        user_id=None,
        file_job=file_job,
        session=session,
    )

    if created_file_job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    await app_cache.invalidate_admin()
    return created_file_job


@router.get("/list", dependencies=[Depends(require_admin_user)])
async def list_file_jobs_route(
    params: FileJobListRead = Query(),
    session: AsyncSession = Depends(get_session),
) -> list[str]:
    cache_key = (
        f"{CACHE_PREFIX}:admin:file-jobs:list:"
        f"status:{','.join(params.status or ())}:type:{params.job_type or 'all'}:"
        f"created:{params.created_at if params.created_at is not None else 'all'}:"
        f"limit:{params.limit}:offset:{params.offset}"
    )
    cached_jobs = await app_cache.get_json(cache_key)
    if cached_jobs is not None:
        return [str(job_id) for job_id in cached_jobs]

    file_jobs = await list_file_jobs(
        session=session,
        status=params.status,
        job_type=params.job_type,
        created_at=params.created_at,
        limit=params.limit,
        offset=params.offset,
    )

    await app_cache.set_json(cache_key, file_jobs, ADMIN_CACHE_TTL_SECONDS)
    return file_jobs


@router.get("/{job_id}", response_model=FileJobRead, dependencies=[Depends(require_admin_user)])
async def get_file_job_route(
    job_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> FileJobRead:
    cache_key = f"{CACHE_PREFIX}:admin:file-job:{job_id}"
    cached_job = await app_cache.get_json(cache_key)
    if cached_job is not None:
        return FileJobRead.model_validate(cached_job)

    file_job = await get_file_job(
        job_id=job_id,
        session=session,
    )

    if file_job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File job not found",
        )

    await app_cache.set_json(cache_key, file_job.model_dump(mode="json"), ADMIN_CACHE_TTL_SECONDS)
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

    await app_cache.invalidate_admin()
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

    await app_cache.invalidate_admin()
    updated_file_job_read = FileJobRead.model_validate(updated_file_job)

    return updated_file_job_read
