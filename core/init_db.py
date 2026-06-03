from api_app.models.spimex_trading import SpimexTradingResults
from core.database import async_engine
import logging

from api_app.models.spimex_trading import Base

logger = logging.getLogger(__name__)


async def create_table():
    async with async_engine.begin() as conn:
        logger.info("Создаю таблицу в базе данных")
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


