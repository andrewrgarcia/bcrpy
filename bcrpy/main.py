import requests 
import json 

import numpy as np
import pandas

from difflib import get_close_matches
from iteration_utilities import flatten

from tqdm import tqdm
from time import sleep

import matplotlib.pyplot as plt 
from bcrpy.anexo import Levenshtein


class Marco:
    def __init__(self):
        '''Este es el marco principal para almacenar variables y ejecutar metodos para extraer, buscar y manejar datos. 

        Parametros
        ----------
        metadata: pandas.DataFrame
            Los metadatos de las series estadísticas del BRCPData, los cuales pueden ser reducidos con el metodo ref_metadata de esta `class`. 
        data: pandas.DataFrame
            Los datos extraidos del BRCPData de acuerdo a la informacion declarada en las variables constructoras (vea metodo `state_inputs()`) con el metodo `GET()` de esta clase.  
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

    def state_inputs(self):
        '''Declara el estado actual de todas las variables constructoras de la clase Marco. 
        '''

        print('''corriendo estado actual de todas las variables constructoras...\n
objeto.metadata = {}
objeto.codigos = {}
objeto.formato = {}
objeto.fechaini = {}
objeto.fechafin = {}
objeto.idioma = {}
'''.format('<vacio>' if len(self.metadata)==0 else str(type(self.metadata))+' size: '+str(self.metadata.shape),
        self.codigos,
        self.formato,
        self.fechaini, 
        self.fechafin,
        self.idioma))


    def get_metadata(self, filename='metadata.csv'): 
        '''Extrae todos los metadatos de BCRPData. 
        
        Parametros
        ----------
        filename : str
            Nombre del archivo para guardar todos los metadatos extraidos como un archivo .csv (predeterminado: 'metadata.csv'). Si se desea no guardar un archivo, cambiar a filename=''
        '''
        self.metadata = pandas.read_csv(
            'https://estadisticas.bcrp.gob.pe/estadisticas/series/metadata', delimiter=';', encoding='latin-1'
            )
        
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


        print('corriendo query para {}...\n'.format(codigo))

        index = df.index[df.iloc[:,0] == codigo].tolist()
        print('{} es indice {} en metadatos'.format(codigo, index[0]))

        dict = self.metadata.loc[index].to_dict()
        for i in dict.keys():
            dict[i] = dict[i][index[0]]
        dict.pop("Unnamed: 13" ) if "Unnamed: 13" in dict.keys() else None

        jsondata = json.dumps(dict,indent = 8,ensure_ascii=False)
        print(jsondata)
        return jsondata
    
    def querydict(self,codigo='PD39793AM'):

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
        '''Busqueda difusa de palabra clave (keyword) en metadatos de BCRPData. Regresa una tabla de 
        datos en formato pandas.DataFrame de los metadatos asociados con aquella palabra. 

        Parametros
        ----------
        keyword : str
            Palabra clave para reducir los metadatos
        cutoff : float
            Este es el Levenshtein similarity ratio (predeterminado=0.65). Un cutoff de 1.00 solo regresara metadatos que contienen palabras que coinciden con la palabra clave al 100%.
        columnas : str
            Indices de columnas de los metadatos seleccionados para correr el metodo. Predeterminado='all' corre el metodo en todas las columnas. 
        '''

        print('corriendo wordsearch: `{}`'.format(keyword))
        print('cutoff =',cutoff, end='')
        print('; columnas =',"`"+columnas+"`(todas)" if columnas=='all' else columnas)
        # print('*medido con Levenshtein similarity ratio')
        print('por favor esperar...\n')

        INDICES = []
        df=  self.get_metadata() if len(self.metadata) == 0 else self.metadata


        'placeholder dataframes (so that nothing gets overwritten)'
        new_df = df.copy()
        bool_df = df.copy()

        'language processing; split titles into separate words and assess all with fuzzy string matching (True if similar word to keyword is found in titles/sentences)'
        loop_range = range(14) if columnas == 'all' else columnas
        for k in tqdm(loop_range):
            # bool_df.iloc[:,k] = bool_df.iloc[:,k].apply(lambda x: (np.array([Levenshtein(word,keyword) for word in str(x).split()]) >= cutoff).any() )
            bool_df.iloc[:,k] = bool_df.iloc[:,k].apply(lambda x: True if \
                                len(list(flatten([get_close_matches(keyword,[word],n=3,cutoff=cutoff) for word in str(x).split()]))) > 0 else False )
            sleep(.1)
            print()

        'set remaining columns not matched to False'
        False_cols = [i for i in range(14)]
        [False_cols.remove(j) for j in loop_range]
        for col in False_cols:
            bool_df.iloc[:,col].values[:] = False

        'keep dataframe rows which evaluate ANY of its columns to True'
        new_df = new_df[bool_df.any(axis=1)]

        print('\n\n',new_df)
        return new_df

    def ref_metadata(self,filename=False):
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


    def ordenar_columnas(self,hacer=True):
        '''sub-metodo para re-ordenar columnas de acuerdo a como fueron definidos en objeto.codigos (vea metodo `GET()` parametro "orden")

        Parametros
        ----------
        hacer : bool
            ordenarlas (True)
        '''
        self.get_metadata() if len(self.metadata) == 0 else None
        df = self.metadata

        user_order = [ '{} - {}'.format(self.querydict(codigo)["Grupo de serie"],self.querydict(codigo)["Nombre de serie"]) for codigo in self.codigos]
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

    def GET(self,filename=False, orden=True,tiempo="timestamp"):
        '''Extrae los datos del BCRPData selecionados por las previamente-declaradas variables `objeto.codigos`, `objeto.fechaini`, `objeto.fechafin`, `objeto.formato`, y `objeto.idioma`. 

        Parametros
        ----------
        filename : str (opcional)
            Nombre para guardar los datos extraidos como un archivo .csv
        orden : bool
            Las columnas mantienen el orden declarados por el usuario en `objeto.codigos`  con opcion `orden=True` (predeterminado). Cuando `orden=False`, las columnas de los datos es la predeterminada por BCRPData. 
        tiempo : str
            Formato de las fechas en el pandas.Dataframe. Predeterminado: `timestamp` convierte fechas con el formato `str(MMM.YYYY)` (ejemplo Apr.2022) de BCRPData a la estructura de datos `Timestampt(YYYY-MM-01)` que es elastico para las graficas visuales y otra manipulacion de datos. Cualquier otro valor para esta variable mantiene el formato rigido `str(MMM.YYYY)` de BCRPData. 
        '''

        root = 'https://estadisticas.bcrp.gob.pe/estadisticas/series/api'
        format = self.formato 
        code_series = '-'.join(self.codigos)
        period = '{}/{}'.format(self.fechaini,self.fechafin) 
        language = self.idioma

        url = "{}/{}/{}/{}/{}".format(root,code_series,format,period,language)

        'https://www.geeksforgeeks.org/response-json-python-requests/'
        response = requests.get(url)

        dict  = response.json()

        header = [k['name'] for k in dict['config']['series'] ]
        df = pandas.DataFrame(columns=header) # aqui todavia no se han insertado los datos en las filas


        for j in dict['periods']:
            # print(j['values'])
            df.loc[j['name']] = [float(ij) if ij!='n.d.' else None for ij in j['values'] ]

        if tiempo =="timestamp":
            df.index = pandas.to_datetime(df.index)     #convierte fechas a datetime (para facilitar visual acercar y alejar ticks de las graficas)

        self.data = df              #almacena datos extraidos de BCRPData en self.data 

        self.ordenar_columnas() if orden else self.ordenar_columnas(False)

        print(url)

        if filename:
            self.data.to_csv(filename,sep=",")
        
        return self.data

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
