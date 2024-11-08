import bcrpy
import pytest
import pandas as pd
from difflib import get_close_matches
import os 
# import matplotlib.pyplot as plt


from bcrpy import Marco, scan_columns  # Replace 'your_module' with the actual module name

banco = Marco()

#  GET with 'df' storage option
def test_GET_dataframe_storage():
    banco.fechaini = "2019-1"
    banco.fechafin = "2021-1"
    df = banco.GET(codes=["PN01288PM", "PN01289PM"], storage='df')
    assert isinstance(df, pd.DataFrame), "GET with storage='df' should return a DataFrame"
    assert not df.empty, "DataFrame should not be empty"
    bcrpy.save_dataframe(df, "mydf.p")
    os.remove("mydf.p")  # Clean up after test

# GET with 'sql' storage option
def test_GET_sql_storage():
    banco.codes = ["PN01288PM", "PN01289PM"]
    banco.fechaini = "2019-1"
    banco.fechafin = "2021-1"
    db_file = "cache.db"
    df_sql = banco.GET(storage='sql')
    assert isinstance(df_sql, pd.DataFrame), "GET with storage='sql' should return a DataFrame"
    assert not df_sql.empty, "DataFrame should not be empty"
    assert os.path.exists(db_file), "SQLite database file should be created"
    os.remove(db_file)  # Clean up after test

# largeGET with 'df' storage option
def test_largeGET_dataframe_storage():
    banco.fechaini = "2019-1"
    banco.fechafin = "2021-1"
    df = banco.largeGET(codes=["PN01288PM", "PN01289PM", "PN00015MM"], chunk_size=2, storage='df')
    assert isinstance(df, pd.DataFrame), "largeGET with storage='df' should return a DataFrame"
    assert not df.empty, "DataFrame should not be empty"
    bcrpy.save_dataframe(df, "mydf_large.p")
    os.remove("mydf_large.p")  # Clean up after test
    os.remove("large_cache.bcrfile")  # Clean up after test

# largeGET with 'sql' storage option
def test_largeGET_sql_storage():
    banco.fechaini = "2019-1"
    banco.fechafin = "2021-1"
    db_file = "large_cache.db"
    df_sql = banco.largeGET(codes=["PN01288PM", "PN01289PM", "PN00015MM"], chunk_size=2, storage='sql')
    assert isinstance(df_sql, pd.DataFrame), "largeGET with storage='sql' should return a DataFrame"
    assert not df_sql.empty, "DataFrame should not be empty"
    assert os.path.exists(db_file), "SQLite database file should be created"
    os.remove(db_file)  # Clean up after test

# cache retrieval (both 'df' and 'sql' modes)
def test_GET_cache():
    # Ensure cache exists by making a GET request with forget=False
    banco.codes = ["PN01288PM", "PN01289PM"]
    banco.fechaini = "2019-1"
    banco.fechafin = "2021-1"
    
    # First request to generate cache
    df = banco.GET(forget=True, storage='df')
    assert not df.empty, "Initial DataFrame should not be empty"
    cached_df = banco.GET(forget=False, storage='df')
    assert not cached_df.empty, "Cached DataFrame should not be empty"
    
    db_file = "cache.db"
    df_sql = banco.GET(forget=True, storage='sql')
    assert not df_sql.empty, "Initial SQLite data should not be empty"
    cached_df_sql = banco.GET(forget=False, storage='sql')
    assert not cached_df_sql.empty, "Cached SQLite data should not be empty"
    assert os.path.exists(db_file), "SQLite database file should exist after caching"
    os.remove(db_file)  # Clean up after test


def test_queries():
    banco.query()
    banco.query("PN00015MM")

    banco.codes = ["PN01288PM", "PN01289PM"]
    banco.refine_metadata("metadata_refined.csv")

def test_metadataGET():
    banco.get_metadata()

def test_words():
    banco.wordsearch("chicles")
    banco.wordsearch("economia", columnas=[0, 1])

def test_metadataLOAD():
    banco.load_metadata()
    print(banco.metadata)

# def plot_template(data, title):
#     plt.title(title, fontsize=12)
#     plt.grid(axis="x")
#     plt.plot(data)
#     plt.tight_layout()

def test_GET():
    banco.codes = ["PN01288PM", "PN01289PM", "PN00015MM"]
    banco.fechaini = "2019-1"
    banco.fechafin = "2021-1"

    banco.parameters()

    df = banco.GET()

    bcrpy.save_dataframe(df, "mydf.p")
    os.remove("mydf.p")  # Clean up after test

    # for name in df.columns:
    #     plt.figure(figsize=(9, 4))
    #     plot_template(df[name], name)

    # plt.show()

def test_GETorden():
    print("GET orden metadatos")
    banco.codes = ["PN01288PM", "PN01289PM", "PN00015MM"]
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
    banco.codes = ["PN01288PM", "PN01289PM", "PN00015MM"]
    banco.fechaini = "2019-1"
    banco.fechafin = "2021-1"

    banco.parameters()

    df = banco.GET(forget=True)
    print(df)

def test_load_dataframe():
    df = bcrpy.load_dataframe("mydf.p")
    print(df)
    os.remove("mydf.p")  # Clean up after test

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

