import pandas as pd
import pickle, json, os
from difflib import get_close_matches
import sqlite3
from typing import Optional


def scan_columns(df: pd.DataFrame, keyword: str, cutoff: float = 0.65):
    """
    Perform a fuzzy search on the column names of the given DataFrame and return columns that closely resemble the specified keyword.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame whose columns are to be scanned.
    keyword : str
        The keyword to search for in the column names.
    cutoff : float, optional
        The similarity cutoff for the fuzzy matching (default is 0.65). Columns with a similarity score above this cutoff will be returned.

    Returns
    -------
    list of str
        A list of column names that closely resemble the specified keyword.
    """
    def contains_similar_keyword(text, keyword, cutoff=0.8):
        words = text.split()
        return any(get_close_matches(keyword, [word], n=1, cutoff=cutoff) for word in words)

    close_matches = [col for col in df.columns if contains_similar_keyword(col, keyword, cutoff)]
    return close_matches



def save_dataframe(df: pd.DataFrame, filename: str, meta: Optional[dict] = None):
    """
    Save a DataFrame to disk in CSV, Markdown, or pickle format.
    Also writes an optional .meta JSON file with context (codes, start, end, lang).

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to save.
    filename : str
        Target filename. Suffix determines the format:
          - ".csv" → CSV
          - ".md"  → Markdown
          - else   → Pickle
    meta : dict, optional
        Dictionary of metadata (codes, start, end, lang, etc.) to save alongside cache.
    """
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".csv":
        df.to_csv(filename)
    elif ext == ".md":
        with open(filename, "w", encoding="utf-8") as f:
            f.write(df.to_markdown())
    else:
        with open(filename, "wb") as f:
            pickle.dump(df, f)

    # Save sidecar metadata if provided
    if meta is not None:
        sidecar = filename + ".meta"
        with open(sidecar, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)



def load_dataframe(filename):
    """Load stored data from a file into Python.

    Parameters
    ----------
    filename : str
        Name of the file. 
        If the filename ends with the ".csv" suffix, the file is loaded as a CSV. 
        Otherwise, the file is loaded using Python's 'pickle' module.
    """
    if filename[-3:] == "csv":
        return pd.read_csv(filename, delimiter=",")

    else:
        return pickle.load(open(filename, "rb"), encoding="latin1")


def save_df_as_sql(df, db_name, table_name='time series'):
    """
    Saves a DataFrame with time series data to an SQLite database.
    
    Parameters:
    --------------
    df: pandas.DataFrame, the DataFrame containing time series data.
    db_name: str, the name of the SQLite database file (e.g., 'database.db').
    table_name: str, the name of the table in the database to save the data to.
    """
    # Ensure the index is reset if it's a DateTime index for compatibility
    if isinstance(df.index, pd.DatetimeIndex):
        df = df.reset_index()

    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_name)
    try:
        # Save the DataFrame to the database table
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"Data saved successfully to '{table_name}' in '{db_name}'.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the database connection
        conn.close()

def load_from_sqlite(db_name, table_name='time_series'):
    """Load data from the SQLite cache and return as a DataFrame."""
    with sqlite3.connect(db_name) as conn:
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
        df.set_index("date", inplace=True)
        df.index = pd.to_datetime(df.index, errors="coerce")  # Convert index to datetime if necessary
        print("Data loaded from SQLite:", df.head())
        return df
