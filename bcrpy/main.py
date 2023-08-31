import requests 
import json 
import pickle 
import numpy as np
import pandas

from difflib import get_close_matches
from iteration_utilities import flatten
from itertools import chain

from tqdm import tqdm
from time import sleep

import matplotlib.pyplot as plt 

from bcrpy.anexo import save_dataframe
from bcrpy.anexo import load_dataframe
from bcrpy.hacha import Hacha

import os

from termcolor import colored, cprint
from colorama import just_fix_windows_console
just_fix_windows_console()

class Marco:
    def __init__(self):
        '''Este es el marco principal para almacenar variables y ejecutar metodos para extraer, buscar y manejar datos. 

        Parametros
        ----------
        metadata: pandas.DataFrame
            Los metadatos de las series estadísticas del BRCPData, los cuales pueden ser reducidos con el metodo refine_metadata de esta `class`. 
        data: pandas.DataFrame
            Los datos extraidos del BRCPData de acuerdo a la informacion declarada en las variables constructoras (vea metodo `parameters()`) con el metodo `GET()` de esta clase.  
        codigos : list(str)
            lista de codigos de series en interes para usar con los metodos de esta `class`. 
        formato : str
            formato para extraer / procesar datos (predeterminado: json)
        fechaini : str
            fecha de inicio para la(s) serie(s) seleccionada(s) en mes año (A) y mes (M) (formato AAAA-M)
        fechafin : str
            fecha de final para la(s) serie(s) seleccionada(s) en mes año (A) y mes (M) (formato AAAA-M)
        idioma : str
            idioma seleccionado (predeterminado: ing) otra opcion es 'esp'
        '''
        self.metadata = pandas.DataFrame([])
        self.data = pandas.DataFrame([])
        self.codigos = ['PN01288PM','PN01289PM']
        self.formato = 'json'
        self.fechaini = '2010-1'
        self.fechafin = '2016-9'
        self.idioma = 'ing'

    def parameters(self):
        '''Declara el estado actual de todas las variables constructoras de la clase Marco. 
        '''
        
        decoration = colored("Estado actual de parametros constructores del objeto:", "green")

        def cyan(text): return colored(text, "cyan")

        text = f'''
{cyan('.metadata')} = {'<vacio>' if len(self.metadata)==0 else str(type(self.metadata))+' size: '+str(self.metadata.shape)}
{cyan('.codigos')} = {self.codigos}
{cyan('.formato')} = {self.formato}
{cyan('.fechaini')} = {self.fechaini}
{cyan('.fechafin')} = {self.fechafin}
{cyan('.idioma')} = {self.idioma}
'''

        print(decoration)
        print(text)


    def get_metadata(self, filename='metadata.csv'): 
        '''Extrae todos los metadatos de BCRPData. 
        
        Parametros
        ----------
        filename : str
            Nombre del archivo para guardar todos los metadatos extraidos como un archivo .csv (predeterminado: 'metadata.csv'). Si se desea no guardar un archivo, cambiar a filename=''
        '''
        # SYSTEM DOWN --- BCRP Metadata emptied
        # self.metadata = pandas.read_csv(
        #     'https://estadisticas.bcrp.gob.pe/estadisticas/series/metadata', delimiter=';', encoding='latin-1'
        #     )
        
        # BACKUP vv
        url = 'https://github.com/andrewrgarcia/bcrpy/raw/main/metadatos'
        self.metadata = requests.get(url).content
        self.metadata = pickle.loads(self.metadata)
        
        if filename[-3:] == 'csv':
            self.metadata.to_csv(filename,sep=";",index=False, index_label=False)

    def load_metadata(self,filename='metadata.csv'):
        '''Carga los metadatos guardados como archivo .csv a Python.

        Parametros
        ----------
        filename : str
            Nombre del archivo .csv del cual cargar los metadatos a Python.
        '''

        if filename[-3:] == 'csv':
            self.metadata = pandas.read_csv(filename, delimiter=';')

    def save_metadata(self,filename='metadata_new.csv'):
        '''Guarda los metadatos de self.metadata como archivo .csv

        Parametros
        ----------
        filename : str
            Nombre para el archivo .csv (predeterminado = 'metadata_new.csv')
        '''
        if filename[-3:] == 'csv':
            self.metadata.to_csv(filename,sep=";",index=False, index_label=False)

        
    def query(self,codigo='PD39793AM'):
        '''Consulta (query) de codigo de serie, impresa en formato json. 

        Parametros
        ----------
        codigo : str
            Nombre de codigo de series a consultar
        '''
        self.get_metadata() if len(self.metadata) == 0 else None
        df = self.metadata

        # print('corriendo query para {}...\n'.format(codigo))
        print(colored('corriendo query para {}...\n'.format(codigo), "green"))

        index = df.index[df.iloc[:,0] == codigo].tolist()
        # print('{} es indice {} en metadatos'.format(codigo, index[0]))
        # print(colored(codigo, "blue",attrs=["bold"]),end=" ")
        cprint(codigo, "white", "on_green",end=" ")

        print('es indice {} en metadatos'.format(index[0]))

        dict = self.metadata.loc[index].to_dict()
        for i in dict.keys():
            dict[i] = dict[i][index[0]]
        dict.pop("Unnamed: 13" ) if "Unnamed: 13" in dict.keys() else None

        jsondata = json.dumps(dict,indent = 8,ensure_ascii=False)
        print(jsondata)
        return jsondata
    
    def query_dict(self,codigo='PD39793AM'):

        self.get_metadata() if len(self.metadata) == 0 else None
        df = self.metadata

        # print('corriendo query para {}...\n'.format(codigo))

        index = df.index[df.iloc[:,0] == codigo].tolist()
        # print('{} es indice {} en metadatos'.format(codigo, index[0]))

        dict = self.metadata.loc[index].to_dict()
        for i in dict.keys():
            dict[i] = dict[i][index[0]]
        dict.pop("Unnamed: 13" ) if "Unnamed: 13" in dict.keys() else None

        return dict
   
    def wordsearch(self,keyword='economia',cutoff=0.65,columnas='all'):
        '''Realiza una búsqueda difusa de palabras clave (keyword) en los metadatos de BCRPData. Regresa una tabla de 
        datos en formato `pandas.DataFrame` de los metadatos asociados con aquella palabra. 

        Parametros
        ----------
        keyword : str
            Palabra clave para reducir los metadatos
        cutoff : float
            Este es la metrica de similitud de palabras (predeterminado=0.65). Un cutoff de 1.00 solo regresara metadatos que contienen palabras que coinciden con la palabra clave al 100%.
        columnas : str
            Indices de columnas de los metadatos seleccionados para correr el metodo. Predeterminado='all' corre el metodo en todas las columnas. Seleccion por indice: e.g. [0,2,4] busca en la primera, tercera, y quinta columna. 
        '''
        
        print(f'\nBusqueda difusa de palabra: `{keyword}`')
        print(f'cutoff (tolerancia) = {cutoff}', end='')
        print('; columnas =', "`"+columnas+"`(todas)" if columnas=='all' else columnas)
        print(colored('corriendo wordsearch...', "green", attrs=["blink"]))

        INDICES = []
        self.get_metadata() if len(self.metadata) == 0 else None
        df= self.metadata

        # placeholder dataframes (so that nothing gets overwritten)
        new_df = df.copy()
        bool_df = df.copy()

        ## CLOSED-FORM LANGUAGE PROCESSING
        def contains_similar_keyword(text, keyword, cutoff=0.8, ):
            '''Split titles into separate words and assess all with fuzzy string matching 
            (True if similar word to keyword is found in titles/sentences)'''
            words = text.split()
            similar_matches = list(chain.from_iterable(
                get_close_matches(keyword, [word], n=1, cutoff=cutoff) for word in words
            ))
            
            return bool(similar_matches)
        
        # Do above for all columns in BCRP metadata
        loop_range = range(14) if columnas == 'all' else columnas
        for k in tqdm(loop_range):
            bool_df.iloc[:, k] = bool_df.iloc[:, k].apply(
                lambda x: contains_similar_keyword(str(x), keyword, cutoff)
            )
            sleep(0.001)
            print()

        # Set remaining columns not matched to False
        False_cols = [i for i in range(14)]
        [False_cols.remove(j) for j in loop_range]
        for col in False_cols:
            bool_df.iloc[:,col].values[:] = False

        # Keep dataframe rows which evaluate ANY of its columns to True
        new_df = new_df[bool_df.any(axis=1)]

        print('\n\n',new_df)
        return new_df

    def refine_metadata(self,filename=False):
        '''Reduce los metadatos en self.metadata a aquellos perteneciendo a los codigos de serie declarados en self.codigos. 

        Parametros
        ----------
        filename : str (opcional)
            Nombre para guardar la informacion de la modificada self.metadata como un archivo .csv 
        '''

        self.get_metadata() if len(self.metadata) == 0 else None
        df= self.metadata

        indices = [ df.index[df.iloc[:,0] == k].tolist()[0] for k in self.codigos ]
        
        self.metadata = self.metadata.loc[indices]

        if filename:
            self.save_metadata(filename)


    def order_columns(self,hacer=True):
        '''sub-metodo para re-ordenar columnas de acuerdo a como fueron definidos en objeto.codigos (vea metodo `GET()` parametro "orden")

        Parametros
        ----------
        hacer : bool
            ordenarlas (True)
        '''
        self.get_metadata() if len(self.metadata) == 0 else None
        df = self.metadata

        user_order = [ '{} - {}'.format(self.query_dict(codigo)["Grupo de serie"],self.query_dict(codigo)["Nombre de serie"]) for codigo in self.codigos]
        code_dict = {user_order[i] : self.codigos[i]  for i in range(len(self.codigos))}
        
        if hacer:
            # print('before',self.data.columns)
            self.data = self.data.reindex(columns=user_order)   
            print('Orden de datos determinados por usuario:')

            # print(self.data)
        else:
            print('Orden de datos predeterminados por BCRPData:')

        for count, value in enumerate(self.data.columns,start=1):
            print('{}\t{}\t{}'.format(count,code_dict[value],value))
        # print(code_dict)

    def GET(self, forget = False, order=True, datetime=True):
        '''Extrae los datos del BCRPData selecionados por las previamente-declaradas variables `objeto.codigos`, `objeto.fechaini`, `objeto.fechafin`, `objeto.formato`, y `objeto.idioma`. 

        Parametros
        ----------
        forget : bool
            Si `True`, se restablecerá el caché y se obtendrán los datos nuevamente incluso si ya existen en el caché.
        order : bool
            Las columnas mantienen el orden declarados por el usuario en `objeto.codigos`  con opcion `order=True` (predeterminado). Cuando `order=False`, las columnas de los datos es la predeterminada por BCRPData. 
        datetime : bool
            Formato de las fechas en el pandas.Dataframe. Predeterminado: `True` convierte fechas con el formato `str(MMM.YYYY)` (ejemplo Apr.2022) de BCRPData a la estructura de datos `Timestamp(YYYY-MM-01)` que es elastico para las graficas visuales y otra manipulacion de datos. `False` mantiene el formato rigido `str(MMM.YYYY)` de BCRPData. 
        '''

        root = 'https://estadisticas.bcrp.gob.pe/estadisticas/series/api'
        format = self.formato 
        code_series = '-'.join(self.codigos)
        period = '{}/{}'.format(self.fechaini,self.fechafin) 
        language = self.idioma

        url = "{}/{}/{}/{}/{}".format(root,code_series,format,period,language)

        print('URL:')
        print(url)

        cache_filename = 'cache.bcrfile'    # manten data en memoria temporal (cache) para no hacer GET redundante

        if  os.path.exists(cache_filename) and not forget:  
            print(colored('Obteniendo información de datos desde la memoria caché',"green", attrs=["blink"]))

            self.data = load_dataframe(cache_filename)

        else:
            print(colored('Obteniendo información con la URL de arriba usando requests.get. Por favor espere...',"green", attrs=["blink"]))
            response = requests.get(url)

            dict  = response.json()

            header = [k['name'] for k in dict['config']['series'] ]
            df = pandas.DataFrame(columns=header) # aqui todavia no se han insertado los datos en las filas


            for j in dict['periods']:
                # print(j['values'])
                df.loc[j['name']] = [float(ij) if ij!='n.d.' else None for ij in j['values'] ]

            if datetime:
                df.index = pandas.to_datetime(df.index)     # convierte fechas a datetime (para facilitar visual acercar y alejar ticks de las graficas)

            self.data = df                                  # almacena datos extraidos de BCRPData en self.data 

            self.order_columns() if order else self.order_columns(False)

            print(url)

            save_dataframe(df,cache_filename)
        
        return self.data
    
    def largeGET(self, codigos=[], chunk_size=100):
        '''Extrae los datos del BCRPData selecionados para cantidades mas grandes de 100 series temporales. 

        Parametros:
        ----------
        chunk_size : int
            Número de series de tiempo para obtener en cada fragmento (por defecto es 100).
        '''
        hacha = Hacha()
        # Divide codigos into chunks
        codigo_chunks = [codigos[i:i + chunk_size] for i in range(0, len(codigos), chunk_size)]

        # Initialize a list to store dataframes
        all_dataframes = []

        # Iterate through codigo_chunks with progress tracking and error handling
        for idx, chunk in enumerate(codigo_chunks):
            try:
                self.codigos = chunk
                df = self.GET(forget=True)
                all_dataframes.append(df)
                print(f"Fragmento {idx + 1}/{len(codigo_chunks)} obtenido exitosamente.")
            except Exception as e:
                print(f"Error en el fragmento {idx + 1}: {e}")

        # Concatenate all dataframes into a single dataframe
        final_dataframe = hacha.une(all_dataframes)
        return final_dataframe


    def plot(self, data, title='', titlesize=9, func='plot'):
        '''Grafica x-y data.

        Parametros
        ----------
        data : pandas.DataFrame
            Data x-y extraida de BCRPData, x es fecha y es cantidad. 
        title : str
            Titulo para grafica
        func : str
            Tipo de grafica. 'plot' es grafica comun, 'semilogy' es grafica con escala logaritmica en y-axis.  
        titlesize : str
            Tamaño de titulo para grafica
        '''
        plt.style.use("seaborn")

        plt.title(title, fontsize=titlesize)
        plt.grid(axis='x')
        eval('plt.{}(data)'.format(func))
        # plt.xticks(data.index, rotation =60)
        plt.tight_layout()
