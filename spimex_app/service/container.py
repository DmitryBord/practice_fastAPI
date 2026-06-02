from spimex_app.extract.downloader import Downloader
from spimex_app.load.loaders import PostgresLoader
from api_app.models import SpimexTradingResults
from pathlib import Path


class Container:
    @staticmethod
    def get_pdf_downloader() -> Downloader:
        path = Path(__file__).resolve().parents[1]
        downloader = Downloader(file_path=str(path/"tmp/pdf"), file_type="pdf")
        return downloader

    @staticmethod
    def get_xls_downloader() -> Downloader:
        path = Path(__file__).resolve().parents[1]
        downloader = Downloader(file_path=str(path/"tmp/xls"), file_type="xls")
        return downloader

    @staticmethod
    def get_psql_loader() -> PostgresLoader:
        loader = PostgresLoader(SpimexTradingResults)
        return loader
