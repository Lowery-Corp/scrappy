import logging
import uuid

from repositories.minio import create_bucket
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.filestore import create_user_bucketstore
from schemas.user import UserLogin, LoginResponse
from repositories.auth import login_user, get_user_from_token
from core.errors import ResourceProvisioningError

logger = logging.getLogger(__name__)


async def login(user_login: UserLogin) -> dict[str, str | LoginResponse]:
    user_token: str = await login_user(user_login.username, user_login.password)
    if not user_token:
        raise ValueError("Authentication service returned an empty token")

    authorized_user = await get_user_from_token(user_token)
    if authorized_user is None:
        raise ValueError("Authentication service returned no user")

    permissions = ["read:admin"] if authorized_user.is_admin else []
    user_response = LoginResponse(
        username=authorized_user.username,
        is_admin=authorized_user.is_admin,
        permissions=permissions,
    )
    if not user_response.username:
        raise ValueError("Authentication service returned an empty username")

    return {"token": user_token, "user": user_response}


async def create_user_resources(user_id: uuid.UUID, session: AsyncSession) -> dict[str, str]:
    # Example: Create a MinIO bucket for the user
    bucket_name = f"user-{user_id}-bucket"
    user_bucket_created = await create_bucket(bucket_name)
    if user_bucket_created.get("ok") is not True:
        raise ResourceProvisioningError(f"Failed to create bucket for user ID {user_id}")

    filestore_status = await create_user_bucketstore(
        user_id=user_id,
        bucket_name=bucket_name,
        session=session,
    )
    if filestore_status.get("ok") is not True:
        raise ResourceProvisioningError(f"Failed to create UserFilestore for user ID {user_id}")

    logger.info("Created file-store resources for user %s", user_id)

    return {"message": f"Resources created for user ID {user_id}"}

