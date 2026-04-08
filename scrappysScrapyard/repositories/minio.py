from functools import lru_cache
from minio import Minio
from typing import Any

from core.config import settings


@lru_cache
def get_minio_client() -> Minio:
    return Minio(
        settings.minio_api_url,
        access_key=settings.minio_root_user,
        secret_key=settings.minio_root_password,
        secure=settings.minio_secure,
    )

async def get_bucket_structure(bucket_name: str) -> dict[str, Any]:
    minio_client = get_minio_client()

    objects = minio_client.list_objects(bucket_name, recursive=True)
    structure: dict[str, Any] = {}

    for obj in objects:
        if not obj.object_name:
            continue

        parts = obj.object_name.split("/")
        current_level = structure

        for part in parts[:-1]:
            current_level = current_level.setdefault(part, {})

        current_level[parts[-1]] = None

    return structure


async def create_bucket(bucket_name: str) -> dict[str, Any]:
    minio_client = get_minio_client()
    try:
        minio_client.make_bucket(bucket_name)
        return {"message": f"Bucket '{bucket_name}' created successfully.", "ok": True}
    except Exception as e:
        return {"error": str(e)}