from decimal import Decimal
from datetime import datetime, date
from sqlalchemy import String, Numeric, DateTime, Date, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from typing import Annotated

numeric_price = Annotated[Decimal, Numeric(15, 2)]


class Base(DeclarativeBase):
    pass


class SpimexTradingResults(Base):
    __tablename__ = "spimex_trading_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    exchange_product_id: Mapped[str]
    exchange_product_name: Mapped[str] = mapped_column(String(255))
    oil_id: Mapped[str]
    delivery_basis_id: Mapped[str]
    delivery_basis_name: Mapped[str] = mapped_column(String(255))
    delivery_type_id: Mapped[str]
    volume: Mapped[int]
    total: Mapped[numeric_price]
    count: Mapped[int]
    date: Mapped[date] = mapped_column(Date)

    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )



    __table_args__ = (
        UniqueConstraint(
            "exchange_product_id",
            "date",
            "delivery_basis_name",
            name="uniq_date_product_id",
        ),
    )
