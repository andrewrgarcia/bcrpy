import bcrpy
import pytest
import pandas as pd
import os

from bcrpy import Marco, scan_columns

banco = Marco()

# Test GET with 'df' storage option
def test_GET_dataframe_storage():
    df = banco.GET(codes=["PN01288PM", "PN01289PM"], start="2019-1", end="2021-1", storage='df')
    assert isinstance(df, pd.DataFrame), "GET with storage='df' should return a DataFrame"
    assert not df.empty, "DataFrame should not be empty"
    bcrpy.save_dataframe(df, "mydf.p")
    assert os.path.exists("mydf.p"), "File should be saved"
    os.remove("mydf.p")
    assert not os.path.exists("mydf.p"), "Temporary file should be removed after test"

# Test GET with 'sql' storage option
def test_GET_sql_storage():
    banco.codes = ["PN01288PM", "PN01289PM"]
    banco.start = "2019-1"
    banco.end = "2021-1"
    db_file = "cache.db"
    df_sql = banco.GET(storage='sql')
    assert isinstance(df_sql, pd.DataFrame), "GET with storage='sql' should return a DataFrame"
    assert not df_sql.empty, "DataFrame should not be empty"
    assert os.path.exists(db_file), "SQLite database file should be created"
    os.remove(db_file)
    assert not os.path.exists(db_file), "Temporary database file should be removed after test"

# Test largeGET with 'df' storage option
def test_largeGET_dataframe_storage():
    banco.start = "2019-1"
    banco.end = "2021-1"
    df = banco.largeGET(codes=["PN01288PM", "PN01289PM", "PN00015MM"], chunk_size=2, storage='df')
    assert isinstance(df, pd.DataFrame), "largeGET with storage='df' should return a DataFrame"
    assert not df.empty, "DataFrame should not be empty"
    bcrpy.save_dataframe(df, "mydf_large.p")
    assert os.path.exists("mydf_large.p")
    os.remove("mydf_large.p")
    os.remove("large_cache.bcrfile")

# Test largeGET with 'sql' storage option
def test_largeGET_sql_storage():
    banco.start = "2019-1"
    banco.end = "2021-1"
    db_file = "large_cache.db"
    df_sql = banco.largeGET(codes=["PN01288PM", "PN01289PM", "PN00015MM"], chunk_size=2, storage='sql')
    assert isinstance(df_sql, pd.DataFrame), "largeGET with storage='sql' should return a DataFrame"
    assert not df_sql.empty, "DataFrame should not be empty"
    assert os.path.exists(db_file), "SQLite database file should be created"
    os.remove(db_file)
    assert not os.path.exists(db_file)

# Test cache retrieval for both 'df' and 'sql' modes
def test_GET_cache():
    banco.codes = ["PN01288PM", "PN01289PM"]
    banco.start = "2019-1"
    banco.end = "2021-1"
    
    # Generate cache
    df = banco.GET(forget=True, storage='df')
    assert not df.empty, "Initial DataFrame should not be empty"
    cached_df = banco.GET(forget=False, storage='df')
    assert not cached_df.empty, "Cached DataFrame should not be empty"
    
    # Check SQLite caching
    db_file = "cache.db"
    df_sql = banco.GET(forget=True, storage='sql')
    assert not df_sql.empty, "Initial SQLite data should not be empty"
    cached_df_sql = banco.GET(forget=False, storage='sql')
    assert not cached_df_sql.empty, "Cached SQLite data should not be empty"
    assert os.path.exists(db_file)
    os.remove(db_file)

# Test querying functions
def test_queries():
    banco.query()
    banco.query("PN00015MM")
    banco.codes = ["PN01288PM", "PN01289PM"]
    banco.refine_metadata("metadata_refined.csv")
    assert os.path.exists("metadata_refined.csv")
    os.remove("metadata_refined.csv")

# Test metadata retrieval
def test_metadataGET():
    banco.get_metadata()
    assert not banco.metadata.empty, "Metadata should be loaded"

# Test word search in metadata
def test_words():
    banco.wordsearch("chicles")
    banco.wordsearch("economia", columnas=[0, 1])

# Test metadata loading
def test_metadataLOAD():
    banco.load_metadata()
    assert not banco.metadata.empty, "Metadata should be loaded after loading from file"
    print(banco.metadata)

# Test GET without storage specification (default)
def test_GET():
    banco.codes = ["PN01288PM", "PN01289PM", "PN00015MM"]
    banco.start = "2019-1"
    banco.end = "2021-1"
    banco.parameters()
    df = banco.GET()
    assert not df.empty, "Default GET should return data"
    bcrpy.save_dataframe(df, "mydf.p")
    os.remove("mydf.p")

# Test GET with ordering options
def test_GETorden():
    banco.codes = ["PN01288PM", "PN01289PM", "PN00015MM"]
    banco.start = "2019-1"
    banco.end = "2021-1"
    df_ordered = banco.GET(order=True)
    assert not df_ordered.empty, "Ordered DataFrame should not be empty"
    df_unordered = banco.GET(order=False)
    assert not df_unordered.empty, "Unordered DataFrame should not be empty"

# Test GET with cache reset option
def test_GETreset():
    print("GET reset (forget=True) metadatos")
    banco.codes = ["PN01288PM", "PN01289PM", "PN00015MM"]
    banco.start = "2019-1"
    banco.end = "2021-1"
    
    banco.parameters()

    df_reset = banco.GET(forget=True)
    assert not df_reset.empty, "Reset DataFrame should not be empty"

# Test loading a saved DataFrame
def test_load_dataframe():
    test_df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    bcrpy.save_dataframe(test_df, "mydf.p")
    assert os.path.exists("mydf.p"), "File should exist before loading"
    
    df = bcrpy.load_dataframe("mydf.p")
    assert isinstance(df, pd.DataFrame), "Loaded data should be a DataFrame"
    
    os.remove("mydf.p")
    assert not os.path.exists("mydf.p"), "Temporary file should be removed after test"


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
    result = scan_columns(sample_dataframe, keyword, cutoff=0.5)
    assert 'economia' in result
    assert 'ecologia' in result
    assert 'economics' in result
    assert 'biology' not in result

def test_scan_no_matches(sample_dataframe):
    keyword = 'physics'
    result = scan_columns(sample_dataframe, keyword)
    assert result == []
