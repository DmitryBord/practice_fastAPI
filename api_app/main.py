from datetime import date

from fastapi import FastAPI, Depends, Query

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .schemas import SpimexTradingResultsGet
from .dependencies import DatesQueryParams, validate_dates, TradingResultParam, PaginationTradingResult
from .services import get_latest_trading_results

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
        dates: Annotated[DatesQueryParams, Depends(validate_dates)],
        query_params: Annotated[TradingResultParam, Depends(TradingResultParam)],
        pagination: Annotated[PaginationTradingResult, Depends(PaginationTradingResult)],
        session: Annotated[AsyncSession, Depends(get_session)]
):
    return await get_latest_trading_results(session, dates, query_params, pagination)


if __name__ == '__main__':
    uvicorn.run("app.main", host="0.0.0.0", reload=True)
