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
import curl_cffi
from curl_cffi.requests.errors import RequestsError
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
        # retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        retry=retry_if_exception_type(RequestsError),
        retry_error_callback=error_callback,
        before_sleep=before_sleep_log(logger, logging.INFO),
    )
    async def download(self, session: curl_cffi.requests.AsyncSession, link: str) -> str:
        response = await session.get(link, timeout=10, impersonate="chrome120")
        response.raise_for_status()
        rand_id = uuid.uuid4().hex[:8]
        file_path = f"{self.file_path}/{rand_id}.{self.file_type}"

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(response.content)

        logger.info(f"Скачал файл {file_path}")

        return file_path
