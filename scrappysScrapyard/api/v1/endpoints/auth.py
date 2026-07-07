import uuid

from fastapi import APIRouter, Response, Request, Depends, Cookie
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_session
from schemas.user import UserLogin, UserCreate
from repositories.auth import (
    login_user,
    blacklist_token,
    register_user
)
from repositories.user import create_user_resources
from schemas.user import AuthorizedUser, UserToken
from repositories.auth import get_user_from_token

router = APIRouter(tags=["auth"])

@router.post("/login")
async def login_route(
    UserLogin: UserLogin,
    response: Response,
) -> dict[str, str | bool]:
    user_token: UserToken | bool = await login_user(
        UserLogin.email,
        UserLogin.password,
    )
    if type(user_token) is bool:
        if user_token is False:
            return {"message": "Invalid email or password"}
        elif user_token is True:
            return {"message": "There was an error logging in"}

    response.set_cookie(
        key="access_token",
        value=user_token.token,
        httponly=True,
        secure=True,      # True in production over HTTPS
        samesite="lax",    # often fine for same-site frontend/backend
        max_age=60 * 60,
        expires=60 * 60,
        path="/",
    )

    return {
        "message": "Successfully logged in",
        "ok": True
    }


@router.post("/logout")
async def logout_route(response: Response, request: Request) -> dict[str, bool]:
    token = request.cookies.get("access_token")

    if token:
        # decode token, get jti, store in blacklist table/cache
        blacklist_status = await blacklist_token(token)
        print("Blacklist status:", blacklist_status)

        response.delete_cookie(
            key="access_token",
            path="/",
        )
        return {"ok": True}
    return {"ok": False}


@router.get("/me")
async def get_current_user_route(
    access_token: str | None = Cookie(default=None)
) -> dict[str, AuthorizedUser | str]:
    if not access_token:
        return {"message": "Needs to login first"}

    authorized_user = await get_user_from_token(token=access_token)

    if not authorized_user:
        return {"message": "Invalid or expired token"}

    return {
        "user": authorized_user,
    }


@router.post("/register")
async def register_route(
    new_user: UserCreate,
    session: AsyncSession = Depends(get_session),
) -> dict[str, bool | str]:
    user_created = await register_user(
        email=new_user.email,
        password=new_user.password,
    )

    if user_created.get("ok") is not True:
        return {"ok": False, "message": user_created.get("error", "User creation failed")}

    try:
        user_id = uuid.UUID(str(user_created["user_id"]))
        await create_user_resources(user_id=user_id, session=session)
    except Exception as e:
        print(f"Error creating user resources: {e}")
        return {"ok": False, "message": "User created but user resources were not created"}

    return {"ok": True, "message": "User created successfully"}

