import pandas as pd
import requests
import pickle

class MetadataHandler:
    def get_metadata(self, filename="metadata.csv"):
        """Extract all metadata from BCRPData."""
        try:
            # Attempt to load metadata from primary URL
            self.metadata = pd.read_csv('https://estadisticas.bcrp.gob.pe/estadisticas/series/metadata', delimiter=';', encoding='latin-1')
        except Exception as e:
            print(f"Error loading metadata from the primary URL: {e}")
            self.metadata = pd.DataFrame()

        # If the primary URL fails, load from backup
        if self.metadata.shape[0] <= 5:
            print("Warning: metadata contains fewer than 5 rows, likely empty or incomplete")
            url = "https://github.com/andrewrgarcia/bcrpy/raw/main/metadatos"
            try:
                metadata_content = requests.get(url).content
                self.metadata = pd.read_pickle(metadata_content)  # Ensure it's loaded as a DataFrame
            except Exception as e:
                print(f"Error loading metadata from backup URL: {e}")
                self.metadata = pd.DataFrame()  # Fallback to an empty DataFrame if all loading fails

        # Save the metadata if needed
        if filename and not self.metadata.empty:
            self.metadata.to_csv(filename, sep=";", index=False)



    def load_metadata(self, filename="metadata.csv"):
        """Load the metadata saved as a .csv file into Python."""
        self.metadata = pd.read_csv(filename, delimiter=";")

    def save_metadata(self, filename="metadata_new.csv"):
        """Save the metadata in self.metadata as a .csv file."""
        self.metadata.to_csv(filename, sep=";", index=False, index_label=False)

    def refine_metadata(self, filename=False):
        """Reduce metadata to those belonging to the series codes declared in self.codes."""
        if self.metadata.empty:
            self.get_metadata()
        indices = [self.metadata.index[self.metadata.iloc[:, 0] == k].tolist()[0] for k in self.codes]
        self.metadata = self.metadata.loc[indices]
        if filename:
            self.save_metadata(filename)
