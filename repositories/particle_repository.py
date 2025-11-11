"""
Repository for particle simulation data.

Implements Repository pattern for particle data access.
"""

from pathlib import Path
from typing import List
import pandas as pd
import uproot

from domain.track import Track, TrackCollection
from domain.particle import ParticleChargeRegistry


class ParticleRepository:
    """
    Repository for accessing particle simulation data from ROOT files.

    Responsibilities:
    - Load particle data from ROOT files
    - Convert raw data to domain models
    - Cache loaded data
    """

    def __init__(self, data_path: Path):
        """
        Initialize repository with data path.

        Args:
            data_path: Path to directory containing particle ROOT files
        """
        self._data_path = data_path
        self._charge_registry = ParticleChargeRegistry()
        self._cached_df: pd.DataFrame = None

    def load_particles(self, pattern: str = "particles*.root") -> pd.DataFrame:
        """
        Load particle data from ROOT files.

        Args:
            pattern: Glob pattern for file matching

        Returns:
            DataFrame with particle data
        """
        root_files = sorted(self._data_path.glob(pattern))

        if not root_files:
            raise FileNotFoundError(
                f"No files matching '{pattern}' found in {self._data_path}"
            )

        print(f"Found {len(root_files)} ROOT files in {self._data_path}\n")

        # Load from last file (following original logic)
        for file in root_files:
            print(f"📁 {file.name}")
            tree = uproot.open(file)["particles"]
            arrays = tree.arrays(library="np")

        # Convert to DataFrame
        df = pd.DataFrame(arrays)
        self._cached_df = df

        print("\nColumn names:")
        print(list(df.columns))

        return df

    def get_tracks_for_event(self, event_id: int, df: pd.DataFrame = None,
                             nbin_phi: int = 7000, nbin_qpt: int = 216,
                             min_hits: int = 4) -> TrackCollection:
        """
        Extract tracks for a specific event.

        Args:
            event_id: Event identifier
            df: DataFrame with particle data (uses cached if None)
            nbin_phi: Number of phi bins
            nbin_qpt: Number of q/pT bins
            min_hits: Minimum number of hits required

        Returns:
            TrackCollection for the event
        """
        if df is None:
            df = self._cached_df

        if df is None:
            raise ValueError("No data loaded. Call load_particles() first.")

        tracks = []

        for row in df.itertuples(index=False):
            if row.event_id != event_id:
                continue

            # Get charges for particles
            charges = self._get_charges(row.particle_type)

            # Create mask for charged particles with sufficient hits
            import numpy as np
            mask = (np.array(charges) != 0) & (np.array(row.number_of_hits) > min_hits)

            if not np.any(mask):
                continue

            # Calculate bin positions
            phi = row.phi
            phi_bin = (phi + np.pi) * nbin_phi / (2.0 * np.pi)

            curv = np.array(charges) / row.pt
            curv_bin = int(nbin_qpt / 2.0) + curv * int(nbin_qpt / 2.0)

            # Apply mask and create tracks
            for i in np.where(mask)[0]:
                track = Track(
                    event_id=event_id,
                    phi_bin=float(phi_bin[i]),
                    curv_bin=float(curv_bin[i]),
                    eta=float(row.eta[i]),
                    vz=float(row.vz[i]),
                    number_of_hits=int(row.number_of_hits[i]),
                    pz_over_pt=float(row.pz[i] / row.pt[i]),
                    particle_type=int(row.particle_type[i]),
                    phi=float(row.phi[i]),
                    pt=float(row.pt[i]),
                    pz=float(row.pz[i]),
                    is_reconstructed=False
                )
                tracks.append(track)

        return TrackCollection(tracks)

    def get_all_events(self, df: pd.DataFrame = None) -> List[int]:
        """
        Get list of all event IDs.

        Args:
            df: DataFrame with particle data (uses cached if None)

        Returns:
            List of event IDs
        """
        if df is None:
            df = self._cached_df

        if df is None:
            raise ValueError("No data loaded. Call load_particles() first.")

        return df["event_id"].unique().tolist()

    def create_tracks_dict(self, nbin_phi: int = 7000, nbin_qpt: int = 216,
                          min_hits: int = 4) -> dict:
        """
        Create dictionary mapping event_id to TrackCollection.

        Args:
            nbin_phi: Number of phi bins
            nbin_qpt: Number of q/pT bins
            min_hits: Minimum number of hits required

        Returns:
            Dictionary mapping event_id to TrackCollection
        """
        if self._cached_df is None:
            raise ValueError("No data loaded. Call load_particles() first.")

        tracks_dict = {}
        event_ids = self.get_all_events()

        for event_id in event_ids:
            tracks_dict[event_id] = self.get_tracks_for_event(
                event_id, self._cached_df, nbin_phi, nbin_qpt, min_hits
            )

        return tracks_dict

    def _get_charges(self, particle_types) -> List[float]:
        """Get charges for particle types."""
        charges = []
        for pid in particle_types:
            charge = self._charge_registry.get_charge_safe(pid)
            charges.append(charge)
        return charges

    def save_tracks_to_root(self, tracks_dict: dict, event_list: List[int],
                           filename: str, treename: str = "ntuple") -> pd.DataFrame:
        """
        Save tracks to ROOT file.

        Args:
            tracks_dict: Dictionary mapping event_id to TrackCollection
            event_list: List of events to include
            filename: Output ROOT file name
            treename: Name of the TTree

        Returns:
            Combined DataFrame
        """
        combined_dfs = []

        for event_id in event_list:
            if event_id in tracks_dict:
                collection = tracks_dict[event_id]
                df = collection.to_dataframe()
                if not df.empty:
                    combined_dfs.append(df)

        if not combined_dfs:
            raise ValueError("No tracks to save")

        combined_df = pd.concat(combined_dfs, ignore_index=True)

        print(f"Combined DataFrame shape: {combined_df.shape}")
        print(f"Columns: {combined_df.columns.tolist()}")

        # Save as ROOT ntuple
        with uproot.recreate(filename) as file:
            file[treename] = combined_df.to_dict(orient='list')

        print(f"Successfully saved to {filename}")
        return combined_df
