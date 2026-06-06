from fastapi import FastAPI, Depends, Query

from api_app.schemas.spimex_get import SpimexTradingResultsGet
from api_app.dependencies import (
    DatesQueryParams,
    validate_dates,
    TradingResultParams,
    PaginationTradingResult,
)
from api_app.services import SpimexTradingService

from core.init_db import create_table

from contextlib import asynccontextmanager
from typing import Annotated

import uvicorn


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # await create_table()
#     yield


# app = FastAPI(
app = FastAPI()


@app.get("/spimex/trading-results", response_model=list[SpimexTradingResultsGet])
async def get_trading_results(
    query_params: Annotated[TradingResultParams, Depends()],
    service: Annotated[SpimexTradingService, Depends()],
    pagination: Annotated[PaginationTradingResult, Depends()],
):
    result = await service.get_trading_results(
        params=query_params, pagination=pagination
    )

    return result


@app.get("/spimex/trading-results/dates/", response_model=list[str])
async def get_last_trading_dates(
    service: Annotated[SpimexTradingService, Depends()],
    count_days: Annotated[int, Query(gt=0, le=100)] = 1,
):
    result = await service.get_last_trading_dates(count_days=count_days)
    return result


@app.get(
    "/spimex/trading-results/dynamics", response_model=list[SpimexTradingResultsGet]
)
async def get_dynamic(
    query_params: Annotated[TradingResultParams, Depends()],
    service: Annotated[SpimexTradingService, Depends()],
    dates: Annotated[DatesQueryParams, Depends(validate_dates)],
    pagination: Annotated[PaginationTradingResult, Depends()],
):
    result = await service.get_dynamic(
        params=query_params, pagination=pagination, dates=dates
    )

    return result


if __name__ == "__main__":
    uvicorn.run("api_app.main:app", host="0.0.0.0", reload=True)
