from pathlib import Path

import pandas as pd

from config import OUTPUT_FILE


def save_to_csv(vacancies: list[dict], output_file: Path = OUTPUT_FILE) -> None:
    """Загрузка таблицы вакансий в CSV"""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    dataframe = pd.DataFrame(vacancies)

    if "experience" in dataframe.columns:
        dataframe["experience"] = pd.to_numeric(
            dataframe["experience"], errors="coerce"
        ).astype("Int64")

    for column in ("salary_from", "salary_to"):
        if column in dataframe.columns:
            dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce")

    dataframe.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig",
        float_format="%.15g",
    )
