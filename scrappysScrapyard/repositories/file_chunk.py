from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.file_chunk import FileChunk
from schemas.file_chunk import FileChunkCreate, FileChunkRead, FileChunkUpdate


async def create_file_chunk(
    file_chunk: FileChunkCreate,
    session: AsyncSession,
) -> FileChunk | None:
    create_values = file_chunk.model_dump(exclude_none=True)

    try:
        created_file_chunk = await session.scalar(
            insert(FileChunk)
            .values(**create_values)
            .returning(FileChunk)
        )
        await session.commit()
    except IntegrityError:
        await session.rollback()
        return None

    return created_file_chunk


async def list_file_chunks(
    session: AsyncSession,
    file_id: int | None = None,
    embedding_status: str | None = None,
    chunk_index: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[FileChunkRead]:
    stmt = select(FileChunk)

    if file_id is not None:
        stmt = stmt.where(FileChunk.file_id == file_id)
    if embedding_status is not None:
        stmt = stmt.where(FileChunk.embedding_status == embedding_status)
    if chunk_index is not None:
        stmt = stmt.where(FileChunk.chunk_index == chunk_index)

    stmt = stmt.order_by(FileChunk.id.desc()).limit(limit).offset(offset)

    result = await session.scalars(stmt)

    return [FileChunkRead.model_validate(file_chunk) for file_chunk in result]


async def get_file_chunk(
    file_chunk_id: int,
    session: AsyncSession,
) -> FileChunk | None:
    return await session.scalar(
        select(FileChunk).where(FileChunk.id == file_chunk_id)
    )


async def update_file_chunk(
    file_chunk_id: int,
    file_chunk_update: FileChunkUpdate,
    session: AsyncSession,
) -> FileChunk | None:
    existing_file_chunk = await get_file_chunk(
        file_chunk_id=file_chunk_id,
        session=session,
    )

    if existing_file_chunk is None:
        return None

    update_values = file_chunk_update.model_dump(exclude_unset=True)
    if not update_values:
        return existing_file_chunk

    try:
        updated_file_chunk = await session.scalar(
            update(FileChunk)
            .where(FileChunk.id == existing_file_chunk.id)
            .values(**update_values)
            .returning(FileChunk)
        )
        await session.commit()
    except IntegrityError:
        await session.rollback()
        return None

    return updated_file_chunk


async def delete_file_chunk(
    file_chunk_id: int,
    session: AsyncSession,
) -> bool:
    existing_file_chunk = await get_file_chunk(
        file_chunk_id=file_chunk_id,
        session=session,
    )

    if existing_file_chunk is None:
        return False

    await session.execute(delete(FileChunk).where(FileChunk.id == existing_file_chunk.id))
    await session.commit()

    return True
