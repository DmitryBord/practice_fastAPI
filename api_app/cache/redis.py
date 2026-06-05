from datetime import datetime, timedelta
import redis.asyncio as redis
from core.config import settings

import json


class RedisCacheBackend:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url, decode_responses=True)

    async def set_dict(self, key: str, value: list[dict]) -> None:
        await self.redis.set(
            key, json.dumps(value), exat=RedisHandler.get_time_deadline()
        )

    async def set_list(self, key: str, values: list[str]) -> None:
        await self.redis.set(
            key, json.dumps(values), exat=RedisHandler.get_time_deadline()
        )

    async def get(self, key: str) -> str | None:
        return await self.redis.get(key)

    async def delete(self, key) -> None:
        await self.redis.delete(key)

    async def close(self) -> None:
        await self.redis.close()


class RedisHandler:
    @classmethod
    def get_time_deadline(cls) -> datetime:
        now: datetime = datetime.now()
        target_date: datetime = now.replace(hour=14, minute=11, second=0, microsecond=0)

        if now >= target_date:
            target_date += timedelta(days=1)

        return target_date

    @classmethod
    def get_key_by_args(cls, *args: dict) -> str:
        args_params = ":".join(f"{k}={v}" for item in args for k, v in item.items())

        key = f"trades:{args_params}"
        return key

    @classmethod
    def get_redis(cls) -> RedisCacheBackend:
        redis_url = settings.redis_url
        return RedisCacheBackend(redis_url)
