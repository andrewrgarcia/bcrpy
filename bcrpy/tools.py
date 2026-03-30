import json
from difflib import get_close_matches

import pandas as pd
from termcolor import colored


class MetadataTools:
    def __init__(self, metadata: pd.DataFrame):
        self.metadata = metadata

    def query(self, codigo="PD39793AM"):
        if self.metadata.empty:
            raise ValueError("Metadata is empty. Load metadata first.")

        index = self.metadata.index[self.metadata.iloc[:, 0] == codigo].tolist()

        if not index:
            print(f"[WARN] code {codigo} not found")
            return None

        idx = index[0]
        data_dict = self.metadata.loc[[idx]].to_dict()

        for key in data_dict:
            data_dict[key] = data_dict[key][idx]

        data_dict.pop("Unnamed: 13", None)

        print(colored(f"query → {codigo}", "green"))
        print(json.dumps(data_dict, indent=4, ensure_ascii=False))

        return data_dict

    def query_dict(self, codigo="PD39793AM"):
        if self.metadata.empty:
            raise ValueError("Metadata is empty.")

        index = self.metadata.index[self.metadata.iloc[:, 0] == codigo].tolist()

        if not index:
            return None

        idx = index[0]
        data_dict = self.metadata.loc[[idx]].to_dict()

        for key in data_dict:
            data_dict[key] = data_dict[key][idx]

        data_dict.pop("Unnamed: 13", None)

        return data_dict

    def wordsearch(self, keyword="economia", cutoff=0.65, columnas="all"):
        if self.metadata.empty:
            raise ValueError("Metadata is empty.")

        def contains_similar_keyword(text, keyword, cutoff):
            words = str(text).split()
            return any(
                get_close_matches(keyword, [word], n=1, cutoff=cutoff)
                for word in words
            )

        if columnas == "all":
            bool_df = self.metadata.apply(
                lambda col: col.apply(
                    lambda x: contains_similar_keyword(x, keyword, cutoff)
                )
            )
        else:
            bool_df = self.metadata.iloc[:, columnas].apply(
                lambda col: col.apply(
                    lambda x: contains_similar_keyword(x, keyword, cutoff)
                )
            )

        result = self.metadata[bool_df.any(axis=1)]
        print(result)
        return result

    def order_columns(self, df: pd.DataFrame, codes: list[str]) -> pd.DataFrame:
        if self.metadata.empty:
            raise ValueError("Metadata is empty.")

        user_order = []
        for code in codes:
            meta = self.query_dict(code)
            if meta is None:
                continue
            user_order.append(f"{meta['Grupo de serie']} - {meta['Nombre de serie']}")

        return df.reindex(columns=user_order)