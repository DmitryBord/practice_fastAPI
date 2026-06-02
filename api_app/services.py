from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .dependencies import DatesQueryParams, TradingResultParam, PaginationTradingResult
from .models import SpimexTradingResults
from .schemas import SpimexTradingResultsGet


async def get_latest_trading_results(
        session: AsyncSession,
        dates: DatesQueryParams,
        query_params: TradingResultParam,
        pagination: PaginationTradingResult
) -> list[SpimexTradingResultsGet]:

    stmt = (
        select(SpimexTradingResults)
        .order_by(SpimexTradingResults.date.desc())
    )

    if not dates.is_none():
        stmt = stmt.where(SpimexTradingResults.date >= dates.start_date, SpimexTradingResults.date <= dates.end_date)

    if query_params.oil_id:
        oil_id = query_params.oil_id.upper()
        stmt = stmt.where(SpimexTradingResults.oil_id == oil_id)

    if query_params.delivery_type_id:
        delivery_type_id = query_params.delivery_type_id.upper()
        stmt = stmt.where(SpimexTradingResults.delivery_type_id == delivery_type_id)

    if query_params.delivery_basis_id:
        delivery_basis_id = query_params.delivery_basis_id.upper()
        stmt = stmt.where(SpimexTradingResults.delivery_basis_id == delivery_basis_id)

    stmt = stmt.offset(pagination.offset).limit(pagination.limit)

    results = await session.execute(stmt)
    return results.scalars().all()
