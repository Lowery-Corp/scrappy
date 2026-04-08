from minio import Minio
from typing import Any

from core.config import settings


async def create_minio_client() -> Minio:
    minio_client = Minio(
        settings.minio_api_url,
        access_key=settings.minio_root_user,
        secret_key=settings.minio_root_password,
        secure=settings.minio_secure,
    )
    return minio_client


async def get_bucket_structure(bucket_name: str) -> dict[str, Any]:
    minio_client = await create_minio_client()

    objects = minio_client.list_objects(bucket_name, recursive=True)
    structure: dict[str, Any] = {}
    for obj in objects:
        if obj.object_name is not None:
            parts = obj.object_name.split('/')
            current_level = structure
            for part in parts[:-1]:  # Traverse directories
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]
            current_level[parts[-1]] = None  # Mark the file
        else:
            return {"error": "Object with no name found"}
    return structure


async def create_bucket(bucket_name: str) -> dict[str, Any]:
    minio_client = await create_minio_client()
    try:
        minio_client.make_bucket(bucket_name)
        return {"message": f"Bucket '{bucket_name}' created successfully."}
    except Exception as e:
        return {"error": str(e)}