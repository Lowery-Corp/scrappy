from functools import lru_cache
import asyncio
from io import BytesIO
from minio import Minio
from minio.commonconfig import CopySource
from minio.deleteobjects import DeleteObject
from typing import Any, BinaryIO

from core.config import settings


def _normalize_path(path: str) -> str:
    normalized = path.replace("\\", "/").strip("/")
    parts = [part for part in normalized.split("/") if part not in ("", ".")]
    if any(part == ".." for part in parts):
        raise ValueError("Invalid storage path")
    return "/".join(parts)


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

    objects = await asyncio.to_thread(
        lambda: list(minio_client.list_objects(bucket_name, recursive=True))
    )
    structure: dict[str, Any] = {}

    for obj in objects:
        if not obj.object_name:
            continue

        parts = obj.object_name.split("/")
        current_level = structure

        for part in parts[:-1]:
            current_level = current_level.setdefault(part, {})

        current_level[parts[-1]] = None

    return structure["home"] if "home" in structure else structure


async def create_bucket(bucket_name: str) -> dict[str, Any]:
    minio_client = get_minio_client()
    try:
        if await asyncio.to_thread(minio_client.bucket_exists, bucket_name):
            return {"message": f"Bucket '{bucket_name}' already exists.", "ok": True}

        await asyncio.to_thread(minio_client.make_bucket, bucket_name)
        return {"message": f"Bucket '{bucket_name}' created successfully.", "ok": True}
    except Exception as e:
        return {"error": str(e), "ok": False}


async def upload_file_to_minio(
    bucket_name: str,
    file_path: str,
    file_data: BinaryIO,
    content_length: int,
) -> dict[str, Any]:
    minio_client = get_minio_client()

    try:
        uploaded_file = await asyncio.to_thread(
            minio_client.put_object,
            bucket_name,
            file_path,
            file_data,
            length=content_length,
        )

        return {
            "uploaded_file": {
                "object_name": uploaded_file.object_name,
                "etag": uploaded_file.etag,
            },
            "message": f"File '{file_path}' uploaded successfully to bucket '{bucket_name}'.",
            "ok": True,
        }
    except Exception as e:
        return {"error": str(e), "ok": False}


async def create_folder_in_minio(bucket_name: str, folder_path: str) -> dict[str, Any]:
    minio_client = get_minio_client()
    try:
        normalized_path = _normalize_path(folder_path)
        if not normalized_path:
            raise ValueError("Folder path cannot be empty")
        object_name = f"{normalized_path.rstrip('/')}/"
        await asyncio.to_thread(
            minio_client.put_object,
            bucket_name,
            object_name,
            BytesIO(b""),
            length=0,
        )
        return {"ok": True, "path": object_name}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


async def rename_path_in_minio(
    bucket_name: str,
    source_path: str,
    destination_path: str,
    is_folder: bool = False,
) -> dict[str, Any]:
    minio_client = get_minio_client()
    try:
        source = _normalize_path(source_path)
        destination = _normalize_path(destination_path)
        if not source or not destination:
            raise ValueError("Source and destination paths are required")

        def rename() -> int:
            if is_folder:
                source_prefix = f"{source.rstrip('/')}/"
                destination_prefix = f"{destination.rstrip('/')}/"
                objects = list(
                    minio_client.list_objects(
                        bucket_name,
                        prefix=source_prefix,
                        recursive=True,
                    )
                )
                if not objects:
                    raise FileNotFoundError(source)

                copied = 0
                for obj in objects:
                    relative_path = obj.object_name.removeprefix(source_prefix)
                    target = f"{destination_prefix}{relative_path}"
                    minio_client.copy_object(
                        bucket_name,
                        target,
                        CopySource(bucket_name, obj.object_name),
                    )
                    copied += 1

                delete_objects = [DeleteObject(obj.object_name) for obj in objects]
                list(minio_client.remove_objects(bucket_name, delete_objects))
                return copied

            minio_client.copy_object(
                bucket_name,
                destination,
                CopySource(bucket_name, source),
            )
            minio_client.remove_object(bucket_name, source)
            return 1

        copied_count = await asyncio.to_thread(rename)
        return {"ok": True, "copied_count": copied_count}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


async def get_file_from_minio(bucket_name: str, file_path: str) -> dict[str, Any]:
    minio_client = get_minio_client()

    try:
        normalized_path = _normalize_path(file_path)
        if not normalized_path:
            raise ValueError("File path cannot be empty")

        def read_object() -> bytes:
            response = minio_client.get_object(bucket_name, normalized_path)
            try:
                return response.read()
            finally:
                response.close()
                response.release_conn()

        file_data = await asyncio.to_thread(read_object)

        return {"file_data": file_data, "ok": True}
    except Exception as e:
        return {"error": str(e), "ok": False}


async def delete_path_from_minio(bucket_name: str, path: str) -> dict[str, Any]:
    minio_client = get_minio_client()

    try:
        normalized_path = _normalize_path(path)
        if not normalized_path:
            raise ValueError("Delete path cannot be empty")
        if path.rstrip().endswith("/"):
            normalized_path = f"{normalized_path}/"

        if normalized_path.endswith("/"):
            prefix = normalized_path.rstrip("/") + "/"

            objects = await asyncio.to_thread(
                lambda: list(
                    minio_client.list_objects(
                        bucket_name,
                        prefix=prefix,
                        recursive=True,
                    )
                )
            )

            delete_objects = [DeleteObject(obj.object_name) for obj in objects] # type: ignore

            if not delete_objects:
                return {
                    "message": f"No objects found under folder '{prefix}' in bucket '{bucket_name}'.",
                    "ok": True,
                    "deleted_count": 0,
                }

            errors = await asyncio.to_thread(
                lambda: list(minio_client.remove_objects(bucket_name, delete_objects))
            )

            if errors:
                return {
                    "message": f"Folder '{prefix}' partially deleted from bucket '{bucket_name}'.",
                    "ok": False,
                    "errors": [str(error) for error in errors],
                }

            return {
                "message": f"Folder '{prefix}' deleted successfully from bucket '{bucket_name}'.",
                "ok": True,
                "deleted_count": len(delete_objects),
            }

        await asyncio.to_thread(minio_client.remove_object, bucket_name, normalized_path)
        return {
            "message": f"File '{normalized_path}' deleted successfully from bucket '{bucket_name}'.",
            "ok": True,
            "deleted_count": 1,
        }

    except Exception as e:
        return {"error": str(e), "ok": False}
