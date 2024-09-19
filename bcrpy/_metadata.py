import pandas as pd
import requests
import pickle

class MetadataHandler:
    def get_metadata(self, filename="metadata.csv"):
        """Extract all metadata from BCRPData."""
        
        # Load metadata from the URL
        try:
            self.metadata = pd.read_csv('https://estadisticas.bcrp.gob.pe/estadisticas/series/metadata', delimiter=';', encoding='latin-1')
        except Exception as e:
            print(f"Error loading metadata from the primary URL: {e}")
            self.metadata = pd.DataFrame()  

        if self.metadata.shape[0] <= 5:
            print("Warning: metadata contains fewer than 5 rows, likely empty or incomplete")
            
            # Load metadata from the backup URL using pickle
            url = "https://github.com/andrewrgarcia/bcrpy/raw/main/metadatos"
            try:
                self.metadata = pickle.loads(requests.get(url).content)
            except Exception as e:
                print(f"Error loading metadata from backup URL: {e}")
                return  # Exit the function if both URLs fail

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
