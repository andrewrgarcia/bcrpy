import pandas as pd

class Axe:
    def __init__(self):
        """Initializes the Axe class for splitting and combining dataframes."""
        self.fragments = []

    def slice(self, dataframe, chunk_size=100):
        """Splits a dataframe into smaller chunks of the specified size.

        Parameters
        ----------
        dataframe : pandas.DataFrame
            DataFrame to be split.
        chunk_size : int, optional
            Size of each chunk (default is 100).
        """
        self.fragments = [dataframe[i:i + chunk_size] for i in range(0, len(dataframe), chunk_size)]
        return self.fragments

    def forge(self, fragments, axis=1, ignore_index=False):
        """Combines a list of fragments into a single dataframe.

        Parameters
        ----------
        fragments : list of pandas.DataFrame
            List of dataframe fragments to be combined.
        axis : {0, 1}, optional
            Axis along which to concatenate (default is 1):
            - 0: Vertical concatenation (along rows).
            - 1: Horizontal concatenation (along columns).
        ignore_index : bool, optional
            If True, do not use the index values along the concatenation axis (default is False).

        Returns
        -------
        pandas.DataFrame
            The combined dataframe.
        """
        return pd.concat(fragments, axis=axis, ignore_index=ignore_index)
