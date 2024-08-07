import pandas as pd
import pickle
from difflib import get_close_matches

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


def edit_distance(s1, s2, n, m, dp):
    """This is a memoized version of recursion i.e. Top-Down DP: to find minimum number
    operations to convert str1 to str2
    external credit: # This code is contributed by divyesh072019.
    source: GeeksforGeeks https://www.geeksforgeeks.org/edit-distance-dp-5/
    """
    # If any string is empty,
    # return the remaining characters of other string
    if n == 0:
        return m
    if m == 0:
        return n

    # To check if the recursive tree
    # for given n & m has already been executed
    if dp[n][m] != -1:
        return dp[n][m]

    # If characters are equal, execute
    # recursive function for n-1, m-1
    if s1[n - 1] == s2[m - 1]:
        if dp[n - 1][m - 1] == -1:
            dp[n][m] = edit_distance(s1, s2, n - 1, m - 1, dp)
            return dp[n][m]
        else:
            dp[n][m] = dp[n - 1][m - 1]
            return dp[n][m]

    # If characters are nt equal, we need to
    # find the minimum cost out of all 3 operations.
    else:
        if dp[n - 1][m] != -1:
            m1 = dp[n - 1][m]
        else:
            m1 = edit_distance(s1, s2, n - 1, m, dp)

        if dp[n][m - 1] != -1:
            m2 = dp[n][m - 1]
        else:
            m2 = edit_distance(s1, s2, n, m - 1, dp)
        if dp[n - 1][m - 1] != -1:
            m3 = dp[n - 1][m - 1]
        else:
            m3 = edit_distance(s1, s2, n - 1, m - 1, dp)

        dp[n][m] = 1 + min(m1, min(m2, m3))
        return dp[n][m]


def levenshtein_ratio(str1, str2):
    """this is the Levenshtein similarity ratio
    https://www.datacamp.com/tutorial/fuzzy-string-python
    """

    n = len(str1)
    m = len(str2)
    dp = [[-1 for i in range(m + 1)] for j in range(n + 1)]

    lev = edit_distance(str1, str2, n, m, dp)

    return ((n + m) - lev) / (n + m)
