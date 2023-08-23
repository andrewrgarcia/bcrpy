import bcrpy
import matplotlib.pyplot as plt 
import numpy as np

banco = bcrpy.Marco()

def test_queries():
    banco.query()
    banco.query('PN00015MM')

    banco.codigos = ['PN01288PM','PN01289PM']
    banco.refine_metadata('metadata_refined.csv')


def test_metadataGET():

    banco.get_metadata()


def test_words():

    banco.wordsearch('economia')
    banco.wordsearch('economia',columnas =[0,1])

    # df= banco.metadata
    # for i in df.index :
    #     print(i)


def test_metadataLOAD():
    banco.load_metadata()
    print(banco.metadata)


def test_GETandplot():
    banco.codigos = ['PN01288PM','PN01289PM','PN00015MM']
    banco.fechaini = '2019-1'
    banco.fechafin = '2021-1'

    banco.parametros()

    df = banco.GET()

    bcrpy.save_dataframe(df,"mydf.p")


    for name in df.columns:
        plt.figure(figsize=(9, 4))
        banco.plot(df[name],name,12)

    plt.show()


def test_GETorden():
    print('GET orden metadatos')
    banco.codigos = ['PN01288PM','PN01289PM','PN00015MM']
    banco.fechaini = '2019-1'
    banco.fechafin = '2021-1'

    banco.parametros()

    df = banco.GET(order=True)
    print(df)

    banco.parametros()

    print('GET orden de lista')

    df =banco.GET(order=False)
    print(df)


def test_GETreset():
    print('GET reset (forget=True) metadatos')
    banco.codigos = ['PN01288PM','PN01289PM','PN00015MM']
    banco.fechaini = '2019-1'
    banco.fechafin = '2021-1'

    banco.parametros()

    df = banco.GET(forget=True)
    print(df)



def test_load_dataframe():

    df = bcrpy.load_dataframe("mydf.p")
    print(df)