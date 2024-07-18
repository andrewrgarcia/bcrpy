import pandas as pd
import requests
import pickle

class MetadataHandler:
    def get_metadata(self, filename="metadata.csv"):
        """Extract all metadata from BCRPData."""
        url = "https://github.com/andrewrgarcia/bcrpy/raw/main/metadatos"
        self.metadata = pickle.loads(requests.get(url).content)
        if filename:
            self.metadata.to_csv(filename, sep=";", index=False)

    def load_metadata(self, filename="metadata.csv"):
        """Load the metadata saved as a .csv file into Python."""
        self.metadata = pd.read_csv(filename, delimiter=";")

    def save_metadata(self, filename="metadata_new.csv"):
        """Save the metadata in self.metadata as a .csv file."""
        self.metadata.to_csv(filename, sep=";", index=False, index_label=False)

    def refine_metadata(self, filename=False):
        """Reduce metadata to those belonging to the series codes declared in self.codigos."""
        if self.metadata.empty:
            self.get_metadata()
        indices = [self.metadata.index[self.metadata.iloc[:, 0] == k].tolist()[0] for k in self.codigos]
        self.metadata = self.metadata.loc[indices]
        if filename:
            self.save_metadata(filename)
