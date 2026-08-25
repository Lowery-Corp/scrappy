import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from db.dependencies import get_session
from repositories.user_file import (
    get_user_files,
)
from schemas.user import AuthorizedUser
from schemas.user_file import ReadUserFiles

router = APIRouter(tags=["user_files"])

@router.get("", response_model=ReadUserFiles)
@router.get("/{file_id}", response_model=ReadUserFiles)
async def get_user_file(
    file_id: uuid.UUID | None = None,
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    user_files = await get_user_files(
        user_id=current_user.id,
        file_id=file_id,
        session=session
    )

    if not user_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User file not found",
        )

    return_files: ReadUserFiles = ReadUserFiles(files=[])
    if user_files:
        return_files.files = user_files

    return return_files

