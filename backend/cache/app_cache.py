from __future__ import annotations

import json
import logging
from collections.abc import Iterable
from typing import Any

from cache.redis import redis_manager

logger = logging.getLogger(__name__)

CACHE_PREFIX = "scrappy:v1"
USER_CACHE_TTL_SECONDS = 30
ADMIN_CACHE_TTL_SECONDS = 15


class AppCache:
    """Small, fail-open application cache with explicit invalidation helpers."""

    async def get_json(self, key: str) -> Any | None:
        try:
            value = await redis_manager.get_client().get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception:
            logger.warning("Redis cache read failed for key %s", key)
            return None

    async def set_json(self, key: str, value: Any, ttl: int) -> bool:
        try:
            return bool(
                await redis_manager.get_client().set(
                    key,
                    json.dumps(value, default=str),
                    ex=ttl,
                )
            )
        except Exception:
            logger.warning("Redis cache write failed for key %s", key)
            return False

    async def invalidate_keys(self, keys: Iterable[str]) -> None:
        keys = list(keys)
        if not keys:
            return
        try:
            await redis_manager.get_client().delete(*keys)
        except Exception:
            logger.warning("Redis cache invalidation failed")

    async def invalidate_pattern(self, pattern: str) -> None:
        try:
            client = redis_manager.get_client()
            keys = [key async for key in client.scan_iter(match=pattern, count=100)]
            await self.invalidate_keys(keys)
        except Exception:
            logger.warning("Redis cache pattern invalidation failed for %s", pattern)

    async def invalidate_user(self, user_id: Any) -> None:
        await self.invalidate_pattern(f"{CACHE_PREFIX}:user:{user_id}:*")

    async def invalidate_admin(self) -> None:
        await self.invalidate_pattern(f"{CACHE_PREFIX}:admin:*")


app_cache = AppCache()
