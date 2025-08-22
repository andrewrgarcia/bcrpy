import bcrpy
import pytest
import pandas as pd
import os, json
from bcrpy import Marco, scan_columns, get, large_get
from unittest.mock import patch, MagicMock

banco = Marco()

# --- Helpers ---

def cleanup_cache():
    """Remove all cache + meta files created during tests."""
    for fname in [
        "cache.bcrfile", "cache.bcrfile.meta",
        "cache.db", "cache.db.meta",
        "large_cache.bcrfile", "large_cache.bcrfile.meta",
        "large_cache.db", "large_cache.db.meta",
        "mydf.p", "mydf_large.p", "metadata_refined.csv"
    ]:
        if os.path.exists(fname):
            os.remove(fname)

@pytest.fixture(autouse=True)
def clear_cache_files():
    cleanup_cache()
    yield
    cleanup_cache()


# --- Tests ---

def test_GET_dataframe_storage():
    df = banco.GET(codes=["PN01288PM", "PN01289PM"], start="2019-1", end="2021-1", storage='df', forget=True)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert os.path.exists("cache.bcrfile")
    assert os.path.exists("cache.bcrfile.meta")


def test_GET_sql_storage():
    banco.codes = ["PN01288PM", "PN01289PM"]
    banco.start = "2019-1"
    banco.end = "2021-1"
    df_sql = banco.GET(storage='sql', forget=True)
    assert isinstance(df_sql, pd.DataFrame)
    assert not df_sql.empty
    assert os.path.exists("cache.db")
    assert os.path.exists("cache.db.meta")


def test_largeGET_dataframe_storage():
    banco.start = "2019-1"
    banco.end = "2021-1"
    df = banco.largeGET(codes=["PN01288PM", "PN01289PM", "PN00015MM"], chunk_size=2, storage='df', forget=True)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert os.path.exists("large_cache.bcrfile")
    assert os.path.exists("large_cache.bcrfile.meta")


def test_largeGET_sql_storage():
    banco.start = "2019-1"
    banco.end = "2021-1"
    df_sql = banco.largeGET(codes=["PN01288PM", "PN01289PM", "PN00015MM"], chunk_size=2, storage='sql', forget=True)
    assert isinstance(df_sql, pd.DataFrame)
    assert not df_sql.empty
    assert os.path.exists("large_cache.db")
    assert os.path.exists("large_cache.db.meta")


# --- Mocked cache reuse test ---
@patch("bcrpy._fetcher.requests.get")
def test_GET_cache_reuse_and_warning(mock_get, capfd):
    # Fake API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "config": {"series": [{"name": "Serie A"}, {"name": "Serie B"}]},
        "periods": [
            {"name": "2019-01", "values": ["1.0", "2.0"]},
            {"name": "2019-02", "values": ["3.0", "4.0"]},
        ],
    }
    mock_get.return_value = mock_response

    banco.codes = ["PN01288PM", "PN01289PM"]
    banco.start = "2019-1"
    banco.end = "2021-1"

    df = banco.GET(forget=True, storage='df')
    assert not df.empty

    cached_df = banco.GET(forget=False, storage='df')
    assert not cached_df.empty

    out, _ = capfd.readouterr()
    assert "[CACHE] Using cached data" in out


def test_cache_mismatch_warning(capfd):
    # Create fake cache + .meta
    pd.DataFrame({"X": [1, 2]}).to_pickle("cache.bcrfile")
    with open("cache.bcrfile.meta", "w", encoding="utf-8") as f:
        json.dump({"codes": ["FAKECODE"], "start": "2000-1", "end": "2001-1"}, f)

    banco.codes = ["PN01288PM"]
    banco.start = "2019-1"
    banco.end = "2021-1"

    _ = banco.GET(forget=False, storage='df')
    out, _ = capfd.readouterr()
    assert "⚠️ Warning: cache parameters differ" in out


def test_queries():
    banco.query()
    banco.query("PN00015MM")
    banco.codes = ["PN01288PM", "PN01289PM"]
    banco.refine_metadata("metadata_refined.csv")
    assert os.path.exists("metadata_refined.csv")


def test_metadataGET():
    banco.get_metadata()
    assert not banco.metadata.empty


def test_words():
    banco.wordsearch("chicles")
    banco.wordsearch("economia", columnas=[0, 1])


def test_metadataLOAD():
    banco.load_metadata()
    assert not banco.metadata.empty


def test_GET_default():
    banco.codes = ["PN01288PM", "PN01289PM", "PN00015MM"]
    banco.start = "2019-1"
    banco.end = "2021-1"
    banco.parameters()
    df = banco.GET(forget=True)  # force fresh for safety
    assert not df.empty


# --- GET order tests ---
@patch("bcrpy._fetcher.requests.get")
def test_GETorden(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "config": {
            "series": [
                {"name": "Índice de precios Lima Metropolitana (índice 2009 = 100) (descontinuada) - IPC Sin Alimentos y Bebidas"},
                {"name": "Índice de precios Lima Metropolitana (índice 2009 = 100) (descontinuada) - IPC Sin Alimentos y Energía"},
            ]
        },
        "periods": [
            {"name": "2019-01", "values": ["1.0", "2.0"]},
            {"name": "2019-02", "values": ["3.0", "4.0"]},
        ],
    }
    mock_get.return_value = mock_response

    banco.codes = ["PN01288PM", "PN01289PM"]
    banco.start = "2019-1"
    banco.end = "2019-2"

    df_ordered = banco.GET(order=True, forget=True)
    assert isinstance(df_ordered, pd.DataFrame)
    assert not df_ordered.empty

    df_unordered = banco.GET(order=False, forget=True)
    assert isinstance(df_unordered, pd.DataFrame)
    assert not df_unordered.empty


@pytest.mark.integration
def test_GETorden_integration():
    banco.codes = ["PN01288PM", "PN01289PM", "PN00015MM"]
    banco.start = "2019-1"
    banco.end = "2021-1"
    df_ordered = banco.GET(order=True, forget=True)
    assert not df_ordered.empty
    df_unordered = banco.GET(order=False, forget=True)
    assert not df_unordered.empty


@pytest.mark.integration
def test_GETreset():
    banco.codes = ["PN01288PM", "PN01289PM", "PN00015MM"]
    banco.start = "2019-1"
    banco.end = "2021-1"
    df_reset = banco.GET(forget=True)
    assert not df_reset.empty



def test_load_dataframe_roundtrip():
    test_df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    bcrpy.save_dataframe(test_df, "mydf.p")
    assert os.path.exists("mydf.p")
    
    df = bcrpy.load_dataframe("mydf.p")
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["A", "B"]


# --- scan_columns tests ---
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
    result = scan_columns(sample_dataframe, "econ", cutoff=0.5)
    assert 'economia' in result
    assert 'ecologia' in result
    assert 'economics' in result
    assert 'biology' not in result

def test_scan_no_matches(sample_dataframe):
    result = scan_columns(sample_dataframe, "physics")
    assert result == []


# --- Wrapper tests ---
@patch("bcrpy._fetcher.requests.get")
def test_get_wrapper(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "config": {"series": [{"name": "DummySeries"}]},
        "periods": [
            {"name": "2020-01", "values": ["1.23"]},
            {"name": "2020-02", "values": ["4.56"]},
        ],
    }
    mock_get.return_value = mock_response

    df = get(codes=["PN01288PM"], start="2020-01", end="2020-12", forget=True)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


@pytest.mark.integration
def test_get_wrapper_integration():
    df = get(codes=["PN01288PM"], start="2020-01", end="2020-12", forget=True)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_large_get_wrapper():
    df = large_get(codes=["PN01288PM", "PN01289PM"], start="2019-01", end="2020-01", chunk_size=2, forget=True)
    assert not df.empty
