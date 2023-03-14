import requests 
import json 

import numpy as np
import pandas

from tqdm import tqdm
from time import sleep

import matplotlib.pyplot as plt 
from bcrpy.anexo import Levenshtein
plt.style.use("seaborn-pastel")


class Marco:
    def __init__(self):
        self.metadata = ''
        self.codigos = ['PN01288PM','PN01289PM']
        self.formato = 'json'
        self.fechaini = '2010-1'
        self.fechafin = '2016-9'
        self.idioma = 'ing'

    def state_inputs(self):

        print('''running current inputs state...\n
self.metadata = {}
self.codigos = {}
self.formato = {}
self.fechaini = {}
self.fechafin = {}
self.idioma = {}
'''.format('<vacio>' if len(self.metadata)==0 else type(self.metadata),
        self.codigos,
        self.formato,
        self.fechaini, 
        self.fechafin,
        self.idioma))


    def get_metadata(self, filename='metadata.csv'): 
        self.metadata = pandas.read_csv(
            'https://estadisticas.bcrp.gob.pe/estadisticas/series/metadata', delimiter=';', encoding='latin-1'
            )
        
        if filename[-3:] == 'csv':
            self.metadata.to_csv(filename,sep=";",index=False, index_label=False)

    def load_metadata(self,filename='metadata.csv'):
        if filename[-3:] == 'csv':
            self.metadata = pandas.read_csv(filename, delimiter=';')

    def save_metadata(self,filename='metadata_new.csv'):
        if filename[-3:] == 'csv':
            self.metadata.to_csv(filename,sep=";",index=False, index_label=False)

        
    def query(self,codigo='PD39793AM'):
        self.get_metadata() if len(self.metadata) == 0 else None
        df = self.metadata


        print('running query for {}...\n'.format(codigo))

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

        print('running word search: `{}` (fidelity = {})* '.format(keyword,fidelity))
        print('*measured with Levenshtein similarity ratio')
        print('please wait...\n')

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
        '''refinar metadata'''
        df=self.metadata
        indices = [ df.index[df.iloc[:,0] == k].tolist()[0] for k in self.codigos ]
        
        self.metadata = self.metadata.loc[indices]

        if filename:
            self.save_metadata(filename)


    def GET(self,filename=False):

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

    def plot(self, data,title='', func='plot'):

        plt.title(title, fontsize=9)
        plt.grid(axis='y')
        eval('plt.{}(data)'.format(func))
        plt.xticks(data.index, rotation =60)
        plt.tight_layout()
