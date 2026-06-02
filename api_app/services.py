from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .dependencies import DatesQueryParams
from .models import SpimexTradingResults
from .schemas import SpimexTradingResultsGet


async def get_dynamics(
        session: AsyncSession,
        dates: DatesQueryParams,
        oil_id: str | None = None,
        delivery_type_id: str | None = None,
        delivery_basis_id: str | None = None,
) -> list[SpimexTradingResultsGet]:
    stmt = (
        select(SpimexTradingResults)
        .where(SpimexTradingResults.date >= dates.start_date, SpimexTradingResults.date <= dates.end_date)
    )

    if oil_id:
        oil_id = oil_id.upper()
        stmt = stmt.where(SpimexTradingResults.oil_id == oil_id)

    if delivery_type_id:
        delivery_type_id = delivery_type_id.upper()
        stmt = stmt.where(SpimexTradingResults.delivery_type_id == delivery_type_id)

    if delivery_basis_id:
        delivery_basis_id = delivery_basis_id.upper()
        stmt = stmt.where(SpimexTradingResults.delivery_basis_id == delivery_basis_id)

    stmt = stmt.order_by(
        SpimexTradingResults.date.desc()
    )

    results = await session.execute(stmt)
    return results.scalars().all()


async def get_latest_trading_results(
        session: AsyncSession,
        oil_id: str | None = None,
        delivery_type_id: str | None = None,
        delivery_basis_id: str | None = None,
) -> list[SpimexTradingResultsGet]:
    pass
