from datetime import date

from fastapi import Depends, HTTPException
from starlette import status

from pydantic import BaseModel, Field

from typing import Annotated


class PaginationTradingResult(BaseModel):
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=5, gt=0, le=100)


class TradingResultParams(BaseModel):
    oil_id: str | None = Field(
        default=None, description="for example ('A106')", max_length=4
    )
    delivery_type_id: str | None = Field(
        default=None, description="for example ('A')", max_length=1
    )
    delivery_basis_id: str | None = Field(
        default=None, description="for example ('NPT')", max_length=3
    )


class DatesQueryParams(BaseModel):
    start_date: date = Field(description="The date must be in format ('YYYY-MM-DD')")
    end_date: date = Field(description="The date must be in format ('YYYY-MM-DD')")


def validate_dates(dates: Annotated[DatesQueryParams, Depends()]) -> DatesQueryParams:
    current_date: date = date.today()

    if dates.start_date > current_date or dates.end_date > current_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The date cannot be later than current date",
        )

    if dates.start_date > dates.end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The start date cannot be later then end date",
        )

    return dates
