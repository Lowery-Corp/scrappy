from fastapi import APIRouter, Depends
from typing import Any

from schemas.user import UserLogin
from repositories.auth import login_user
from schemas.user import AuthorizedUser

router = APIRouter(tags=["auth"])


@router.post("/login")
async def login_route(
    UserLogin: UserLogin,
) -> AuthorizedUser| dict[str, str]:
    logged_in_user: AuthorizedUser | bool = await login_user(
        UserLogin.email,
        UserLogin.password,
    )
    if type(logged_in_user) is bool:
        if logged_in_user is False:
            return {"message": "Invalid email or password"}
        elif logged_in_user is True:
            return {"message": "There was an error logging in"}

    return logged_in_user

# TODO: this route should check to see if the token is still
# valid by calling the auth service.
@router.get("/check-auth")
async def token_check_route(token: str) -> dict[str, Any]:
    return {"status": True}


# TODO: Implement logout functionality (e.g., token blacklisting in auth service)
@router.post("/logout")
async def logout_route() -> dict[str, str]:
    return {"message": "Successfully logged out"}
