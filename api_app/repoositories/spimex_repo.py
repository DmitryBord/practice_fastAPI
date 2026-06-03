from datetime import date
from core.database import AsyncSession
from sqlalchemy import select
from ..models.spimex_trading import SpimexTradingResults
from ..dependencies import DatesQueryParams, TradingResultParams, PaginationTradingResult


class SpimexRepository:
    model = SpimexTradingResults

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_dates(self, count: int) -> list[date]:
        stmt = (
            select(SpimexTradingResults.date)
            .distinct()
            .order_by(SpimexTradingResults.date.desc())
            .limit(count)
        )
        results = await self.session.execute(stmt)
        dates = results.scalars().all()
        return list(dates)

    async def get_list(
            self,
            dates: DatesQueryParams,
            params: TradingResultParams,
            pagination: PaginationTradingResult
    ) -> list[SpimexTradingResults]:

        # TODO: Решить что делать с пагинацией
        stmt = (
            select(SpimexTradingResults)
            .order_by(SpimexTradingResults.date.desc())
        )

        if not dates.is_none():
            stmt = stmt.where(SpimexTradingResults.date >= dates.start_date,
                              SpimexTradingResults.date <= dates.end_date)

        if params.oil_id:
            oil_id = params.oil_id.upper()
            stmt = stmt.where(SpimexTradingResults.oil_id == oil_id)

        if params.delivery_type_id:
            delivery_type_id = params.delivery_type_id.upper()
            stmt = stmt.where(SpimexTradingResults.delivery_type_id == delivery_type_id)

        if params.delivery_basis_id:
            delivery_basis_id = params.delivery_basis_id.upper()
            stmt = stmt.where(SpimexTradingResults.delivery_basis_id == delivery_basis_id)

        stmt = stmt.offset(pagination.offset).limit(pagination.limit)

        results = await self.session.execute(stmt)
        return list(results.scalars().all())
