from schemas.user import UserToken, AuthorizedUser
from core.config import settings
from httpx import AsyncClient

async def login_user(username: str, password: str) -> UserToken | bool:

    auth_endpoint: str = f"{settings.auth_api_url}/api/v1/auth/login"
    async with AsyncClient() as client:
        response = await client.post(
            auth_endpoint,
            json={"email": username, "password": password},
        )
        response.raise_for_status()
        data = response.json()

        user_token = UserToken(
            token=data.get("token", "fake-token"),
        )

        return user_token


async def get_user_from_token(token: str) -> AuthorizedUser | None:
    auth_endpoint: str = f"{settings.auth_api_url}/api/v1/auth/me"
    async with AsyncClient() as client:
        response = await client.get(
            auth_endpoint,
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code == 401:
            return None

        response.raise_for_status()
        data = response.json()

        authorized_user = AuthorizedUser(
            id=str(data.get("id", "fake-id")),
            username=data.get("username", "fake-username"),
            email=data.get("email", "fake-email@gmail.com"),
            is_admin=False,
        )

        return authorized_user


async def blacklist_token(token: str) -> bool:
    auth_endpoint: str = f"{settings.auth_api_url}/api/v1/auth/logout"
    async with AsyncClient() as client:
        response = await client.post(
            auth_endpoint,
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code == 200:
            return True
        return False