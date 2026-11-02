from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from auth.dependencies import require_admin_user
from cache.app_cache import ADMIN_CACHE_TTL_SECONDS, CACHE_PREFIX, app_cache
from db.dependencies import get_session
from repositories.file_chunk import (
    create_file_chunk,
    delete_file_chunk,
    get_file_chunks,
    list_file_chunks,
    update_file_chunk,
)
from schemas.file_chunk import FileChunkCreate, FileChunkRead, FileChunkUpdate

router = APIRouter(tags=["file_chunks"])


@router.post("", response_model=FileChunkRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin_user)])
async def create_file_chunk_route(
    file_chunk: FileChunkCreate,
    session: AsyncSession = Depends(get_session),
) -> FileChunkRead:

    created_file_chunk = await create_file_chunk(
        file_chunk=file_chunk,
        session=session,
    )

    if created_file_chunk is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="File chunk already exists or violates a database constraint",
        )

    await app_cache.invalidate_admin()
    return created_file_chunk


@router.get("", response_model=list[FileChunkRead], dependencies=[Depends(require_admin_user)])
async def list_file_chunks_route(
    file_id: uuid.UUID | None = None,
    embedding_status: str | None = Query(default=None, alias="status"),
    chunk_index: int | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> list[FileChunkRead]:
    cache_key = (
        f"{CACHE_PREFIX}:admin:file-chunks:list:file:{file_id or 'all'}:"
        f"status:{embedding_status or 'all'}:"
        f"index:{chunk_index if chunk_index is not None else 'all'}:"
        f"limit:{limit}:offset:{offset}"
    )
    cached_chunks = await app_cache.get_json(cache_key)
    if cached_chunks is not None:
        return [FileChunkRead.model_validate(chunk) for chunk in cached_chunks]

    file_chunks = await list_file_chunks(
        session=session,
        file_id=file_id,
        embedding_status=embedding_status,
        chunk_index=chunk_index,
        limit=limit,
        offset=offset,
    )

    await app_cache.set_json(
        cache_key,
        [chunk.model_dump(mode="json") for chunk in file_chunks],
        ADMIN_CACHE_TTL_SECONDS,
    )
    return file_chunks


@router.get("/{file_chunk_id}", response_model=FileChunkRead, dependencies=[Depends(require_admin_user)])
@router.get("/{file_id}/{file_chunk_id}", response_model=FileChunkRead, dependencies=[Depends(require_admin_user)])
async def get_file_chunk_route(
    file_chunk_id: int,
    file_id: uuid.UUID | None = None,
    session: AsyncSession = Depends(get_session),
) -> FileChunkRead:
    cache_key = f"{CACHE_PREFIX}:admin:file-chunk:{file_id or 'all'}:{file_chunk_id}"
    cached_chunk = await app_cache.get_json(cache_key)
    if cached_chunk is not None:
        return FileChunkRead.model_validate(cached_chunk)

    file_chunk = await get_file_chunks(
        file_chunk_id=file_chunk_id,
        file_id=file_id,
        session=session,
    )

    if not file_chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File chunk not found",
        )

    response = file_chunk[0]
    await app_cache.set_json(cache_key, response.model_dump(mode="json"), ADMIN_CACHE_TTL_SECONDS)
    return response


@router.patch("/{file_chunk_id}", response_model=FileChunkRead, dependencies=[Depends(require_admin_user)])
async def update_file_chunk_route(
    file_chunk_id: int,
    file_chunk_update: FileChunkUpdate,
    session: AsyncSession = Depends(get_session),
) -> FileChunkRead:

    updated_file_chunk = await update_file_chunk(
        file_chunk_id=file_chunk_id,
        file_chunk_update=file_chunk_update,
        session=session,
    )

    if updated_file_chunk is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File chunk not found or update violates a database constraint",
        )

    await app_cache.invalidate_admin()
    return updated_file_chunk


@router.delete("/{file_id}", dependencies=[Depends(require_admin_user)])
@router.delete("/{file_id}/{file_chunk_id}", dependencies=[Depends(require_admin_user)])
async def delete_file_chunk_route(
    file_id: uuid.UUID | None = None,
    file_chunk_id: int | None = None,
    session: AsyncSession = Depends(get_session),
) -> dict[str, bool]:

    deleted = await delete_file_chunk(
        file_id=file_id,
        file_chunk_id=file_chunk_id,
        session=session,
    )

    if deleted:
        await app_cache.invalidate_admin()
    return {"ok": deleted}
