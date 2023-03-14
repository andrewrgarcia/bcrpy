import requests 
import json 

import numpy as np
import pandas

from tqdm import tqdm
from time import sleep

import matplotlib.pyplot as plt 
from bcrpy.anexo import Levenshtein


class Marco:
    def __init__(self):
        '''Este es el marco principal para almacenar variables y ejecutar metodos para extraer, buscar y manejar datos. 

        Parametros
        ----------
        metadata: <Pandas DataFrame>
            Los metadatos de las series estadísticas del BRCPData, los cuales pueden ser reducidos con el metodo ref_metadata de esta `class`. 
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
        self.metadata = ''
        self.codigos = ['PN01288PM','PN01289PM']
        self.formato = 'json'
        self.fechaini = '2010-1'
        self.fechafin = '2016-9'
        self.idioma = 'ing'

    def state_inputs(self):
        '''Declara el estado actual de todas las variables constructoras de la clase Marco. 
        '''

        print('''corriendo estado actual de todas las variables constructoras...\n
self.metadata = {}
self.codigos = {}
self.formato = {}
self.fechaini = {}
self.fechafin = {}
self.idioma = {}
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



    def wordsearch(self,keyword='economia',fidelity=0.65,columnas='all',verbose=False):
        '''Busqueda difusa de palabra clave (keyword) en metadatos de BCRPData. Regresa una tabla de 
        datos en formato <Pandas DataFrame> de los metadatos asociados con aquella palabra. 

        Parametros
        ----------
        keyword : str
            Palabra clave para reducir los metadatos
        fidelity : float
            Este es el Levenshtein similarity ratio (predeterminado=0.65). Un fidelity de 1.00 solo regresara metadatos que contienen palabras que coinciden con la palabra clave al 100%.
        columnas : str
            Indices de columnas de los metadatos seleccionados para correr el metodo. Predeterminado='all' corre el metodo en todas las columnas. 
        verbose : bool
            Muestra las columnas que estan siendo elegidas mientras el metodo corre (predeterminado=False)
        '''

        print('corriendo wordsearch: `{}` (fidelity = {})* '.format(keyword,fidelity))
        print('*medido con Levenshtein similarity ratio')
        print('por favor esperar...\n')

        INDICES = []
        df=  self.get_metadata() if len(self.metadata) == 0 else self.metadata

        loop_range = range(12) if columnas == 'all' else columnas
        for k in tqdm(loop_range):
            sim_words = []
            for j in df.iloc[:,k]:
                wordstring = str(j)
                a = [Levenshtein(word,keyword) for word in wordstring.split()]
                b = [(word,keyword) for word in wordstring.split()]
                if (np.array(a) >= fidelity).any():
                    sim_words.append(wordstring)
            
            sim_words=list(set(sim_words))
            
            print(sim_words) if verbose else None

            sleep(.1)

            print()
            if len(sim_words) !=0:
                INDICES.extend(list(set(df.index[ df.iloc[:,k].isin(sim_words)].tolist())))

        INDICES = list(set(INDICES))
        new_df = df.iloc[INDICES]
        print('\n\n',new_df)
        return new_df

    def ref_metadata(self,filename=False):
        '''Reduce los metadatos en self.metadata a aquellos perteneciendo a los codigos de serie declarados en self.codigos. 

        Parametros
        ----------
        filename : str (opcional)
            Nombre para guardar la informacion de la modificada self.metadata como un archivo .csv 
        '''
                
        df=self.metadata
        indices = [ df.index[df.iloc[:,0] == k].tolist()[0] for k in self.codigos ]
        
        self.metadata = self.metadata.loc[indices]

        if filename:
            self.save_metadata(filename)


    def GET(self,filename=False):
        '''Extrae los datos del BCRPData selecionados por las previamente-declaradas variables `self.codigos`, `self.fechaini`, `self.fechafin`, `self.formato`, y `self.idioma`. 

        Parametros
        ----------
        filename : str (opcional)
            Nombre para guardar los datos extraidos como un archivo .csv
        '''

        root = 'https://estadisticas.bcrp.gob.pe/estadisticas/series/api'
        format = self.formato 
        code_series = '-'.join(self.codigos)
        period = '{}/{}'.format(self.fechaini,self.fechafin) 
        language = self.idioma

        url = "{}/{}/{}/{}/{}".format(root,code_series,format,period,language)
        print(url)

        'https://www.geeksforgeeks.org/response-json-python-requests/'
        response = requests.get(url)
        dict  = response.json()

        header = [k['name'] for k in dict['config']['series'] ]
        df = pandas.DataFrame(columns=header) # Note that there are now row data inserted.

        for j in dict['periods']:
            # print(j['values'])
            df.loc[j['name']] = [float(ij) if ij!='n.d.' else None for ij in j['values'] ]

        if filename:
            df.to_csv(filename,sep=",")
        
        # print(df)
        return df

    def plot(self, data, title='', titlesize=9, func='plot'):
        '''Grafica x-y data.

        Parametros
        ----------
        data : <Pandas DataFrame>
            Data x-y extraida de BCRPData, x es fecha y es cantidad. 
        title : str
            Titulo para grafica
        func : str
            Tipo de grafica. 'plot' es grafica comun, 'semilogy' es grafica con escala logaritmica en y-axis.  
        titlesize : str
            Tamaño de titulo para grafica
        '''
        plt.style.use("seaborn-pastel")

        plt.title(title, fontsize=titlesize)
        plt.grid(axis='y')
        eval('plt.{}(data)'.format(func))
        plt.xticks(data.index, rotation =60)
        plt.tight_layout()
