import pandas

class Hacha:
    def __init__(self):
        """Inicializador de la clase Hacha.

        Esta clase está diseñada para dividir y combinar dataframes en fragmentos más pequeños para un procesamiento eficiente.

        Parametros
        ---------------
        fragments : list
            Una lista para almacenar fragmentos de dataframes.
        """
        self.fragments = []

    def parte(self, dataframe, chunk_size=100):
        """Divide un dataframe en una lista de fragmentos del tamaño especificado.

        Parametros
        --------------
        dataframe : pandas.DataFrame
            DataFrame para dividir.
        chunk_size : int
            Tamaño de cada fragmento (por defecto es 100).
        """
        self.fragments = [dataframe[i:i + chunk_size] for i in range(0, len(dataframe), chunk_size)]
        return self.fragments


    def une(self, fragments):
        """Combina una lista de fragmentos en un solo dataframe.

        Parametros:
        ----------
        fragments : List[pandas.DataFrame]
            Lista de fragmentos para combinar.

        """
        return pandas.concat(fragments, ignore_index=True)