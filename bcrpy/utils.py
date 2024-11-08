import pandas as pd
import pickle
from difflib import get_close_matches
import sqlite3

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



def save_dataframe(df, filename):
    """Guarda la informacion de datos almacenados y procesados por Python en un archivo

    Parametros
    ----------
    filename: str
        Nombre del archivo para guardar. Si el nombre termina con el sufijo ".csv", se guarda como archivo CSV, si termina con ".md", se guarda como archivo Markdown. En otro caso, el archivo se guarda en formato de Python ['pickle']
    """

    if filename[-3:] == "csv":
        df.to_csv(filename)

    if filename[-3:] == ".md":
        with open(filename, "w") as f:
            f.write(df.to_markdown())

    else:
        return pickle.dump(df, open(filename, "wb"))


def load_dataframe(filename):
    """Carga la informacion de datos almacenados en un archivo a Python

    Parametros
    ----------
    filename: str
        Nombre del archivo. Si el nombre termina con el sufijo ".csv", se carga el archivo CSV. En otro caso, el archivo se carga con el modulo de Python ['pickle']
    """

    if filename[-3:] == "csv":
        return pd.read_csv(filename, delimiter=",")

    else:
        return pickle.load(open(filename, "rb"), encoding="latin1")


def save_df_as_sql(df, db_name, table_name='time series'):
    """
    Saves a DataFrame with time series data to an SQLite database.
    
    Parameters:
    - df: pandas.DataFrame, the DataFrame containing time series data.
    - db_name: str, the name of the SQLite database file (e.g., 'database.db').
    - table_name: str, the name of the table in the database to save the data to.
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
        df.index = pd.to_datetime(df.index)  # Convert index to datetime if necessary
        print("Data loaded from SQLite:", df.head())
        return df
