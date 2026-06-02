from sqlalchemy.dialects.postgresql import insert
from core.database import async_engine, AsyncSessionLocal
from api_app.models import Base
from typing import Type


class PostgresLoader:
    def __init__(self, db: Type[Base]):
        self.db = db
        self.engine = async_engine

    async def load_to_sql(self, data: list[dict]) -> None:
        if not data:
            return

        async with AsyncSessionLocal() as session:
            async with session.begin():
                stmt = insert(self.db).values(data)
                stmt = stmt.on_conflict_do_nothing(constraint="uniq_date_product_id")

                await session.execute(stmt)
