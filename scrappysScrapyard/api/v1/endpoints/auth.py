from fastapi import APIRouter, Depends, Response, Cookie, Request
from typing import Any

from schemas.user import UserLogin
from repositories.auth import login_user, get_user_from_token, blacklist_token
from schemas.user import AuthorizedUser, UserToken

router = APIRouter(tags=["auth"])


@router.post("/login")
async def login_route(
    UserLogin: UserLogin,
    response: Response,
) -> dict[str, str]:
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

    return {"message": "Successfully logged in"}

# TODO: Implement logout functionality (e.g., token blacklisting in auth service)
@router.post("/logout")
async def logout_route(response: Response, request: Request) -> dict[str, bool]:
    token = request.cookies.get("access_token")

    if token:
        # decode token, get jti, store in blacklist table/cache
        print("Token to blacklist:", token)
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
    print(f"Access token from cookie: {access_token}", flush=True)
    if not access_token:
        return {"message": "Needs to login first"}

    authorized_user = await get_user_from_token(token=access_token)

    if not authorized_user:
        return {"message": "Invalid or expired token"}

    return {
        "user": authorized_user
    }