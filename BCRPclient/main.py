import requests 
import pandas
import json 


class Marco:
    def __init__(self):
        self.metadata = ''
        self.codigos = ['PN01288PM','PN01289PM']
        self.formato = 'json'
        self.fechaini = '2010-1'
        self.fechafin = '2016-9'
        self.periodo = ''
        self.idioma = 'ing'

    def state_inputs(self):

        print('''
        self.metadata = {}
        self.codigos = {}
        self.formato = {}
        self.fechaini = {}
        self.fechafin = {}
        self.periodo = {}
        self.idioma = {}
        '''.format('<vacio>' if len(self.metadata)==0 else type(self.metadata),
        self.codigos,
        self.formato,
        self.fechaini, 
        self.fechafin,
        '<vacio>' if len(self.periodo)==0 else self.periodo,
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

        
    def consulta(self,codigo='PD39793AM'):
        print('corriendo consulta...\n')
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
        period = self.periodo if len(self.periodo) != 0 else '{}/{}'.format(self.fechaini,self.fechafin) 
        language = self.idioma

        url = "{}/{}/{}/{}/{}".format(root,code_series,format,period,language)
        print(url)

        'https://www.geeksforgeeks.org/response-json-python-requests/'
        response = requests.get(url)
        dict  = response.json()

        header = [k['name'] for k in dict['config']['series'] ]
        df = pandas.DataFrame(columns=header) # Note that there are now row data inserted.

        for j in dict['periods']:
            df.loc[j['name']] = j['values']

        if filename:
            df.to_csv(filename,sep=",")
        
        print(df)
        return df
