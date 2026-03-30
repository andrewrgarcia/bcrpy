from bcrpy._fetcher import Fetcher
from bcrpy._metadata import MetadataHandler
from bcrpy.tools import MetadataTools


class Marco(Fetcher, MetadataHandler):
    def __init__(self, verbose=True):
        super().__init__(verbose=verbose)

    def tools(self):
        if self.metadata.empty:
            self.get_metadata()
        return MetadataTools(self.metadata)