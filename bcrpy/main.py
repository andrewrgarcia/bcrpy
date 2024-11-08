import pandas as pd
import requests
import json
import pickle
from difflib import get_close_matches
from termcolor import colored, cprint
from colorama import just_fix_windows_console
from bcrpy.utils import save_dataframe, load_dataframe
from ._fetcher import Fetcher  
from ._metadata import MetadataHandler

just_fix_windows_console()

class Marco(Fetcher, MetadataHandler):
    def __init__(self):
        """
        Main framework for storing variables and executing methods to extract, search, and handle data.
        
        Attributes
        ----------
        metadata : pd.DataFrame
            DataFrame to store metadata of statistical series from BCRPData.
        data : pd.DataFrame
            DataFrame to store extracted data from BCRPData.
        codes : list of str
            List of series codes of interest.
        start : str
            Start date for the selected series in year-month format (default: '2010-1').
        end : str
            End date for the selected series in year-month format (default: '2016-9').
        format : str
            Format for extracting/processing data (default: 'json').
        lang : str
            Selected language (default: 'ing' for English). Other option is 'esp' for Spanish.
        """
        self.metadata: pd.DataFrame = pd.DataFrame()
        self.data: pd.DataFrame = pd.DataFrame()
        self.codes: list[str] = ["PN01288PM", "PN01289PM"]
        self.start: str = "2010-1"
        self.end: str = "2016-9"
        self.format: str = "json"
        self.lang: str = "ing"


    def parameters(self):
        """Declare the current state of all constructor variables of the Marco class."""
        def cyan(text):
            return colored(text, "cyan")

        text = f"""
{cyan('.metadata')} = {'<vacio>' if self.metadata.empty else str(type(self.metadata))+' size: '+str(self.metadata.shape)}
{cyan('.codes')} = {self.codes}
{cyan('.format')} = {self.format}
{cyan('.start')} = {self.start}
{cyan('.end')} = {self.end}
{cyan('.lang')} = {self.lang}
"""
        print(colored("Estado actual de parametros constructores del objeto:", "green"))
        print(text)

    def query(self, codigo="PD39793AM"):
        """Query series code, printed in JSON format."""
        if self.metadata.empty:
            self.get_metadata()

        print(colored("corriendo query para {}...\n".format(codigo), "green"))
        
        index = self.metadata.index[self.metadata.iloc[:, 0] == codigo].tolist()
        cprint(codigo, "white", "on_green", end=" ")
        print(f"es indice {index[0]} en metadatos")
        data_dict = self.metadata.loc[index].to_dict()
        for key in data_dict:
            data_dict[key] = data_dict[key][index[0]]
        data_dict.pop("Unnamed: 13", None)
        jsondata = json.dumps(data_dict, indent=8, ensure_ascii=False)
        print(jsondata)
        return jsondata

    def query_dict(self, codigo="PD39793AM"):
        if self.metadata.empty:
            self.get_metadata()
        index = self.metadata.index[self.metadata.iloc[:, 0] == codigo].tolist()
        data_dict = self.metadata.loc[index].to_dict()
        for key in data_dict:
            data_dict[key] = data_dict[key][index[0]]
        data_dict.pop("Unnamed: 13", None)
        return data_dict

    def wordsearch(self, keyword="economia", cutoff=0.65, columnas="all"):
        """
        Perform a fuzzy search for keywords in the BCRPData metadata.
        
        Parameters
        ----------
        keyword : str
            Keyword to search for in the metadata.
        cutoff : float
            Similarity cutoff for the fuzzy matching (default is 0.65).
        columnas : str or list of int
            Columns to search in. If 'all', search in all columns (default is 'all').
        """
        print(f"\nBusqueda difusa de palabra: `{keyword}`")
        print(f"cutoff (tolerancia) = {cutoff}; columnas = {'`all`(todas)' if columnas == 'all' else columnas}")
        
        if self.metadata.empty:
            self.get_metadata()
        
        def contains_similar_keyword(text, keyword, cutoff=0.8):
            words = text.split()
            return any(get_close_matches(keyword, [word], n=1, cutoff=cutoff) for word in words)
        
        if columnas == "all":
            bool_df = self.metadata.apply(lambda col: col.apply(lambda x: contains_similar_keyword(str(x), keyword, cutoff)))
        else:
            bool_df = self.metadata.iloc[:, columnas].apply(lambda col: col.apply(lambda x: contains_similar_keyword(str(x), keyword, cutoff)))
        
        new_df = self.metadata[bool_df.any(axis=1)]
        print("\n\n", new_df)
        return new_df


    def order_columns(self, hacer=True):
        """Sub-method to reorder columns according to how they were defined in objeto.codes."""
        if self.metadata.empty:
            self.get_metadata()
        user_order = [f"{self.query_dict(codigo)['Grupo de serie']} - {self.query_dict(codigo)['Nombre de serie']}" for codigo in self.codes]
        code_dict = {user_order[i]: self.codes[i] for i in range(len(self.codes))}

        if hacer:
            self.data = self.data.reindex(columns=user_order)
            print("Orden de datos determinados por usuario:")
        else:
            print("Orden de datos predeterminados por BCRPData:")

        for count, value in enumerate(self.data.columns, start=1):
            print(f"{count}\t{code_dict[value]}\t{value}")

