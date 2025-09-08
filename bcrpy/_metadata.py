import os, json, datetime
import pandas as pd
import requests

class MetadataHandler:
    def get_metadata(self, filename="metadata.csv", max_age_days=9, auto_refresh_days=30, force=False):
        """
        Fetch BCRP metadata if missing, stale, or forced.
        
        Rules:
        - If metadata exists and is < max_age_days old → use it silently.
        - If >= max_age_days but < auto_refresh_days → warn the user (manual refresh).
        - If >= auto_refresh_days → automatically redownload fresh copy.
        - If 'force=True' → always redownload.
        """

        sidecar = filename + ".meta"

        if not force and os.path.exists(filename):
            try:
                if os.path.exists(sidecar):
                    meta = json.load(open(sidecar))
                    ts = datetime.datetime.fromisoformat(meta["downloaded_at"])
                    age_days = (datetime.datetime.utcnow() - ts).days

                    if age_days >= auto_refresh_days:
                        print(f"♻️ Metadata is {age_days} days old → auto-refreshing...")
                        return self._download_metadata(filename, sidecar)

                    elif age_days >= max_age_days:
                        print(
                            f"⚠️ Metadata is {age_days} days old. "
                            f"Delete {filename} to fetch a fresh copy."
                        )
                # Use existing metadata
                self.metadata = pd.read_csv(filename, delimiter=";")
                return self.metadata

            except Exception as e:
                print(f"Error reading cached metadata, refetching: {e}")
                return self._download_metadata(filename, sidecar)

        # No cache or forced
        return self._download_metadata(filename, sidecar)


    def _download_metadata(self, filename, sidecar):
        """Helper: download and cache metadata with timestamp."""
        try:
            self.metadata = pd.read_csv(
                "https://estadisticas.bcrp.gob.pe/estadisticas/series/metadata",
                delimiter=";", encoding="latin-1"
            )
            self.metadata.to_csv(filename, sep=";", index=False)
            with open(sidecar, "w") as f:
                json.dump({"downloaded_at": datetime.datetime.utcnow().isoformat()}, f)
            print("✅ Metadata downloaded and cached.")
        except Exception as e:
            print(f"Error fetching metadata: {e}")
            self.metadata = pd.DataFrame()
        return self.metadata


    def load_metadata(self, filename="metadata.csv", max_age_days=9, auto_refresh_days=30):
        """
        Load metadata safely, with staleness checks.
        Delegates to get_metadata() so warnings/auto-refresh still apply.
        """
        return self.get_metadata(filename=filename,
                                 max_age_days=max_age_days,
                                 auto_refresh_days=auto_refresh_days,
                                 force=False)

    def save_metadata(self, filename="metadata_snapshot.csv"):
        """
        Save the current metadata to disk.
        Useful for archiving or exporting refined subsets.
        """
        if self.metadata.empty:
            raise ValueError("⚠️ No metadata available to save. Run get_metadata() first.")
        self.metadata.to_csv(filename, sep=";", index=False)
        print(f"✅ Metadata saved to {filename}")

    def refine_metadata(self, filename=None, inplace=True):
        """
        Reduce metadata to rows belonging to the codes declared in self.codes.
        
        Parameters
        ----------
        filename : str, optional
            If provided, save the refined metadata to this file.
        inplace : bool, optional
            If True, replace self.metadata with the refined version (default).
            If False, return the refined DataFrame without overwriting self.metadata.
        """
        if self.metadata.empty:
            self.get_metadata()

        mask = self.metadata.iloc[:, 0].isin(self.codes)
        refined = self.metadata[mask]

        missing = [c for c in self.codes if c not in refined.iloc[:, 0].tolist()]
        if missing:
            print(f"⚠️ Warning: {len(missing)} codes not found in metadata: {missing}")

        if inplace:
            self.metadata = refined
            if filename:
                self.save_metadata(filename)
            return self.metadata
        else:
            if filename:
                refined.to_csv(filename, sep=";", index=False)
            return refined