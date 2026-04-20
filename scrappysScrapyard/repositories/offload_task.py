from core.config import settings
from httpxC.http_client import http_client
from models.user_file import UserFile
from repositories.auth import internal_api_login


async def offload_file_injestion_task(user_id: str, user_file: UserFile) -> dict[str, str | bool]:
    print(f"Offloading file ingestion task for user ID {user_id} to Celery")
    print(f"UserFile details: ID={user_file.id}, storage_key='{user_file.storage_key}', status='{user_file.status}'", flush=True)


    settings.internal_cookie = await internal_api_login()
    if not settings.internal_cookie:
        return {"message": "Failed to authenticate with internal API", "ok": False}

    http_client.cookies.set("access_token", settings.internal_cookie)
    offload_endpoint = f"{settings.offload_api_url}/api/v1/ingest-file"
    job_creation_status = await http_client.post(
        offload_endpoint,
        json={
            "user_id": user_id,
            "file_id": user_file.id,
            "storage_key": user_file.storage_key,
        },
    )
    assert job_creation_status.status_code == 200, f"Failed to create offload job: {job_creation_status.text}"


    return {"message": f"File ingestion task for user ID {user_id} offloaded to Celery", "ok": True}
