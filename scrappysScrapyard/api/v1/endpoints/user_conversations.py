from fastapi import APIRouter, Depends
from typing import Any
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import AuthorizedUser

from auth.dependencies import get_current_user
from db.dependencies import get_session
from repositories.user_conversation import (
    select_user_conversations,
    insert_user_conversation,
)

router = APIRouter(tags=["conversations"])


@router.get("")
async def fetch_user_conversation(
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> dict[str, Any]:
    user_conversations = await select_user_conversations(
        user_id=uuid.UUID(current_user.id),
        session=session,
    )

    print(user_conversations)

    return {"ok": True, "data": user_conversations}


@router.post("")
async def create_user_conversation(
    session: AsyncSession = Depends(get_session),
    current_user: AuthorizedUser = Depends(get_current_user)
) -> dict[str, Any]:
    new_conversation = await insert_user_conversation(
        user_id=uuid.UUID(current_user.id),
        session=session,
    )
    print(new_conversation)
    return {"ok": True}


@router.delete("/delete")
async def delete_user_conversation(
    current_user: AuthorizedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> dict[str, Any]:

    return {"ok": True}
