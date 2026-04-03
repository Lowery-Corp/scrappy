from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from models.user import User
from schemas.user import UserLogin
from core.security import create_access_token
from auth.dependencies import get_current_active_user, blacklist_current_token
from db.dependencies import get_session
from repositories.user import login_user

router = APIRouter(tags=["auth"])

@router.get("/login")
async def login_route(
    UserLogin: UserLogin,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    logged_in_user = await login_user(
        session,
        UserLogin.email,
        UserLogin.password,
    )
    if not logged_in_user:
        return {"message": "Invalid email or password"}

    user_token = create_access_token(subject=str(logged_in_user.id))

    return {"token": user_token}


@router.get("/token-check")
async def token_check_route(
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    return {
        "message": f"Token is valid for user {current_user.email}",
        "status": True,
    }


@router.post("/logout")
async def logout_route(
    revoked: bool = Depends(blacklist_current_token),
) -> dict[str, str]:
    return {"message": "Successfully logged out"}


@router.get("/is-admin")
async def is_admin_route(
    current_user: User = Depends(get_current_active_user),
) -> dict[str, bool]:
    return {"is_admin": current_user.is_admin}
