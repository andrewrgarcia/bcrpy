import pickle
import sqlite3
import os

import requests
from termcolor import colored

import pandas as pd
from pathos.multiprocessing import ProcessPool

from bcrpy.utils import save_dataframe, load_dataframe
from bcrpy.hacha import Axe

class Fetcher:
    def GET(self, codes=[], forget=False, order=True, datetime=True, check_codes=False, storage='df'):
        """
        Extrae datos de BCRPData seleccionados por las variables declaradas previamente.

        Parameters
        ------------
        codes : list, optional
            Lista de códigos de series de datos a extraer. Si se proporciona, esta lista reemplaza 
            la lista predeterminada en `self.codes` y se utiliza para la solicitud GET. Si es None 
            (predeterminado), se utilizará la lista de `self.codes` existente.
        forget : bool
            Si True, se restablecerá el caché y se obtendrán los datos nuevamente incluso si ya existen en el caché.
        order : bool
            Las columnas mantienen el orden declarado por el usuario en objeto.codes con opción order=True (predeterminado).
            Cuando order=False, las columnas de los datos es la predeterminada por BCRPData.
        datetime : bool
            Formato de las fechas en el pandas.DataFrame. Predeterminado: True convierte fechas con el formato str(MMM.YYYY) 
            (ejemplo Apr.2022) de BCRPData a la estructura de datos Timestamp(YYYY-MM-01) que es elástico para las gráficas 
            visuales y otras manipulaciones de datos. False mantiene el formato rígido str(MMM.YYYY) de BCRPData.
        check_codes : bool
            Si True, los códigos de series serán validados contra los metadatos antes de realizar la solicitud GET (predeterminado: False).
        storage : str, optional
            Almacenamiento de datos: 'df' (DataFrame) o 'sql' (SQLite). Controla el formato en el que se almacena y devuelve la información.
        """
        if bool(len(codes)):
            self.codes = codes

        root = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
        format = self.formato
        period = "{}/{}".format(self.fechaini, self.fechafin)
        language = self.idioma

        if check_codes:
            valid_codes = self.check_metadata_codes()
            if valid_codes is None:
                return pd.DataFrame()
            code_series = "-".join(valid_codes)
        else:
            code_series = "-".join(self.codes)

        url = f"{root}/{code_series}/{format}/{period}/{language}"
        print(f"URL: {url}")

        cache_filename = "cache.bcrfile"
        sql_cache_filename = "cache.db"




        # Handle cache based on the chosen storage format
        if storage == 'df':
            # DataFrame Cache Logic
            if os.path.exists(cache_filename) and not forget:
                print(colored("Obteniendo información de datos desde la memoria caché (DataFrame)", "green", attrs=["blink"]))
                self.data = load_dataframe(cache_filename)
                return self.data
            elif forget and os.path.exists(cache_filename):
                os.remove(cache_filename)  # Clear cache if forget=True

        elif storage == 'sql':
            # SQLite Cache Logic
            if os.path.exists(sql_cache_filename) and not forget:
                print(colored("Obteniendo información de datos desde la memoria caché (SQLite)", "green", attrs=["blink"]))
                return self.load_from_sqlite(sql_cache_filename)
            elif forget and os.path.exists(sql_cache_filename):
                os.remove(sql_cache_filename)  # Clear cache if forget=True

        
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

            for j in data["periods"]:
                df.loc[j["name"]] = [float(ij) if ij != "n.d." else None for ij in j["values"]]

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

            return self.load_from_sqlite(sql_cache_filename)







    def get_data_for_chunk(self, chunk):
        """Helper function for largeGET; Get data for a single chunk."""
        self.codes = chunk
        df = self.GET(forget=True, storage='df')  # Use DataFrame as intermediate storage
        df.columns = [f"{col}, codigo no. {chunk[idx]}" for idx, col in enumerate(df.columns)]
        return df

    def largeGET(self, codes=[], chunk_size=100, turbo=True, nucleos=4, check_codes=False, storage='df'):
        """
        Extrae los datos del BCRPData seleccionados para cantidades mayores a 100 series temporales.

        Parameters
        ----------
        codes : list, optional
            Lista de códigos de series temporales a obtener y/o obtenidos [para el caso de turbo (cómputo paralelo)].
            El valor predeterminado es una lista vacía.
        chunk_size : int, optional
            Número de series temporales para obtener en cada fragmento. El valor predeterminado es 100.
        turbo : bool, optional
            Indica si se debe utilizar el modo "turbo" para la extracción paralela. El valor predeterminado es True.
        nucleos : int, optional
            Número de núcleos de procesador ("cores") a utilizar en el modo "turbo". El valor predeterminado es 4.
        check_codes : bool, optional
            Si True, valida los códigos de las series temporales contra los metadatos antes de realizar la solicitud. El valor predeterminado es False.
        storage : str, optional
        Almacenamiento de datos: 'df' (DataFrame) o 'sql' (SQLite). Controla el formato en el que se almacena y devuelve la información.        
        
        Notas
        -----
        - En el modo turbo, se utiliza un `ProcessPool` para distribuir la extracción de datos en múltiples procesos.
        - Cuando el modo turbo está desactivado, la extracción se realiza secuencialmente.
        - Se utiliza la clase `Axe` para combinar los datos extraídos de los diferentes fragmentos en un solo DataFrame.
        """

        if check_codes:
            valid_codes = self.check_metadata_codes()
            if valid_codes is None:
                print("No valid codes found. Skipping the large GET request.")
                return pd.DataFrame() if storage == 'df' else None
        else:
            valid_codes = codes

        axe = Axe()
        codigo_chunks = [valid_codes[i:i + chunk_size] for i in range(0, len(valid_codes), chunk_size)]
        sql_cache_filename = "large_cache.db"

        # Reset SQLite database if storage is 'sql'
        if storage == 'sql':
            with sqlite3.connect(sql_cache_filename) as conn:
                conn.execute("DROP TABLE IF EXISTS time_series;")  # Clear previous data if it exists

        all_chunks = []

        # Process chunks
        if turbo:
            with ProcessPool(processes=nucleos) as pool:
                results = pool.map(self.get_data_for_chunk, codigo_chunks)
                for df_chunk in results:
                    if storage == 'df':
                        all_chunks.append(df_chunk)
                    elif storage == 'sql':
                        self.save_chunk_to_sqlite(df_chunk, sql_cache_filename)
        else:
            for idx, chunk in enumerate(codigo_chunks):
                try:
                    data_chunk = self.get_data_for_chunk(chunk)
                    if storage == 'df':
                        all_chunks.append(data_chunk)
                    elif storage == 'sql':
                        self.save_chunk_to_sqlite(data_chunk, sql_cache_filename)
                    print(f"Fragmento {idx + 1}/{len(codigo_chunks)} obtenido exitosamente.")
                except Exception as e:
                    print(f"Error en el fragmento {idx + 1}: {e}")

        # Combine all chunks into a single DataFrame if storage is 'df'
        if storage == 'df':
            final_dataframe = axe.forge(all_chunks)
            save_dataframe(final_dataframe, "large_cache.bcrfile")
            self.codes = [col.split(", codigo no. ")[-1] for col in final_dataframe.columns] if turbo else valid_codes
            print(self.codes)
            print(f"Todos los fragmentos han sido obtenidos! (n={len(self.codes)})")

            return final_dataframe
        
        elif storage == 'sql':
            print(self.codes)
            print(f"Todos los fragmentos han sido obtenidos! (n={len(self.codes)})")

            return self.load_from_sqlite(sql_cache_filename)



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


    def save_chunk_to_sqlite(self, df, db_name="large_cache.db"):
        """Save a DataFrame chunk to the SQLite database."""
        with sqlite3.connect(db_name) as conn:
            # Ensure the table exists before adding columns
            conn.execute("CREATE TABLE IF NOT EXISTS time_series (date TEXT PRIMARY KEY)")
            
            # Check existing columns and add only new ones
            existing_columns = [row[1] for row in conn.execute("PRAGMA table_info(time_series);").fetchall()]
            for col in df.columns:
                if col not in existing_columns:
                    conn.execute(f"ALTER TABLE time_series ADD COLUMN \"{col}\" REAL")
            
            # Insert DataFrame rows into the SQLite table
            df.to_sql("time_series", conn, if_exists="append", index=False)


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



    def load_from_sqlite(self, db_name="cache.db"):
        """Load data from the SQLite cache and return as a DataFrame."""
        with sqlite3.connect(db_name) as conn:
            df = pd.read_sql("SELECT * FROM time_series", conn, index_col="date")
            print("Data loaded from SQLite:", df.head())  # Debug: print first few rows to verify loading
            return df
