
<a href="https://bcrpy.vercel.app/">
  <img src="https://raw.githubusercontent.com/andrewrgarcia/bcrpy/main/docs/img/bcrp_poly_logo.png" 
       alt="BCRP Logo" 
       width="260" 
       style="display: block; margin: 0 auto" />
</a>

<br>

<h2 align="center">bcrpy</h2>

<p align="center">
Python client for accessing and analyzing macroeconomic data from the
<a href="https://www.bcrp.gob.pe/">Banco Central de Reserva del Perú (BCRP)</a>.
</p>

<p align="center">
<a href="https://pypi.org/project/bcrpy/"><img src="https://img.shields.io/pypi/v/bcrpy.svg"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg"></a>
<a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

---

## 📊 What is BCRP Data?

The BCRP provides a public API with hundreds of economic time series, including:

- Inflation (IPC)
- GDP and economic activity
- Interest rates
- Monetary aggregates
- External sector indicators

Official API:
👉 https://estadisticas.bcrp.gob.pe/estadisticas/series/ayuda/api

Explore data:
👉 https://estadisticas.bcrp.gob.pe/estadisticas/series/

---

## ⚡ Overview

`bcrpy` is a **lightweight data access layer** for BCRP macroeconomic data.

It provides:

- Simple Python interface (`get`, `large_get`)
- Parallel data fetching
- Built-in caching (disk + SQLite)
- Metadata exploration tools
- Clean pandas output

---

## 🚀 Installation (UV recommended)

```bash
git clone https://github.com/andrewrgarcia/bcrpy
cd bcrpy
uv sync
```

---

## ⚡ Quick Start

```python
from bcrpy import get

df = get(
    codes=["PN01288PM"],  # inflation
    start="2020-01",
    end="2023-01"
)

print(df.head())
```

---

## 🔥 Large Requests (Parallel)

```python
from bcrpy import large_get

df = large_get(
    codes=["PN01288PM", "PN01289PM", "PN00015MM"],
    start="2010-01",
    end="2023-01",
    chunk_size=2,
    workers=4
)
```

---

## 🧠 Metadata Tools

```python
from bcrpy import Marco

m = Marco()
m.get_metadata()

tools = m.tools()

tools.query("PN01288PM")
tools.wordsearch("inflacion")
```

---

## 📁 Cache System

Data is cached automatically:

```
.bcrpy_cache/
├── cache_<hash>.bcrfile
├── cache_<hash>.meta
├── large_cache_<hash>.bcrfile
```

Features:

* Automatic reuse
* Hash-based isolation (no collisions)
* Optional SQLite backend

---

## ⚙️ Configuration

```python
get(..., forget=True)     # ignore cache
large_get(..., workers=2) # control parallelism
```

---

## 🧪 Testing

Run all tests:

```bash
uv run pytest -v
```

---

## 🧱 Architecture

```
bcrpy/
├── _fetcher.py     # core data retrieval
├── _http.py        # HTTP + retry logic
├── _metadata.py    # metadata handling
├── tools.py        # search / query tools
├── utils.py        # IO + helpers
```

---

## 🎯 Design Principles

* Minimal dependencies
* Explicit behavior (no hidden magic)
* Reproducibility via caching
* Separation of concerns (data vs tools)

---

## 📌 Notes

* No API key required (public BCRP API)
* Network-dependent (uses official endpoint)
* Designed for research and modeling workflows

---

## 📄 License

MIT
