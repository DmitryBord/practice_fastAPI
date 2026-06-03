from sqlalchemy.ext.asyncio import AsyncSession

from .dependencies import DatesQueryParams, TradingResultParams, PaginationTradingResult
from .models.spimex_trading import SpimexTradingResults


from .repoositories.spimex_repo import SpimexRepository
from fastapi import Depends
from core.database import get_session
from datetime import date


class SpimexTradingService:
    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.spimex_repo = SpimexRepository(session=session)

    async def get_last_trading_dates(self, count_days: int) -> dict[str, list[date]]:

        dates: list[date] = await self.spimex_repo.get_dates(count_days)
        return {"list_dates": dates}

    async def get_trading_results(
            self,
            dates: DatesQueryParams,
            params: TradingResultParams,
            pagination: PaginationTradingResult
    ) -> list[SpimexTradingResults]:

        result = await self.spimex_repo.get_list(dates, params, pagination)
        return result
