from pydantic import BaseModel, ConfigDict, field_serializer
from datetime import date
from decimal import Decimal


class SpimexTradingDatesGet(BaseModel):
    list_dates: list[date]


class SpimexTradingResultsGet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    exchange_product_id: str
    exchange_product_name: str
    oil_id: str
    delivery_basis_id: str
    delivery_basis_name: str
    delivery_type_id: str
    volume: int
    total: Decimal
    count: int
    date: date

    @field_serializer("total", when_used="json")
    def total_serializer(self, value: Decimal):
        return f"{value.normalize():f}"
