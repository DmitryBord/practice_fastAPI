from datetime import date

from fastapi import FastAPI, Depends, Query

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .schemas import SpimexTradingResultsGet
from .dependencies import DatesQueryParams, validate_dates
from .services import get_dynamics

from .models import SpimexTradingResults
from core.init_db import create_table
from core.database import get_session

from contextlib import asynccontextmanager

from typing import Annotated

import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_table()
    yield


app = FastAPI(lifespan=lifespan)


# TODO: Обработать краевые случаи
@app.get("/spimex/trading-results/dates/", response_model=dict[str, list[date]])
async def get_last_trading_dates(
        count_days: Annotated[int, Query(gt=0)] = 1,
        session: AsyncSession = Depends(get_session)
):
    stmt = (
        select(SpimexTradingResults.date)
        .distinct()
        .order_by(SpimexTradingResults.date.desc())
        .limit(count_days)
    )
    results = await session.execute(stmt)
    dates = results.scalars().all()
    return {"list_dates": dates}


# TODO: Обработать краевые случаи
@app.get("/spimex/trading-results", response_model=list[SpimexTradingResultsGet])
async def get_trading_results(
        dates: DatesQueryParams = Depends(validate_dates),
        oil_id: Annotated[str | None, Query(description="for example ('A106')", max_length=4)] = None,
        delivery_type_id: Annotated[str | None, Query(description="for example ('A')", max_length=1)] = None,
        delivery_basis_id: Annotated[str | None, Query(description="for example ('NPT')", max_length=3)] = None,
        session:
        AsyncSession = Depends(get_session)
):

    if not dates.is_none():
        return await get_dynamics(session, dates, oil_id, delivery_type_id, delivery_basis_id)


if __name__ == '__main__':
    uvicorn.run("app.main", host="0.0.0.0", reload=True)
