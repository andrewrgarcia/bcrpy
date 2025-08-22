from bcrpy.main import *
from bcrpy.hacha import *
from bcrpy.utils import scan_columns, save_df_as_sql, load_from_sqlite, save_dataframe, load_dataframe

# --- Legacy style (kept for backwards compatibility) ---
def GET(**kwargs):
    """Legacy wrapper for Marco().GET(). 
    Kept for compatibility; prefer `bcrpy.get`."""
    return Marco().GET(**kwargs)

def largeGET(**kwargs):
    """Legacy wrapper for Marco().largeGET(). 
    Kept for compatibility; prefer `bcrpy.large_get`."""
    return Marco().largeGET(**kwargs)

# --- New Pythonic style ---
def get(**kwargs):
    """Fetch time series data. 
    Wrapper for Marco().GET().
    
    Example:
        >>> from bcrpy import get
        >>> df = get(codes=["PN01288PM"], start="2020-01", end="2021-01")
    """
    return Marco().GET(**kwargs)

def large_get(**kwargs):
    """Fetch large sets of time series data (chunked / parallelized).
    Wrapper for Marco().largeGET().
    
    Example:
        >>> from bcrpy import large_get
        >>> df = large_get(codes=["PN01288PM", "PN01289PM"], start="2019-01", end="2020-01")
    """
    return Marco().largeGET(**kwargs)
