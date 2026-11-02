import unittest

from cache.app_cache import AppCache


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self.values.get(key)

    async def set(self, key: str, value: str, ex: int) -> bool:
        self.values[key] = value
        return True

    async def delete(self, *keys: str) -> int:
        deleted = 0
        for key in keys:
            if key in self.values:
                deleted += 1
                del self.values[key]
        return deleted

    async def scan_iter(self, match: str, count: int):
        prefix = match.removesuffix("*")
        for key in list(self.values):
            if key.startswith(prefix):
                yield key


class AppCacheTests(unittest.IsolatedAsyncioTestCase):
    async def test_user_invalidation_removes_only_user_namespace(self) -> None:
        redis = FakeRedis()
        cache = AppCache()

        from cache.redis import redis_manager

        original_client = redis_manager._client
        redis_manager._client = redis  # type: ignore[assignment]
        try:
            await cache.set_json("scrappy:v1:user:one:files:all", {"value": 1}, 30)
            await cache.set_json("scrappy:v1:user:two:files:all", {"value": 2}, 30)
            await cache.invalidate_user("one")

            self.assertIsNone(await cache.get_json("scrappy:v1:user:one:files:all"))
            self.assertEqual(
                await cache.get_json("scrappy:v1:user:two:files:all"),
                {"value": 2},
            )
        finally:
            redis_manager._client = original_client


if __name__ == "__main__":
    unittest.main()
