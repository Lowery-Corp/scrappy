from schemas.user import AuthorizedUser
from core.config import settings
from httpx import AsyncClient

async def login_user(username: str, password: str) -> AuthorizedUser | bool:

    auth_endpoint: str = f"{settings.auth_api_url}/api/v1/auth/login"
    async with AsyncClient() as client:
        response = await client.post(
            auth_endpoint,
            json={"email": username, "password": password},
        )
        response.raise_for_status()
        data = response.json()

        authorized_user = AuthorizedUser(
            id=data.get("id", "fake-id"),
            username=data.get("username", "fake-username"),
            is_admin=False,
            token=data.get("token", "fake-token"),
        )

        return authorized_user
