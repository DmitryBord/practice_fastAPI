from datetime import date

from fastapi import Depends, HTTPException
from pydantic import BaseModel, Field
from starlette import status


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
