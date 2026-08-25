import uuid

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models.user_file import UserFile
from schemas.user_file import UserFileCreate, UserFileUpdate


async def create_user_file(
    new_user_file: UserFileCreate,
    session: AsyncSession,
) -> UserFile | None:
    stmt = insert(UserFile).values(**new_user_file.model_dump()).returning(UserFile)
    user_file = await session.scalar(stmt)
    await session.commit()
    return user_file


async def get_user_files(
    session: AsyncSession,
    file_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    status: str | None = None,
    storage_key: str | None = None,
) -> list[UserFile] | None:
    stmt = select(UserFile)

    if not file_id and not user_id and not storage_key:
        raise ValueError("At least one of user_file_id, user_id, or storage_key must be provided.")

    if file_id is not None:
        stmt = stmt.where(UserFile.file_id == file_id)
    if user_id is not None:
        stmt = stmt.where(UserFile.user_id == user_id)
    if storage_key is not None:
        stmt = stmt.where(UserFile.storage_key == storage_key)
    if status is not None:
        stmt = stmt.where(UserFile.status == status)

    results = await session.scalars(stmt)

    file_data = [user_file for user_file in results.all()]
    print(file_data, flush=True)

    return file_data


async def update_user_file(
    file_id: uuid.UUID,
    file_update: UserFileUpdate,
    session: AsyncSession,
) -> UserFile | None:
    existing_user_file = await get_user_files(
        file_id=file_id,
        session=session,
    )
    existing_user_file = existing_user_file[0] if existing_user_file else None

    if existing_user_file is None:
        return None

    update_values = file_update.model_dump(exclude_unset=True)
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
    existing_user_file = await get_user_files(
        file_id=file_id,
        storage_key=storage_key,
        session=session,
        user_id=user_id
    )
    existing_user_file = existing_user_file[0] if existing_user_file else None

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