from datetime import date
from pydantic import BaseModel, Field
from pydantic_core import PydanticCustomError
from fastapi import Depends, HTTPException, status


class DatesQueryParams(BaseModel):
    start_date: date = Field(description="The date must be in format ('YYYY-MM-DD')")
    end_date: date = Field(description="The date must be in format ('YYYY-MM-DD')")


def validate_dates(dates: DatesQueryParams = Depends(DatesQueryParams)) -> DatesQueryParams:
    current_date = date.today()
    if dates.start_date > current_date or dates.end_date > current_date:
        # TODO: raise a error
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The date cannot be later than current date"
        )

    if dates.start_date > dates.end_date:
        # TODO: raise a error
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The start date cannot be later then end date"
        )

    return dates
