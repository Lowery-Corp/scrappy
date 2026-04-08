from fastapi import APIRouter
from typing import Any

from repositories.minio import get_bucket_structure

router = APIRouter(tags=["minio"])


@router.get("/bucket-structure")
async def fetch_bucket_structure() -> dict[str, Any]:
    bucket_structure: dict[str, Any] = await get_bucket_structure("testing")
    return {"bucket_structure": bucket_structure}

