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


    def une(self, fragments, axis=1, ignore_index=False):
        """Combina una lista de fragmentos en un solo dataframe.

        Combina una lista de fragmentos en un solo dataframe a lo largo del eje especificado.

        Parametros
        -------------
        fragments : List[pandas.DataFrame]
            Lista de fragmentos (DataFrames) que se combinarán en uno solo.

        axis : {0, 1}, defecto 1
            Eje a lo largo del cual se realizará la concatenación:
            - 0: Para concatenación vertical (a lo largo de las filas).
            - 1: Para concatenación horizontal (a lo largo de las columnas).

        ignore_index : bool, defecto False
            Si es True, no se conservarán los índices originales de los fragmentos y se
            generará un nuevo índice en el dataframe resultante.
        """
        return pandas.concat(fragments,axis=axis,ignore_index=ignore_index)