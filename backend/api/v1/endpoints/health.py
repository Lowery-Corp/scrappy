from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text

from cache.redis import redis_manager
from db.session import engine

router = APIRouter(tags=["health"])


@router.get("")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def readiness_check() -> dict[str, str]:
    try:
        await redis_manager.get_client().ping()
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="A required dependency is unavailable",
        ) from exc

    return {"status": "ready"}


@router.get("/live")
async def liveness_check() -> dict[str, str]:
    return {"status": "alive", "timestamp": datetime.now(timezone.utc).isoformat()}
