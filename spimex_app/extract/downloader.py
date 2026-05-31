from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
import uuid
import os
import aiofiles
import aiohttp
import asyncio
import logging


logger = logging.getLogger(__name__)


def error_callback(retry_state):
    link = retry_state.args[2]
    error = retry_state.outcome.exception()

    logger.error(f"Не удалось скачать файл {link}\nОшибка: {repr(error)}")
    return ""


class Downloader:
    def __init__(self, file_path: str, file_type: str):
        if not os.path.isdir(file_path):
            raise NotADirectoryError(
                f"Директория с таким именем {file_path} не найдена!"
            )

        self.file_path = file_path
        self.file_type = file_type

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        retry_error_callback=error_callback,
        before_sleep=before_sleep_log(logger, logging.INFO),
    )
    async def download(self, session: aiohttp.ClientSession, link: str) -> str:
        async with session.get(link, timeout=aiohttp.ClientTimeout(10)) as response:
            response.raise_for_status()
            rand_id = uuid.uuid4().hex[:8]

            async with aiofiles.open(
                f"{self.file_path}/{rand_id}.{self.file_type}", "wb"
            ) as f:
                async for chunk in response.content.iter_any():
                    await f.write(chunk)

            file_path = f"{self.file_path}/{rand_id}.{self.file_type}"
            logger.info(f"Скачал файл {file_path}")

            return file_path
