from typing import TypedDict


class ParsedData(TypedDict):
    data: list[list[str | None]]
    headers: list[str]
    trading_date: str
    total_sum: int | None
