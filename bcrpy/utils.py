import json
import os
import pickle
import sqlite3
from difflib import get_close_matches
from typing import Optional

import pandas as pd


def scan_columns(df: pd.DataFrame, keyword: str, cutoff: float = 0.65) -> list[str]:
    """
    Fuzzy-search DataFrame column names.
    """

    def contains_similar_keyword(text: str, keyword: str, cutoff: float) -> bool:
        words = str(text).split()
        return any(
            get_close_matches(keyword, [word], n=1, cutoff=cutoff)
            for word in words
        )

    return [
        col for col in df.columns
        if contains_similar_keyword(str(col), keyword, cutoff)
    ]


def save_dataframe(df: pd.DataFrame, filename: str, meta: Optional[dict] = None) -> None:
    """
    Save a DataFrame to CSV, Markdown, or pickle depending on file suffix.
    Also writes a JSON sidecar if meta is provided.
    """
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".csv":
        df.to_csv(filename)
    elif ext == ".md":
        with open(filename, "w", encoding="utf-8") as f:
            f.write(df.to_markdown())
    else:
        with open(filename, "wb") as f:
            pickle.dump(df, f)

    if meta is not None:
        with open(filename + ".meta", "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)


def load_dataframe(filename: str) -> pd.DataFrame:
    """
    Load a DataFrame from CSV or pickle.
    """
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".csv":
        return pd.read_csv(filename)

    with open(filename, "rb") as f:
        return pickle.load(f)


def save_df_as_sql(df: pd.DataFrame, db_name: str, table_name: str = "time_series") -> None:
    """
    Save a DataFrame into SQLite.
    """
    if isinstance(df.index, pd.DatetimeIndex):
        df = df.reset_index().rename(columns={"index": "date"})

    with sqlite3.connect(db_name) as conn:
        df.to_sql(table_name, conn, if_exists="replace", index=False)


def load_from_sqlite(db_name: str, table_name: str = "time_series") -> pd.DataFrame:
    """
    Load a DataFrame from SQLite.
    """
    with sqlite3.connect(db_name) as conn:
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)

    if "date" in df.columns:
        df = df.set_index("date")
        df.index = pd.to_datetime(df.index, errors="coerce")

    return df