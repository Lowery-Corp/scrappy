import uuid
import logging
from fastapi import APIRouter, Response, Request, Depends
from httpx import HTTPStatusError, RequestError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from db.dependencies import get_session
from schemas.user import UserLogin, UserCreate, AuthorizedUser, LoginResponse
from repositories.auth import (
    blacklist_token,
    register_user
)
from repositories.user import create_user_resources, login
from auth.dependencies import get_current_user
from core.errors import ResourceProvisioningError

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])

@router.post("/login")
async def login_route(
    UserLogin: UserLogin,
    response: Response,
) -> LoginResponse | dict[str, str | bool]:
    try:
        login_data = await login(UserLogin)

        response.set_cookie(
            key=settings.cookie_key,
            value=str(login_data.get("token")),
            httponly=True,
            secure=settings.cookie_secure,
            samesite="lax",    # often fine for same-site frontend/backend
            max_age=60 * 60,
            expires=60 * 60,
            path="/",
        )

        user_data = login_data.get("user")
        if not isinstance(user_data, LoginResponse):
            raise ValueError("Invalid user data type")
        user: LoginResponse = user_data

        return user
    except (HTTPStatusError, ValueError) as exc:
        logger.warning("Login rejected: %s", exc)
        response.status_code = 401
        return {"ok": False, "message": "Invalid username or password"}
    except RequestError as exc:
        logger.exception("Authentication service request failed", exc_info=exc)
        response.status_code = 502
        return {"ok": False, "message": "Authentication service unavailable"}
    except Exception:
        logger.exception("Unexpected login failure")
        response.status_code = 500
        return {"ok": False, "message": "Login failed"}


@router.get("/me")
async def read_me_route(
    current_user: AuthorizedUser = Depends(get_current_user),
) -> dict[str, str | bool | list[str]]:
    permissions = ["read:admin"] if current_user.is_admin else []
    return {
        "username": current_user.username,
        "is_admin": current_user.is_admin,
        "permissions": permissions,
    }


@router.post("/logout")
async def logout_route(response: Response, request: Request) -> dict[str, bool]:
    token = request.cookies.get(settings.cookie_key)

    if token:
        # decode token, get jti, store in blacklist table/cache
        blacklist_status = await blacklist_token(token)
        logger.info("Token blacklist request completed: %s", blacklist_status)

        response.delete_cookie(key=settings.cookie_key, path="/")
        return {"ok": True}
    return {"ok": False}


@router.post("/register")
async def register_route(
    new_user: UserCreate,
    response: Response,
    session: AsyncSession = Depends(get_session),
) -> dict[str, bool | str]:
    try:
        user_created = await register_user(
            email=new_user.username,
            password=new_user.password,
        )
    except (HTTPStatusError, RequestError) as exc:
        logger.exception("Authentication service registration failed", exc_info=exc)
        response.status_code = 502
        return {"ok": False, "message": "Authentication service unavailable"}

    if user_created.get("ok") is not True:
        response.status_code = 409
        return {"ok": False, "message": user_created.get("error", "User creation failed")}

    try:
        user_id = uuid.UUID(str(user_created["user_id"]))
        await create_user_resources(user_id=user_id, session=session)
    except ResourceProvisioningError:
        logger.exception("Failed to create user resources")
        response.status_code = 502
        return {"ok": False, "message": "User created but user resources were not created"}

    return {"ok": True, "message": "User created successfully"}

