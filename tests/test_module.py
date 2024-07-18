import bcrpy
import matplotlib.pyplot as plt
import pytest
import pandas as pd
from difflib import get_close_matches

plt.style.use("seaborn")

from bcrpy import Marco, scan_columns  # Replace 'your_module' with the actual module name

banco = Marco()

def test_queries():
    banco.query()
    banco.query("PN00015MM")

    banco.codigos = ["PN01288PM", "PN01289PM"]
    banco.refine_metadata("metadata_refined.csv")

def test_metadataGET():
    banco.get_metadata()

def test_words():
    banco.wordsearch("chicles")
    banco.wordsearch("economia", columnas=[0, 1])

def test_metadataLOAD():
    banco.load_metadata()
    print(banco.metadata)

def plot_template(data, title):
    plt.title(title, fontsize=12)
    plt.grid(axis="x")
    plt.plot(data)
    plt.tight_layout()

def test_GETandplot():
    banco.codigos = ["PN01288PM", "PN01289PM", "PN00015MM"]
    banco.fechaini = "2019-1"
    banco.fechafin = "2021-1"

    banco.parameters()

    df = banco.GET()

    bcrpy.save_dataframe(df, "mydf.p")

    for name in df.columns:
        plt.figure(figsize=(9, 4))
        plot_template(df[name], name)

    plt.show()

def test_GETorden():
    print("GET orden metadatos")
    banco.codigos = ["PN01288PM", "PN01289PM", "PN00015MM"]
    banco.fechaini = "2019-1"
    banco.fechafin = "2021-1"

    banco.parameters()

    df = banco.GET(order=True)
    print(df)

    banco.parameters()

    print("GET orden de lista")

    df = banco.GET(order=False)
    print(df)

def test_GETreset():
    print("GET reset (forget=True) metadatos")
    banco.codigos = ["PN01288PM", "PN01289PM", "PN00015MM"]
    banco.fechaini = "2019-1"
    banco.fechafin = "2021-1"

    banco.parameters()

    df = banco.GET(forget=True)
    print(df)

def test_load_dataframe():
    df = bcrpy.load_dataframe("mydf.p")
    print(df)

# New test for the scan_columns function
@pytest.fixture
def sample_dataframe():
    data = {
        'economia': [1, 2, 3],
        'ecologia': [4, 5, 6],
        'economics': [7, 8, 9],
        'biology': [10, 11, 12]
    }
    return pd.DataFrame(data)

def test_scan(sample_dataframe):
    keyword = 'econ'
    result = scan_columns(sample_dataframe, keyword, cutoff=0.5)  # Lowered cutoff
    assert 'economia' in result
    assert 'ecologia' in result
    assert 'economics' in result
    assert 'biology' not in result

def test_scan_no_matches(sample_dataframe):
    keyword = 'physics'
    result = scan_columns(sample_dataframe, keyword)
    assert result == []

