from repositories.minio import create_bucket
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.filestore import create_user_bucketstore
from schemas.user import UserLogin, LoginResponse
from repositories.auth import login_user, get_user_from_token


async def login(user_login: UserLogin) -> dict[str, str | LoginResponse]:
    user_token: str = await login_user(user_login.username, user_login.password)
    assert user_token, "Token should not be None or empty"

    authorized_user = await get_user_from_token(user_token)
    assert authorized_user is not None, "Authorized user should not be None"

    user_response = LoginResponse(username=authorized_user.username)
    assert user_response.username, "Username should not be None or empty"

    return {"token": user_token, "user": user_response}


async def create_user_resources(user_id: int, session: AsyncSession) -> dict[str, str]:
    # Example: Create a MinIO bucket for the user
    bucket_name = f"user-{user_id}-bucket"
    user_bucket_created = await create_bucket(bucket_name)
    assert user_bucket_created.get("ok") is True, f"Failed to create bucket for user ID {user_id}: {user_bucket_created.get('error', 'Unknown error')}"

    filestore_status = await create_user_bucketstore(
        user_id=user_id,
        bucket_name=bucket_name,
        session=session,
    )
    assert filestore_status.get("ok") is True, f"Failed to create UserFilestore for user ID {user_id}"

    # Simulate bucket creation for this example
    print(f"Creating bucket '{bucket_name}' for user ID {user_id}")

    return {"message": f"Resources created for user ID {user_id}"}

