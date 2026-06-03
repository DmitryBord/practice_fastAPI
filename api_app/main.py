from fastapi import FastAPI, Depends, Query

from .schemas.spimex_get import SpimexTradingResultsGet, SpimexTradingDatesGet
from .dependencies import DatesQueryParams, validate_dates, TradingResultParams, PaginationTradingResult
from .services import SpimexTradingService

from core.init_db import create_table

from contextlib import asynccontextmanager

from typing import Annotated

import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_table()
    yield


app = FastAPI(lifespan=lifespan)


# TODO: Обработать краевые случаи
@app.get("/spimex/trading-results/dates/", response_model=SpimexTradingDatesGet)
async def get_last_trading_dates(
        count_days: Annotated[int, Query(gt=0)] = 1,
        service: SpimexTradingService = Depends(SpimexTradingService)
):
    result = await service.get_last_trading_dates(count_days=count_days)
    return result


# TODO: Обработать краевые случаи
@app.get("/spimex/trading-results", response_model=list[SpimexTradingResultsGet])
async def get_trading_results(
        # TODO: Разобраться зависимостями
        dates: Annotated[DatesQueryParams, Depends(validate_dates)],
        query_params: Annotated[TradingResultParams, Query()],
        pagination: Annotated[PaginationTradingResult, Depends(PaginationTradingResult)],
        service: Annotated[SpimexTradingService, Depends(SpimexTradingService)]
):
    result = await service.get_trading_results(dates, query_params, pagination)
    return result


if __name__ == '__main__':
    uvicorn.run("app.main", host="0.0.0.0", reload=True)
