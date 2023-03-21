import bcrpy
import matplotlib.pyplot as plt 
import numpy as np

banco = bcrpy.Marco()

def test_queries():
    banco.query()
    banco.query('PN00015MM')

    banco.codigos = ['PN01288PM','PN01289PM']
    banco.ref_metadata('metadata_refined.csv')


def test_metadataGET():

    banco.get_metadata()


def test_words():

    banco.wordsearch('economia')
    banco.wordsearch('economia',columnas =[0,1])


    df= banco.metadata
    for i in df.index :
        print(i)


def test_metadataLOAD():
    banco.load_metadata()
    print(banco.metadata)


def test_GETandplot():
    banco.codigos = ['PN01288PM','PN01289PM','PN00015MM']
    banco.fechaini = '2019-1'
    banco.fechafin = '2021-1'

    banco.state_inputs()

    df = banco.GET('GET.csv')

    bcrpy.dfsave(df,"mydf.p")


    for name in df.columns:
        plt.figure(figsize=(9, 4))

        banco.plot(df[name],name,12)
        # plt.grid(axis='y')
        # plt.plot(df[name])
        # plt.xticks(df[name].index, rotation = 60)

        # plt.show()
    plt.show()

def test_dfload():

    df = bcrpy.dfload("mydf.p")
    print(df)