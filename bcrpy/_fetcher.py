import os
import requests
import pandas as pd
from pathos.multiprocessing import ProcessPool
from termcolor import colored
import pickle
from bcrpy.utils import save_dataframe, load_dataframe
from bcrpy.hacha import Hacha

class Fetcher:
    def GET(self, forget=False, order=True, datetime=True, check_codes=False):
        """
        Extrae datos de BCRPData seleccionados por las variables declaradas previamente.

        Parameters
        ------------
        forget : bool
            Si True, se restablecerá el caché y se obtendrán los datos nuevamente incluso si ya existen en el caché.
        order : bool
            Las columnas mantienen el orden declarado por el usuario en objeto.codigos con opción order=True (predeterminado).
            Cuando order=False, las columnas de los datos es la predeterminada por BCRPData.
        datetime : bool
            Formato de las fechas en el pandas.DataFrame. Predeterminado: True convierte fechas con el formato str(MMM.YYYY) 
            (ejemplo Apr.2022) de BCRPData a la estructura de datos Timestamp(YYYY-MM-01) que es elástico para las gráficas 
            visuales y otras manipulaciones de datos. False mantiene el formato rígido str(MMM.YYYY) de BCRPData.
        check_codes : bool
            Si True, los códigos de series serán validados contra los metadatos antes de realizar la solicitud GET (predeterminado: False).
        """

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
            code_series = "-".join(self.codigos)

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

    def largeGET(self, codigos=[], chunk_size=100, turbo=True, nucleos=4, check_codes=False):
        """
        Extrae los datos del BCRPData seleccionados para cantidades mayores a 100 series temporales.

        Parameters
        ----------
        codigos : list, optional
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
            
        Notas
        -----
        - En el modo turbo, se utiliza un `ProcessPool` para distribuir la extracción de datos en múltiples procesos.
        - Cuando el modo turbo está desactivado, la extracción se realiza secuencialmente.
        - Se utiliza la clase `Hacha` para combinar los datos extraídos de los diferentes fragmentos en un solo DataFrame.
        """

        if check_codes:
            valid_codes = self.check_metadata_codes()
            if valid_codes is None:
                print("No valid codes found. Skipping the large GET request.")
                return pd.DataFrame()
        else:
            valid_codes = codigos

        hacha = Hacha()
        codigo_chunks = [valid_codes[i:i + chunk_size] for i in range(0, len(valid_codes), chunk_size)]
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
        self.codigos = [col.split(", codigo no. ")[-1] for col in final_dataframe.columns] if turbo else valid_codes

        print(self.codigos)
        print(f"Todos los fragmentos han sido obtenidos! (n={len(self.codigos)})")
        return final_dataframe


    def check_metadata_codes(self):
        """
        Check the self.codigos list against the first column of the metadata.
        Notifies the user if codes are not found in metadata or if there are no valid codes.
        """
        if self.metadata.empty:
            self.get_metadata()

        if not isinstance(self.metadata, pd.DataFrame):
            print("Error: metadata is not loaded or not a DataFrame.")
            return None  # Return None if metadata is not available

        metadata_codes = self.metadata.iloc[:, 0].tolist()  # Extract codes from the first column
        valid_codes = [code for code in self.codigos if code in metadata_codes]
        invalid_codes = [code for code in self.codigos if code not in metadata_codes]

        if invalid_codes:
            print(f"Warning: The following codes were not found in metadata and will be ignored: {invalid_codes}")

        if not valid_codes:
            print("No valid codes found in metadata. Skipping the GET request.")
            return None

        return valid_codes