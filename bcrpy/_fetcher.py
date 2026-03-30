import os
import json
import hashlib
import sqlite3
from typing import List

import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

from bcrpy._http import create_session
from bcrpy.utils import (
    save_dataframe,
    load_dataframe,
    save_df_as_sql,
    load_from_sqlite,
)

BASE_URL = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
CACHE_DIR = ".bcrpy_cache"


class Fetcher:

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.session = create_session()
        os.makedirs(CACHE_DIR, exist_ok=True)

    # ============================================================
    # PUBLIC
    # ============================================================

    def GET(
        self,
        codes: List[str],
        start: str,
        end: str,
        format: str = "json",
        lang: str = "ing",
        forget: bool = False,
        datetime_index: bool = True,
        storage: str = "df",
    ):

        cache_df, cache_sql = self._cache_paths(codes, start, end)

        cached = self._load_cache(cache_df, cache_sql, forget, storage)
        if cached is not None:
            return cached

        url = self._build_url(codes, start, end, format, lang)

        if self.verbose:
            print(f"[GET] {url}")

        data = self._fetch_json(url)

        if not data:
            return pd.DataFrame()

        df = self._json_to_df(data, datetime_index)

        self._save_cache(df, cache_df, cache_sql, storage, codes, start, end, format, lang)

        return df


    def largeGET(
        self,
        codes: List[str],
        start: str,
        end: str,
        format: str = "json",
        lang: str = "ing",
        forget: bool = False,
        chunk_size: int = 100,
        workers: int = 4,
        storage: str = "df",
    ):

        cache_df, cache_sql = self._cache_paths(codes, start, end, large=True)

        cached = self._load_cache(cache_df, cache_sql, forget, storage)
        if cached is not None:
            return cached

        chunks = [codes[i:i + chunk_size] for i in range(0, len(codes), chunk_size)]

        if self.verbose:
            print(f"[largeGET] {len(codes)} series → {len(chunks)} chunks")

        results = []
        errors = []

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [
                executor.submit(self._fetch_chunk, chunk, start, end, format, lang)
                for chunk in chunks
            ]

            for f in as_completed(futures):
                try:
                    results.append(f.result())
                except Exception as e:
                    errors.append(str(e))

        if errors and self.verbose:
            print(f"[WARN] {len(errors)} chunks failed")

        final_df = pd.concat(results, axis=1)

        self._save_cache(final_df, cache_df, cache_sql, storage, codes, start, end, format, lang)

        return final_df

    # ============================================================
    # CORE
    # ============================================================

    def _build_url(self, codes, start, end, format, lang):
        code_series = "-".join(codes)
        period = f"{start}/{end}"
        return f"{BASE_URL}/{code_series}/{format}/{period}/{lang}"


    def _fetch_json(self, url):
        try:
            r = self.session.get(url, timeout=30)

            if r.status_code != 200:
                if self.verbose:
                    print(f"[ERROR] status {r.status_code}")
                return None

            if not r.content:
                return None

            return r.json()

        except Exception as e:
            if self.verbose:
                print(f"[ERROR] request failed: {e}")
            return None


    def _json_to_df(self, data, datetime_index=True):
        header = [k["name"] for k in data["config"]["series"]]

        df = pd.DataFrame(columns=header)

        for p in data["periods"]:
            df.loc[p["name"]] = [
                float(v) if v != "n.d." else None
                for v in p["values"]
            ]

        if datetime_index:
            df.index = pd.to_datetime(df.index, errors="coerce")

        return df


    def _fetch_chunk(self, chunk, start, end, format, lang):
        df = self.GET(
            codes=chunk,
            start=start,
            end=end,
            format=format,
            lang=lang,
            storage="df",
        )

        df.columns = [
            f"{col}, codigo no. {chunk[i]}"
            for i, col in enumerate(df.columns)
        ]

        return df

    # ============================================================
    # CACHE
    # ============================================================

    def _cache_paths(self, codes, start, end, large=False):
        key = hashlib.md5(f"{codes}-{start}-{end}".encode()).hexdigest()
        prefix = "large_cache" if large else "cache"

        return (
            os.path.join(CACHE_DIR, f"{prefix}_{key}.bcrfile"),
            os.path.join(CACHE_DIR, f"{prefix}_{key}.db"),
        )


    def _load_cache(self, df_file, sql_file, forget, storage):

        def load(file, loader):
            if not os.path.exists(file):
                return None

            if forget:
                os.remove(file)
                if os.path.exists(file + ".meta"):
                    os.remove(file + ".meta")
                return None

            if self.verbose:
                print(f"[CACHE] {file}")

            return loader(file)

        if storage == "df":
            return load(df_file, load_dataframe)
        elif storage == "sql":
            return load(sql_file, load_from_sqlite)


    def _save_cache(self, df, df_file, sql_file, storage, codes, start, end, format, lang):

        meta = {
            "codes": codes,
            "start": start,
            "end": end,
            "format": format,
            "lang": lang,
        }

        if storage == "df":
            save_dataframe(df, df_file, meta=meta)
        else:
            save_df_as_sql(df, sql_file, "time_series")

            with open(sql_file + ".meta", "w") as f:
                json.dump(meta, f, indent=2)

    # ============================================================
    # SQLITE
    # ============================================================

    def save_to_sqlite(self, data, header, db_name="cache.db"):
        with sqlite3.connect(db_name) as conn:

            conn.execute("DROP TABLE IF EXISTS time_series")

            cols = ["date TEXT"] + [f'"{col}" REAL' for col in header]
            conn.execute(f"CREATE TABLE time_series ({', '.join(cols)})")

            insert = f"INSERT INTO time_series VALUES ({','.join(['?']*(len(header)+1))})"

            for p in data["periods"]:
                row = [p["name"]] + [
                    float(v) if v != "n.d." else None
                    for v in p["values"]
                ]
                conn.execute(insert, row)

            conn.commit()