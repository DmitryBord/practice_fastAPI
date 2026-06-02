import asyncio

from concurrent.futures import ProcessPoolExecutor
from datetime import date

import curl_cffi

from core.db_utils import get_last_date_from_DB
from spimex_app.extract.downloader import Downloader
from spimex_app.extract.parser import parse_links
from spimex_app.load.loaders import PostgresLoader
from spimex_app.service.processing import process_transform, delete_files

import logging

logger = logging.getLogger(__name__)


class Pipeline:
    def __init__(self, downloader_pdf: Downloader, downloader_xls: Downloader, loader: PostgresLoader):
        self.downloader_pdf = downloader_pdf
        self.downloader_xls = downloader_xls
        self.loader = loader

    async def download(
            self,
            session: curl_cffi.requests.AsyncSession,
            links_pdf: list[str],
            links_xls: list[str],
    ) -> tuple[list[str], list[str]]:

        pdf_files, xls_files = await asyncio.gather(
            asyncio.gather(*[self.downloader_pdf.download(session, link) for link in links_pdf]),
            asyncio.gather(*[self.downloader_xls.download(session, link) for link in links_xls])
        )

        return pdf_files, xls_files

    async def run(self, pool: ProcessPoolExecutor, session: curl_cffi.requests.AsyncSession):
        last_date: date | None = await get_last_date_from_DB()

        async for links_pdf, links_xls in parse_links(session, last_date):
            logger.info("Приступаю к загрузке")
            pdf_files, xls_files = await self.download(session, links_pdf, links_xls)

            # Запускает процесс парсинга файлов
            logger.info("Готовлю данные для загрузки в БД")

            results: [] = await process_transform(
                pool, pdf_files, xls_files
            )

            delete_files()

            page_data: list[dict] = []

            for data in results:
                page_data.extend(data)

            if not page_data:
                logger.info("Новых данных нет")
                continue

            logging.info("Подаю данные в БД")
            await self.loader.load_to_sql(page_data)
