import os
import requests
import pandas as pd
from pathos.multiprocessing import ProcessPool
from termcolor import colored
import pickle
from bcrpy.utils import save_dataframe, load_dataframe
from bcrpy.hacha import Hacha

class Fetcher:
    def GET(self, forget=False, order=True, datetime=True):
        """Extract data from BCRPData selected by the previously declared variables."""
        root = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
        format = self.formato
        code_series = "-".join(self.codigos)
        period = "{}/{}".format(self.fechaini, self.fechafin)
        language = self.idioma

        url = "{}/{}/{}/{}/{}".format(root, code_series, format, period, language)

        print("URL:")
        print(url)

        cache_filename = "cache.bcrfile"  # Maintain data in memory (cache) to avoid redundant GET requests

        if os.path.exists(cache_filename) and not forget:
            print(colored("Obteniendo información de datos desde la memoria caché", "green", attrs=["blink"]))
            self.data = load_dataframe(cache_filename)
        else:
            print(colored("Obteniendo información con la URL de arriba usando requests.get. Por favor espere...", "green", attrs=["blink"]))
            response = requests.get(url)

            if response.status_code != 200:
                print(f"Error: Unable to fetch data, status code {response.status_code}")
                return pd.DataFrame()

            data = response.json()

            header = [k["name"] for k in data["config"]["series"]]
            df = pd.DataFrame(columns=header)

            for j in data["periods"]:
                df.loc[j["name"]] = [float(ij) if ij != "n.d." else None for ij in j["values"]]

            if datetime:
                df.index = pd.to_datetime(df.index)

            self.data = df

            self.order_columns() if order else self.order_columns(False)

            save_dataframe(df, cache_filename)

        return self.data

    def get_data_for_chunk(self, chunk):
        """Helper function for largeGET; Get data for a single chunk."""
        self.codigos = chunk
        df = self.GET(forget=True)
        df.columns = [f"{col}, codigo no. {chunk[idx]}" for idx, col in enumerate(df.columns)]
        return df

    def largeGET(self, codigos=[], chunk_size=100, turbo=True, nucleos=4):
        """Extract data from BCRPData for more than 100 time series."""
        hacha = Hacha()
        codigo_chunks = [codigos[i:i + chunk_size] for i in range(0, len(codigos), chunk_size)]
        all_chunks = []

        if turbo:
            with ProcessPool(processes=nucleos) as pool:
                results = pool.map(self.get_data_for_chunk, codigo_chunks)
                all_chunks.extend(results)
        else:
            for idx, chunk in enumerate(codigo_chunks):
                try:
                    data_chunk = self.get_data_for_chunk(chunk)
                    all_chunks.append(data_chunk)
                    print(f"Fragmento {idx + 1}/{len(codigo_chunks)} obtenido exitosamente.")
                except Exception as e:
                    print(f"Error en el fragmento {idx + 1}: {e}")

        final_dataframe = hacha.une(all_chunks)
        self.codigos = [col.split(", codigo no. ")[-1] for col in final_dataframe.columns] if turbo else codigos

        print(self.codigos)
        print(f"Todos los fragmentos han sido obtenidos! (n={len(self.codigos)})")
        return final_dataframe
