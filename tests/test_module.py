import os
import shutil
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import bcrpy
from bcrpy import Marco, get, large_get
from bcrpy.utils import scan_columns

CACHE_DIR = ".bcrpy_cache"


@pytest.fixture(autouse=True)
def clear_cache_dir():
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)
    yield
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)


@pytest.fixture
def banco():
    return Marco(verbose=False)


@pytest.fixture
def fake_response_single():
    return {
        "config": {
            "series": [
                {"name": "Serie A"},
                {"name": "Serie B"},
            ]
        },
        "periods": [
            {"name": "2019-01", "values": ["1.0", "2.0"]},
            {"name": "2019-02", "values": ["3.0", "4.0"]},
        ],
    }


@pytest.fixture
def fake_response_wrapper():
    return {
        "config": {"series": [{"name": "DummySeries"}]},
        "periods": [
            {"name": "2020-01", "values": ["1.23"]},
            {"name": "2020-02", "values": ["4.56"]},
        ],
    }


@patch("bcrpy._fetcher.Fetcher._fetch_json")
def test_get_dataframe_storage(mock_fetch, banco, fake_response_single):
    mock_fetch.return_value = fake_response_single

    df = banco.GET(
        codes=["PN01288PM", "PN01289PM"],
        start="2019-1",
        end="2021-1",
        storage="df",
        forget=True,
    )

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert os.path.exists(CACHE_DIR)
    assert any(name.endswith(".bcrfile") for name in os.listdir(CACHE_DIR))


@patch("bcrpy._fetcher.Fetcher._fetch_json")
def test_get_sql_storage(mock_fetch, banco, fake_response_single):
    mock_fetch.return_value = fake_response_single

    df = banco.GET(
        codes=["PN01288PM", "PN01289PM"],
        start="2019-1",
        end="2021-1",
        storage="sql",
        forget=True,
    )

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert os.path.exists(CACHE_DIR)
    assert any(name.endswith(".db") for name in os.listdir(CACHE_DIR))


@patch("bcrpy._fetcher.Fetcher._fetch_json")
def test_largeget_dataframe_storage(mock_fetch, banco, fake_response_single):
    mock_fetch.return_value = fake_response_single

    df = banco.largeGET(
        codes=["PN01288PM", "PN01289PM", "PN00015MM"],
        start="2019-1",
        end="2021-1",
        chunk_size=2,
        storage="df",
        forget=True,
        workers=2,
    )

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert any(name.startswith("large_cache_") and name.endswith(".bcrfile") for name in os.listdir(CACHE_DIR))


@patch("bcrpy._fetcher.Fetcher._fetch_json")
def test_largeget_sql_storage(mock_fetch, banco, fake_response_single):
    mock_fetch.return_value = fake_response_single

    df = banco.largeGET(
        codes=["PN01288PM", "PN01289PM", "PN00015MM"],
        start="2019-1",
        end="2021-1",
        chunk_size=2,
        storage="sql",
        forget=True,
        workers=2,
    )

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert any(name.startswith("large_cache_") and name.endswith(".db") for name in os.listdir(CACHE_DIR))


@patch("bcrpy._fetcher.Fetcher._fetch_json")
def test_get_cache_reuse(mock_fetch, banco, fake_response_single):
    mock_fetch.return_value = fake_response_single

    df1 = banco.GET(
        codes=["PN01288PM", "PN01289PM"],
        start="2019-1",
        end="2021-1",
        storage="df",
        forget=True,
    )
    assert not df1.empty
    assert mock_fetch.call_count == 1

    df2 = banco.GET(
        codes=["PN01288PM", "PN01289PM"],
        start="2019-1",
        end="2021-1",
        storage="df",
        forget=False,
    )
    assert not df2.empty
    assert mock_fetch.call_count == 1


def test_metadata_get(banco):
    meta = banco.get_metadata()
    assert isinstance(meta, pd.DataFrame)
    assert not meta.empty


def test_metadata_refine_and_save(banco, tmp_path):
    banco.get_metadata()
    banco.codes = ["PN01288PM", "PN01289PM"]
    out = tmp_path / "metadata_refined.csv"

    refined = banco.refine_metadata(str(out))
    assert isinstance(refined, pd.DataFrame)
    assert out.exists()


def test_scan_columns():
    df = pd.DataFrame({
        "economia": [1, 2],
        "ecologia": [3, 4],
        "economics": [5, 6],
        "biology": [7, 8],
    })

    result = scan_columns(df, "econ", cutoff=0.5)

    assert "economia" in result
    assert "ecologia" in result
    assert "economics" in result
    assert "biology" not in result


def test_scan_columns_no_matches():
    df = pd.DataFrame({
        "economia": [1, 2],
        "biology": [3, 4],
    })

    result = scan_columns(df, "physics")
    assert result == []


@patch("bcrpy._fetcher.Fetcher._fetch_json")
def test_get_wrapper(mock_fetch, fake_response_wrapper):
    mock_fetch.return_value = fake_response_wrapper

    df = get(
        codes=["PN01288PM"],
        start="2020-01",
        end="2020-12",
        forget=True,
    )

    assert isinstance(df, pd.DataFrame)
    assert not df.empty


@patch("bcrpy._fetcher.Fetcher._fetch_json")
def test_large_get_wrapper(mock_fetch, fake_response_single):
    mock_fetch.return_value = fake_response_single

    df = large_get(
        codes=["PN01288PM", "PN01289PM"],
        start="2019-01",
        end="2020-01",
        chunk_size=2,
        forget=True,
        workers=2,
    )

    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_tools_query_and_query_dict(banco):
    banco.get_metadata()
    tools = banco.tools()

    result = tools.query_dict("PN00015MM")
    assert result is None or isinstance(result, dict)


def test_tools_wordsearch(banco):
    banco.get_metadata()
    tools = banco.tools()

    result = tools.wordsearch("economia")
    assert isinstance(result, pd.DataFrame)