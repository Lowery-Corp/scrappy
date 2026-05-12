import uuid

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.user_file import UserFile
from schemas.user_file import UserFileCreate, UserFileRead, UserFileUpdate


async def create_user_file(
    user_file: UserFileCreate,
    session: AsyncSession,
) -> UserFile | None:
    create_values = user_file.model_dump(exclude_none=True)

    try:
        created_user_file = await session.scalar(
            insert(UserFile)
            .values(**create_values)
            .returning(UserFile)
        )
        await session.commit()
    except IntegrityError:
        await session.rollback()
        return None

    return created_user_file


async def list_user_files(
    session: AsyncSession,
    user_id: uuid.UUID | None = None,
    status: str | None = None,
    storage_key: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[UserFileRead]:
    stmt = select(UserFile)

    if user_id is not None:
        stmt = stmt.where(UserFile.user_id == user_id)
    if status is not None:
        stmt = stmt.where(UserFile.status == status)
    if storage_key is not None:
        stmt = stmt.where(UserFile.storage_key == storage_key)

    stmt = stmt.order_by(UserFile.created_at.desc()).limit(limit).offset(offset)

    result = await session.scalars(stmt)

    return [UserFileRead.model_validate(user_file) for user_file in result]


async def get_user_file(
    user_file_id: uuid.UUID,
    session: AsyncSession,
) -> UserFile | None:
    return await session.scalar(
        select(UserFile).where(UserFile.file_id == user_file_id)
    )


async def get_user_file_by_file_id(
    file_id: uuid.UUID,
    session: AsyncSession,
) -> UserFile | None:
    return await session.scalar(
        select(UserFile).where(UserFile.file_id == file_id)
    )


async def update_user_file(
    user_file_id: int,
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
    user_file_id: int,
    session: AsyncSession,
) -> bool:
    existing_user_file = await get_user_file(
        user_file_id=user_file_id,
        session=session,
    )

    if existing_user_file is None:
        return False

    await session.execute(delete(UserFile).where(UserFile.id == existing_user_file.id))
    await session.commit()

    return True
