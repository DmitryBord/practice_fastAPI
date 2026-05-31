from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import async_engine
from core.init_db import logger
from core.models import SpimexTradingResults


async def get_last_date_from_DB():
    async with AsyncSession(async_engine) as session:
        async with session.begin():
            logger.info("Получаю последнюю дату загрузке в базе данных")

            query = select(func.max(SpimexTradingResults.date))

            result = await session.execute(query)
            last_date = result.scalar()
        return last_date
