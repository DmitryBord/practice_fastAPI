import asyncio
from concurrent.futures import ProcessPoolExecutor

import pandas as pd
from spimex_app.transform.utils import ParsedData
from spimex_app.transform.transform_pdf import parse_pdf, transform_to_DateFrame
from spimex_app.transform.transform_xls import TransformXls
from pathlib import Path


def process_pdf_transform(file_path: str) -> list[dict]:
    data_parce: ParsedData = parse_pdf(file_path)
    df: pd.DataFrame = transform_to_DateFrame(data_parce)

    return df.to_dict(orient="records")


def process_xls_transform(file_path: str) -> list[dict]:
    df: pd.DataFrame = TransformXls(file_path).transform()
    return df.to_dict(orient="records")


async def process_transform(
        pool: ProcessPoolExecutor,
        pdf_files: list[str],
        xls_files: list[str]
) -> list[dict]:
    loop = asyncio.get_running_loop()

    all_tasks = await asyncio.gather(
        asyncio.gather(*[loop.run_in_executor(pool, process_pdf_transform, f) for f in pdf_files]),
        asyncio.gather(*[loop.run_in_executor(pool, process_xls_transform, f) for f in xls_files])
    )

    results: list[dict] = []

    for data in all_tasks:
        results.extend(data)

    return results


def delete_files() -> None:
    path = Path(__file__).resolve().parents[1]
    pdf_file = path / "tmp/pdf"
    xls_file = path / "tmp/xls"
    [f.unlink(missing_ok=True) for f in pdf_file.iterdir() if f.is_file()]
    [f.unlink(missing_ok=True) for f in xls_file.iterdir() if f.is_file()]
