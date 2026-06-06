from concurrent.futures import ProcessPoolExecutor

import asyncio

import curl_cffi

from time import time

# from core.init_db import create_table
from spimex_app.pipline.pipeline import Pipeline

from spimex_app.service.container import Container

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def main():
    # await create_table()

    with ProcessPoolExecutor() as pool:
        async with curl_cffi.requests.AsyncSession() as session:
            pipline = Pipeline(
                downloader_pdf=Container.get_pdf_downloader(),
                downloader_xls=Container.get_xls_downloader(),
                loader=Container.get_psql_loader()
            )
            await pipline.run(pool, session)


if __name__ == "__main__":
    t0 = time()
    asyncio.run(main())
    print(time() - t0)
