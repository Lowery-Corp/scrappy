import uuid

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.user_file import UserFile
from schemas.user_file import UserFileCreate, UserFileRead, UserFileUpdate


async def create_user_file(
    new_user_file: UserFileCreate,
    session: AsyncSession,
) -> UserFile | None:
    stmt = insert(UserFile).values(**new_user_file.model_dump()).returning(UserFile)
    user_file = await session.scalar(stmt)
    await session.commit()
    return user_file


async def list_user_files(
    session: AsyncSession,
    user_id: uuid.UUID | None = None,
    status: str | None = None,
    storage_key: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[UserFile]:
    stmt = select(UserFile)

    if user_id is not None:
        stmt = stmt.where(UserFile.user_id == user_id)
    if status is not None:
        stmt = stmt.where(UserFile.status == status)
    if storage_key is not None:
        stmt = stmt.where(UserFile.storage_key == storage_key)

    stmt = stmt.order_by(UserFile.created_at.desc()).limit(limit).offset(offset)

    result = await session.scalars(stmt)

    return [user_file for user_file in result]


async def get_user_file(
    session: AsyncSession,
    file_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    storage_key: str | None = None,
) -> UserFile | None:
    stmt = select(UserFile)

    if not file_id and not user_id and not storage_key:
        raise ValueError("At least one of user_file_id, user_id, or storage_key must be provided.")

    if file_id is not None:
        stmt = stmt.where(UserFile.file_id == file_id)
    if user_id is not None:
        stmt = stmt.where(UserFile.user_id == user_id)
    if storage_key is not None:
        stmt = stmt.where(UserFile.storage_key == storage_key)

    return await session.scalar(stmt)


async def get_user_file_by_file_id(
    file_id: uuid.UUID,
    session: AsyncSession,
) -> UserFile | None:
    return await session.scalar(
        select(UserFile).where(UserFile.file_id == file_id)
    )


async def update_user_file(
    user_file_id: uuid.UUID,
    user_file_update: UserFileUpdate,
    session: AsyncSession,
) -> UserFile | None:
    existing_user_file = await get_user_file(
        user_file_id=user_file_id,
        session=session,
    )

    if existing_user_file is None:
        return None

    update_values = user_file_update.model_dump(exclude_unset=True)
    if not update_values:
        return existing_user_file

    try:
        updated_user_file = await session.scalar(
            update(UserFile)
            .where(UserFile.id == existing_user_file.id)
            .values(**update_values)
            .returning(UserFile)
        )
        await session.commit()
    except IntegrityError:
        await session.rollback()
        return None

    return updated_user_file


async def delete_user_file(
    session: AsyncSession,
    file_id: uuid.UUID | None = None,
    storage_key: str | None = None,
    user_id: uuid.UUID | None = None,
) -> None:
    existing_user_file = await get_user_file(
        file_id=file_id,
        storage_key=storage_key,
        session=session,
        user_id=user_id
    )

    if existing_user_file:
        stmt = delete(UserFile)
        if file_id:
            stmt = stmt.where(UserFile.file_id == file_id)
        if storage_key:
            stmt = stmt.where(UserFile.storage_key == storage_key)
        if user_id:
            stmt = stmt.where(UserFile.user_id == user_id)
        await session.execute(stmt)
        await session.commit()