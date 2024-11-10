import sqlite3
import os

import requests
from termcolor import colored

import pandas as pd
from pathos.multiprocessing import ProcessPool

from bcrpy.utils import save_dataframe, load_dataframe, save_df_as_sql, load_from_sqlite
from bcrpy.hacha import Axe

class Fetcher:
    def GET(self, codes=[], start=None, end=None, forget=False, order=True, datetime=True, check_codes=False, storage='df'):
        """
        Extracts selected data from BCRPData based on previously declared variables.

        Parameters
        ----------
        codes : list, optional
            List of data series codes to extract. If provided, this list replaces the default list in `self.codes` and is used for the GET request. If None (default), the existing `self.codes` list will be used.
        
        start : str, optional
            Start date in 'YYYY-M' format for the data series. If provided, this date replaces `self.start` defined in the constructor, only for this request. If not provided, `self.start` is used.
        
        end : str, optional
            End date in 'YYYY-M' format for the data series. If provided, this date replaces `self.end` defined in the constructor, only for this request. If not provided, `self.end` is used.
        
        forget : bool
            If True, resets the cache, retrieving data again even if it already exists in the cache.
        
        order : bool
            Maintains column order declared by the user in `object.codes` with order=True (default). When order=False, columns follow BCRPData's default order.
        
        datetime : bool
            Format of dates in the pandas.DataFrame. Default: True converts dates from BCRPData's str(MMM.YYYY) format (e.g., Apr.2022) to Timestamp(YYYY-MM-01), allowing for flexible visual graphs and other data manipulations. False keeps the original str(MMM.YYYY) format from BCRPData.
        
        check_codes : bool
            If True, series codes are validated against metadata before making the GET request (default: False).
        
        storage : str, optional
            Data storage format: 'df' (DataFrame) or 'sql' (SQLite). Controls the format in which the information is stored and returned.
        """
        if bool(len(codes)):
            self.codes = codes
        if start is not None:
            self.start = start
        if end is not None:
            self.end = end

        root = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
        format = self.format
        period = "{}/{}".format(self.start, self.end)
        language = self.lang

        if check_codes:
            valid_codes = self.check_metadata_codes()
            if valid_codes is None:
                return pd.DataFrame()
            code_series = "-".join(valid_codes)
        else:
            code_series = "-".join(self.codes)

        cache_filename = "cache.bcrfile"
        sql_cache_filename = "cache.db"

        if (data := self.load_from_cache(cache_filename, sql_cache_filename, forget, storage)) is not None:
            return data 
        
        url = f"{root}/{code_series}/{format}/{period}/{language}"
        print(f"URL: {url}")

        # Fetching from URL as cache is either empty or `forget` is True
        print(colored("Obteniendo información con la URL de arriba usando requests.get. Por favor espere...", "green", attrs=["blink"]))
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Error: Unable to fetch data, status code {response.status_code}")
            return pd.DataFrame()

        data = response.json()

        header = [k["name"] for k in data["config"]["series"]]

        if storage == 'df':
            # Convert JSON data to DataFrame and save as cache
            df = pd.DataFrame(columns=header)

            for period in data["periods"]:
                df.loc[period["name"]] = [float(value) if value != "n.d." else None for value in period["values"]]

            if datetime:
                df.index = pd.to_datetime(df.index)

            self.data = df
            self.order_columns() if order else self.order_columns(False)
            save_dataframe(df, cache_filename)

            return self.data
        
        elif storage == 'sql':
            # Save data directly to SQLite and return a confirmation message
            self.save_to_sqlite(data, header, sql_cache_filename)
            print(colored("Data saved to SQLite database cache.", "green"))

            return load_from_sqlite(sql_cache_filename)
        

    def largeGET(self, codes=[], start=None, end=None, forget=True, chunk_size=100, turbo=True, nucleos=4, check_codes=False, storage='df'):
        """
        Extracts selected BCRPData series when the quantity exceeds 100 time series.

        Parameters
        -------------
        codes : list, optional
            List of time series codes to retrieve, used in turbo mode (parallel computation). Default is an empty list.
        
        start : str, optional
            Start date in 'YYYY-M' format for the data series. If provided, this date replaces `self.start` defined in the constructor, only for this request. If not provided, `self.start` is used.
        
        end : str, optional
            End date in 'YYYY-M' format for the data series. If provided, this date replaces `self.end` defined in the constructor, only for this request. If not provided, `self.end` is used.
        
        chunk_size : int, optional
            Number of time series to retrieve per chunk. Default is 100.
        
        turbo : bool, optional
            Indicates whether to use "turbo" mode for parallel extraction. Default is True.
        
        nucleos : int, optional
            Number of processor cores to use in "turbo" mode. Default is 4.
        
        check_codes : bool, optional
            If True, validates the time series codes against metadata before making the request. Default is False.
        
        storage : str, optional
            Data storage format: `df` (DataFrame) or `sql` (SQLite). Controls the format in which the data is stored and returned.
        """
        if start is not None:
            self.start = start
        if end is not None:
            self.end = end

        if check_codes:
            valid_codes = self.check_metadata_codes()
            if valid_codes is None:
                print("No valid codes found. Skipping the large GET request.")
                return pd.DataFrame() if storage == 'df' else None
        else:
            valid_codes = codes

        cache_filename = "large_cache.bcrfile"
        sql_cache_filename = "large_cache.db"

        if (data := self.load_from_cache(cache_filename, sql_cache_filename, forget, storage)) is not None:
            return data
        
        axe = Axe()
        codigo_chunks = [valid_codes[i:i + chunk_size] for i in range(0, len(valid_codes), chunk_size)]

        all_chunks = []

        # Process chunks
        if turbo:
            with ProcessPool(processes=nucleos) as pool:
                results = pool.map(self.get_data_for_chunk, codigo_chunks)
                for df_chunk in results:
                    all_chunks.append(df_chunk)

        else:
            for idx, chunk in enumerate(codigo_chunks):
                try:
                    data_chunk = self.get_data_for_chunk(chunk)
                    all_chunks.append(data_chunk)
                    print(f"Fragmento {idx + 1}/{len(codigo_chunks)} obtenido exitosamente.")
                except Exception as e:
                    print(f"Error en el fragmento {idx + 1}: {e}")

        final_dataframe = axe.forge(all_chunks)
        self.codes = [col.split(", codigo no. ")[-1] for col in final_dataframe.columns] if turbo else valid_codes
        print(self.codes)
        print(f"Todos los fragmentos han sido obtenidos! (n={len(self.codes)})")

        if storage == 'df':
            save_dataframe(final_dataframe, cache_filename)
        else: 
            print(final_dataframe)
            save_df_as_sql(final_dataframe, sql_cache_filename, 'time_series')

        return final_dataframe

    def get_data_for_chunk(self, chunk):
        """Helper function for largeGET; Get data for a single chunk."""
        self.codes = chunk
        df = self.GET(forget=True, storage='df')  # Use DataFrame as intermediate storage
        df.columns = [f"{col}, codigo no. {chunk[idx]}" for idx, col in enumerate(df.columns)]
        return df

    def load_from_cache(self, df_cache_filename, sql_cache_filename, forget, storage):
        """
        Helper method for GET and largeGET. Loads data from cache based on the specified storage format. 
        Checks if the cache file exists and either loads data from it or clears it based on the `forget` parameter.
        """
        def handle_cache_loading(filename, load_structure, text):
            # Cache Logic
            if os.path.exists(filename) and not forget:
                print(colored(f"Obteniendo información de datos desde la memoria caché ({text})", "green", attrs=["blink"]))
                self.data = load_structure(filename)
                return self.data
            elif forget and os.path.exists(filename):
                os.remove(filename)  # Clear cache if forget=True
                return None

        # Handle cache based on the chosen storage format
        if storage == 'df':
            return handle_cache_loading(df_cache_filename, load_dataframe, "DataFrame")

        elif storage == 'sql':
            return handle_cache_loading(sql_cache_filename, load_from_sqlite, "SQLite")
    

    def check_metadata_codes(self):
        """
        Check the self.codes list against the first column of the metadata.
        Notifies the user if codes are not found in metadata or if there are no valid codes.
        """
        if self.metadata.empty:
            self.get_metadata()

        if not isinstance(self.metadata, pd.DataFrame):
            print("Error: metadata is not loaded or not a DataFrame.")
            return None  # Return None if metadata is not available

        metadata_codes = self.metadata.iloc[:, 0].tolist()  # Extract codes from the first column
        valid_codes = [code for code in self.codes if code in metadata_codes]
        invalid_codes = [code for code in self.codes if code not in metadata_codes]

        if invalid_codes:
            print(f"Warning: The following codes were not found in metadata and will be ignored: {invalid_codes}")

        if not valid_codes:
            print("No valid codes found in metadata. Skipping the GET request.")
            return None

        return valid_codes

    def save_to_sqlite(self, data, header, db_name="cache.db"):
        """Save JSON data directly to an SQLite database in a structured format."""
        with sqlite3.connect(db_name) as conn:
            # Drop table if exists
            conn.execute("DROP TABLE IF EXISTS time_series;")
            
            # Create table with columns
            columns_definitions = ["date TEXT"] + [f'"{col}" REAL' for col in header]
            create_table_query = "CREATE TABLE time_series (" + ", ".join(columns_definitions) + ");"
            
            # Execute the create table query
            conn.execute(create_table_query)

            # Prepare the insert query using parameter placeholders
            column_names = ["date"] + [f'"{col}"' for col in header]
            insert_query = "INSERT INTO time_series (" + ", ".join(column_names) + ") VALUES (" + ", ".join(["?"] * len(column_names)) + ");"
            
            # Insert data row by row
            for period in data["periods"]:
                date = period["name"]
                values = [float(val) if val != "n.d." else None for val in period["values"]]
                conn.execute(insert_query, [date] + values)

            conn.commit()