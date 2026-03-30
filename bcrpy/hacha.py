import pandas as pd


class Axe:
    def __init__(self):
        self.fragments = []

    def slice(self, dataframe: pd.DataFrame, chunk_size: int = 100):
        self.fragments = [
            dataframe[i:i + chunk_size]
            for i in range(0, len(dataframe), chunk_size)
        ]
        return self.fragments

    def forge(self, fragments, axis: int = 1, ignore_index: bool = False) -> pd.DataFrame:
        return pd.concat(fragments, axis=axis, ignore_index=ignore_index)