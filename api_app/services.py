from fastapi import Depends
from pydantic import TypeAdapter

from sqlalchemy.ext.asyncio import AsyncSession

from .dependencies import DatesQueryParams, TradingResultParams, PaginationTradingResult
from .cache.redis import RedisCacheBackend, RedisHandler
from .repoositories.spimex_repo import SpimexRepository
from .schemas.spimex_get import SpimexTradingResultsGet
from .models.spimex_trading import SpimexTradingResults

from core.database import get_session

from datetime import date

from typing import Annotated

import redis
import json


class SpimexTradingService:
    _adapter_trading_results = TypeAdapter(list[SpimexTradingResultsGet])

    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_session)],
        cache: Annotated[RedisCacheBackend, Depends(RedisHandler.get_redis)],
    ):
        self.spimex_repo = SpimexRepository(session=session)
        self.cache = cache

    async def _get_cache_or_fetch(
        self, key_parts: list[dict], coro
    ) -> list[SpimexTradingResultsGet | SpimexTradingResults]:
        key: str = RedisHandler.get_key_by_args(*key_parts)

        try:
            cache: str = await self.cache.get(key)
        except redis.exceptions.RedisError:
            cache = ""

        if cache:
            return self._adapter_trading_results.validate_json(cache)

        results = await coro()

        trades: list[dict] = [
            SpimexTradingResultsGet.model_validate(item).model_dump(mode="json")
            for item in results
        ]

        await self.cache.set_dict(key=key, value=trades)

        return results

    async def get_last_trading_dates(self, count_days: int) -> list[str]:
        try:
            cache: str = await self.cache.get(f"last_dates:{count_days}")
        except redis.exceptions.RedisError:
            cache = ""

        if cache:
            result: list[str] = json.loads(cache)
            return result

        result: list[date] = await self.spimex_repo.get_dates(count_days)
        dates: list[str] = [item.strftime("%Y-%m-%d") for item in result]

        await self.cache.set_list(f"last_dates:{count_days}", dates)

        return dates

    async def get_dynamic(
        self,
        params: TradingResultParams,
        dates: DatesQueryParams,
        pagination: PaginationTradingResult,
    ) -> list[SpimexTradingResultsGet]:

        params_dict: dict = params.model_dump(exclude_none=True)
        dates_dict: dict = dates.model_dump(exclude_none=True)
        paginate_dict: dict = pagination.model_dump(exclude_none=True)

        result = await self._get_cache_or_fetch(
            key_parts=[params_dict, dates_dict, paginate_dict],
            coro=lambda: self.spimex_repo.get_list(
                params=params, pagination=pagination, dates=dates
            ),
        )

        return result

    async def get_trading_results(
        self, params: TradingResultParams, pagination: PaginationTradingResult
    ) -> list[SpimexTradingResultsGet]:

        params_dict: dict = params.model_dump(exclude_none=True, mode="json")
        paginate_dict: dict = pagination.model_dump(exclude_none=True, mode="json")

        result = await self._get_cache_or_fetch(
            key_parts=[params_dict, paginate_dict],
            coro=lambda: self.spimex_repo.get_list(
                params=params, pagination=pagination
            ),
        )

        return result
