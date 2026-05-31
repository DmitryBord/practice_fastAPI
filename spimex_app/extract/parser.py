import asyncio
import aiohttp
from bs4 import BeautifulSoup
from .filtres import tag_filter, compare_date
import logging
from datetime import date
from tenacity import retry, wait_exponential, retry_if_exception_type, stop_after_attempt, before_sleep_log
from typing import AsyncGenerator

logger = logging.getLogger(__name__)


def error_callback(retry_state):
    error = retry_state.outcome.exception()
    link = retry_state.args[0]

    logger.info(f"Ошибка при обработке url: {link}\nОшибка: repr({error})")
    return ""


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
    retry_error_callback=error_callback,
    before_sleep=before_sleep_log(logger, logging.INFO)
)
async def get_html(url: str, session: aiohttp.ClientSession):
    async with session.get(url, timeout=aiohttp.ClientTimeout(10)) as response:
        response.raise_for_status()
        return await response.text()


async def parse_links(
        session: aiohttp.ClientSession, last_date: date
) -> AsyncGenerator[tuple[list[str], list[str]], None]:
    for count in range(1, 84):
        links_pdf: list[str] = []
        links_xls: list[str] = []

        logger.info(f"Страница {count}")

        url = (
            f"https://spimex.com/markets/oil_products/trades/results/?page=page-{count}"
        )

        html = await get_html(url, session)

        if not html:
            continue

        soap = BeautifulSoup(html, "lxml")
        data = soap.find_all(tag_filter)

        for link in data:
            base_link: str = "https://spimex.com"
            link_tag_pdf = link.find("a", class_="accordeon-inner__item-title link pdf")
            link_tag_lsx = link.find("a", class_="accordeon-inner__item-title link xls")

            if last_date is not None:
                if not compare_date(link, last_date):
                    return

            if link_tag_pdf and "href" in link_tag_pdf.attrs:
                links_pdf.append(base_link + link_tag_pdf["href"])

            if link_tag_lsx and "href" in link_tag_lsx.attrs:
                links_xls.append(base_link + link_tag_lsx["href"])

        yield links_pdf, links_xls
