from core.config import settings
from httpxC.http_client import http_client
from models.user_file import UserFile
from repositories.auth import login_user
from schemas.user import UserToken


async def offload_file_injestion_task(user_id: str, user_file: UserFile) -> dict[str, str | bool]:
    print(f"Offloading file ingestion task for user ID {user_id} to Celery")
    print(f"UserFile details: ID={user_file.id}, storage_key='{user_file.storage_key}', status='{user_file.status}'", flush=True)

    file_metadata: dict[str, str] = {
        "user_id": user_id,
        "file_id": str(user_file.id),
        "storage_key": user_file.storage_key,
    }
    print(f"File metadata: {file_metadata}", flush=True)

    user_token: UserToken | bool = await login_user(
        settings.internal_api_username,
        settings.internal_api_password,
    )

    if type(user_token) is bool:
        if user_token is False:
            return {"message": "Invalid email or password"}
        elif user_token is True:
            return {"message": "There was an error logging in"}

    settings.internal_cookie = user_token.token
    headers: dict[str, str] = {
        "Authorization": f"Bearer {settings.internal_cookie}"
    }

    offload_endpoint = f"{settings.offload_api_url}/api/v1/ingestion/file"
    job_creation_status = await http_client.post(
        offload_endpoint,
        headers=headers,
        json=file_metadata,
    )
    assert job_creation_status.status_code == 200, f"Failed to create offload job: {job_creation_status.text}"


    return {"message": f"File ingestion task for user ID {user_id} offloaded to Celery", "ok": True}
