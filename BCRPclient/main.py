import requests 
import pandas
import json 



class Marco:
    def __init__(self):
        self.metadata = []
        self.codigos = []

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
        print('running query...\n')
        self.get_metadata() if len(self.metadata) == 0 else None
        
        df = self.metadata
        index = df.index[df.iloc[:,0] == codigo].tolist()
        print('{} es indice {} en metadatos'.format(codigo, index[0]))

        dict = self.metadata.loc[index].to_dict()
        for i in dict.keys():
            dict[i] = dict[i][index[0]]
        dict.pop("Unnamed: 13" ) if "Unnamed: 13" in dict.keys() else None

        jsondata = json.dumps(dict,indent = 8,ensure_ascii=False)
        print(jsondata)
        return jsondata

    def refine(self,filename=False):

        df=self.metadata
        indices = [ df.index[df.iloc[:,0] == k].tolist()[0] for k in self.codigos ]
        
        self.metadata = self.metadata.loc[indices]

        if filename:
            self.save_metadata(filename)


