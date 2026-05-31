import pdfplumber
import pandas as pd
import re
from spimex_app.transform.utils import ParsedData

import logging

logger = logging.getLogger(__name__)


def get_total_sum_from_pdf(text: list[dict]) -> int | None:
    for line in text:
        line = line["text"].strip()
        if line.startswith("Итого:"):
            parts = line.split()
            total_target = int(parts[-1])
            return total_target


def clean_text(text):
    return text.replace("\n", " ").strip() if text else ""


def parse_pdf(path_file: str) -> ParsedData:
    data = []
    full_header = []
    trading_date = ""
    total_sum = 0

    try:
        with pdfplumber.open(path_file) as pdf:
            if not pdf.pages:
                logger.error("PDF файл пуст")

            idx_last_page: int = len(pdf.pages) - 1

            first_page_text: str = pdf.pages[0].extract_text() or ""
            date_match = re.search(r"\d{2}\.\d{2}\.\d{4}", first_page_text)

            if not date_match:
                logger.warning(f"Warning: Дата торгов не найдена в {path_file}")
            else:
                trading_date = date_match.group(0)

            for i, page in enumerate(pdf.pages):
                table = page.extract_table()

                if not table:
                    continue

                if i == 0:
                    h1, h2 = table[0], table[1]
                    full_header = [
                        f"{clean_text(a)} {clean_text(b)}".strip()
                        for a, b in zip(h1, h2)
                    ]
                    data.extend(table[2:])
                else:
                    data.extend(table)

                if i == idx_last_page:
                    lines = page.extract_text_lines()
                    total_sum = get_total_sum_from_pdf(lines)

    except FileNotFoundError:
        logger.error("Файл не найден")
    except Exception as err:
        logger.error(f"Произошла ошибка при открытии файла: {err}")

    result: ParsedData = {
        "data": data,
        "headers": full_header,
        "trading_date": trading_date,
        "total_sum": total_sum,
    }

    return result


def transform_to_DateFrame(data: ParsedData) -> pd.DataFrame:
    if not data["headers"] or not data["data"]:
        logger.error("Ошибка: Данные для формирования DataFrame отсутствуют")
        return pd.DataFrame()

    df = pd.DataFrame(data["data"], columns=data["headers"])
    df = df.replace("\n", " ", regex=True)

    df["Количество Договоров, шт."] = pd.to_numeric(
        df["Количество Договоров, шт."].str.replace(" ", ""), errors="coerce"
    )
    df = df[df["Количество Договоров, шт."] > 0]

    columns = [
        "Код Инструмента",
        "Наименование Инструмента",
        "Базис поставки",
        "Объем Договоров в единицах измерения",
        "Обьем Договоров, руб.",
        "Количество Договоров, шт.",
    ]

    column_mapping = {
        "Код Инструмента": "exchange_product_id",
        "Наименование Инструмента": "exchange_product_name",
        "Базис поставки": "delivery_basis_name",
        "Объем Договоров в единицах измерения": "volume",
        "Обьем Договоров, руб.": "total",
        "Количество Договоров, шт.": "count",
    }

    df = df[columns]
    df = df.rename(columns=column_mapping)

    df["volume"] = pd.to_numeric(df["volume"], errors="coerce").fillna(0).astype(int)
    df["total"] = pd.to_numeric(df["total"], errors="coerce").fillna(0.0).astype(float)

    df["oil_id"] = df["exchange_product_id"].str[:4]
    df["delivery_basis_id"] = df["exchange_product_id"].str[4:7]
    df["delivery_type_id"] = df["exchange_product_id"].str[-1]

    if data["trading_date"]:
        df["date"] = pd.to_datetime(data["trading_date"], dayfirst=True).date()
    else:
        raise ValueError("Дата торгов не была найдена")

    # calculated_count = df["count"].sum()
    # calculated_count = int(calculated_count)
    # pdf_total_count = int(data["total_sum"])

    return df
