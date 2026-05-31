import re
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class TransformXls:
    def __init__(self, path_file: str):
        self.path: str = path_file
        self.data: dict = {}
        self.df = pd.DataFrame()

    def __extract_meta_data(self, full_df: pd.DataFrame):
        date_mask = full_df.astype(str).apply(
            lambda col: col.str.contains("Дата торгов", na=False)
        )
        if date_mask.any().any():
            row_idx = date_mask.any(axis=1).idxmax()
            row_text = " ".join(map(str, full_df.iloc[row_idx]))
            date_match = re.search(r"\d{2}\.\d{2}\.\d{4}", row_text)
            if date_match:
                self.data["trading_date"] = date_match.group(0)

        if "trading_date" not in self.data:
            raise ValueError("Дата торгов не была найдена")

        total_sum_mask = full_df[1].astype(str).str.contains("Итого", na=False)
        if total_sum_mask.any():
            total_idx = full_df.index[total_sum_mask][-2]
            self.data["total_sum"] = full_df.at[total_idx, full_df.columns[-1]]
        else:
            raise ValueError("Строка 'Итого' для валидации не найдена")

    def transform(self) -> pd.DataFrame:
        try:
            full_df = pd.read_excel(self.path, header=None)
        except FileNotFoundError:
            logger.error("Файл не найден")
            return pd.DataFrame()
        except Exception as err:
            logger.error(f"Произошла ошибка при открытии файла: {err}")
            return pd.DataFrame()
        self.__extract_meta_data(full_df)

        anchor_mask = (
            full_df.astype(str)
            .apply(
                lambda col: col.str.contains(
                    "Единица измерения: Метрическая тонна", na=False
                )
            )
            .any(axis=1)
        )

        if not anchor_mask.any():
            return pd.DataFrame()

        header_start = full_df.index[anchor_mask][0] + 3

        df = full_df.iloc[header_start:].copy()

        itogo_mask = df[1].astype(str).str.contains("Итого", na=False)
        if itogo_mask.any():
            end_idx = df.index[itogo_mask][0]
            df = df.loc[: end_idx - 1]

            # Фильтрация по колонке 14 (> 0)
        df[14] = pd.to_numeric(df[14], errors="coerce").fillna(0)
        df = df[df[14] > 0]

        # Выбираем нужные столбцы
        df = df.iloc[:, [1, 2, 3, 4, 5, 14]]
        df.columns = [
            "exchange_product_id",
            "exchange_product_name",
            "delivery_basis_name",
            "volume",
            "total",
            "count",
        ]

        df["volume"] = (
            pd.to_numeric(df["volume"], errors="coerce").fillna(0).astype(int)
        )
        df["total"] = (
            pd.to_numeric(df["total"], errors="coerce").fillna(0.0).astype(float)
        )

        # Добавляем вычисляемые колонки
        df["oil_id"] = df["exchange_product_id"].astype(str).str[:4]
        df["delivery_basis_id"] = df["exchange_product_id"].astype(str).str[4:7]
        df["delivery_type_id"] = df["exchange_product_id"].astype(str).str[-1]

        if self.data["trading_date"]:
            df["date"] = pd.to_datetime(
                self.data["trading_date"], dayfirst=True
            ).tz_localize("UTC")

        total_sum = df["count"].sum()
        total_sum_from_pdf = self.data["total_sum"]
        if int(total_sum) != int(total_sum_from_pdf):
            raise ValueError(
                "Не совпадение сумм количества договоров с xls документом!"
            )
        self.df = df
        return self.df
