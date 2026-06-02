from datetime import date

from fastapi import Depends, HTTPException, Query
from pydantic import BaseModel, Field
from starlette import status

from typing import Annotated


class PaginationTradingResult:
    def __init__(
            self,
            offset: Annotated[int, Query(ge=0)] = 0,
            limit: Annotated[int, Query(ge=0, le=100)] = 5
    ):
        self.offset = offset
        self.limit = limit


class TradingResultParam(BaseModel):
    oil_id: str | None = Field(default=None, description="for example ('A106')", max_length=4)
    delivery_type_id: str | None = Field(default=None, description="for example ('A')", max_length=1)
    delivery_basis_id: str | None = Field(default=None, description="for example ('NPT')", max_length=3)


class DatesQueryParams(BaseModel):
    start_date: date | None = Field(default=None, description="The date must be in format ('YYYY-MM-DD')")
    end_date: date | None = Field(default=None, description="The date must be in format ('YYYY-MM-DD')")

    def is_none(self):
        if self.start_date is None or self.end_date is None:
            return True


def validate_dates(dates: DatesQueryParams = Depends(DatesQueryParams)) -> DatesQueryParams:
    if dates.is_none():
        return dates

    current_date = date.today()

    if dates.start_date > current_date or dates.end_date > current_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The date cannot be later than current date"
        )

    if dates.start_date > dates.end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The start date cannot be later then end date"
        )

    return dates
