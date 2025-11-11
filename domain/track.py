"""
Track domain models for Hough transform analysis.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np
import pandas as pd


@dataclass
class Track:
    """
    Represents a track in the detector.

    Attributes:
        event_id: Event identifier
        phi_bin: Phi bin in Hough space
        curv_bin: Curvature bin in Hough space
        eta: Pseudorapidity
        vz: Vertex z-position
        number_of_hits: Number of detector hits
        pz_over_pt: Ratio of longitudinal to transverse momentum
        particle_type: PDG particle ID
        phi: Azimuthal angle
        pt: Transverse momentum
        pz: Longitudinal momentum
        is_reconstructed: Whether track was successfully reconstructed
    """
    event_id: int
    phi_bin: float
    curv_bin: float
    eta: float
    vz: float
    number_of_hits: int
    pz_over_pt: float
    particle_type: int
    phi: float
    pt: float
    pz: float
    is_reconstructed: bool = False

    @property
    def cotangent(self) -> float:
        """Get cotangent (same as pz_over_pt)."""
        return self.pz_over_pt

    def is_in_vz_range(self, vz_min: float, vz_max: float) -> bool:
        """Check if track is within vz range."""
        return vz_min < self.vz < vz_max

    def is_in_cot_range(self, cot_min: float, cot_max: float) -> bool:
        """Check if track is within cotangent range."""
        return cot_min < self.cotangent < cot_max

    def mark_reconstructed(self) -> None:
        """Mark track as successfully reconstructed."""
        self.is_reconstructed = True

    def to_dict(self) -> dict:
        """Convert track to dictionary."""
        return {
            'event_id': self.event_id,
            'phi_bin': self.phi_bin,
            'curv_bin': self.curv_bin,
            'eta': self.eta,
            'vz': self.vz,
            'number_of_hits': self.number_of_hits,
            'pz_over_pt': self.pz_over_pt,
            'particle_type': self.particle_type,
            'phi': self.phi,
            'pt': self.pt,
            'pz': self.pz,
            'reco': 1 if self.is_reconstructed else 0,
        }


class TrackCollection:
    """
    Collection of tracks with query and filtering operations.

    Implements the Repository pattern for in-memory track storage.
    """

    def __init__(self, tracks: List[Track] = None):
        """
        Initialize track collection.

        Args:
            tracks: Initial list of tracks
        """
        self._tracks: List[Track] = tracks if tracks is not None else []
        self._by_event: dict = {}
        self._rebuild_index()

    def _rebuild_index(self) -> None:
        """Rebuild event index for fast lookup."""
        self._by_event = {}
        for track in self._tracks:
            if track.event_id not in self._by_event:
                self._by_event[track.event_id] = []
            self._by_event[track.event_id].append(track)

    def add(self, track: Track) -> None:
        """Add a track to the collection."""
        self._tracks.append(track)
        if track.event_id not in self._by_event:
            self._by_event[track.event_id] = []
        self._by_event[track.event_id].append(track)

    def add_all(self, tracks: List[Track]) -> None:
        """Add multiple tracks to the collection."""
        for track in tracks:
            self.add(track)

    def __len__(self) -> int:
        """Return number of tracks."""
        return len(self._tracks)

    def __iter__(self):
        """Iterate over tracks."""
        return iter(self._tracks)

    def get_by_event(self, event_id: int) -> List[Track]:
        """
        Get all tracks for a specific event.

        Args:
            event_id: Event identifier

        Returns:
            List of tracks for the event
        """
        return self._by_event.get(event_id, [])

    def get_event_ids(self) -> List[int]:
        """Get list of unique event IDs."""
        return list(self._by_event.keys())

    def filter_by_hits(self, min_hits: int) -> 'TrackCollection':
        """
        Filter tracks by minimum number of hits.

        Args:
            min_hits: Minimum number of hits required

        Returns:
            New TrackCollection with filtered tracks
        """
        filtered = [t for t in self._tracks if t.number_of_hits > min_hits]
        return TrackCollection(filtered)

    def filter_by_vz_range(self, vz_min: float, vz_max: float) -> 'TrackCollection':
        """
        Filter tracks by vz range.

        Args:
            vz_min: Minimum vz value
            vz_max: Maximum vz value

        Returns:
            New TrackCollection with filtered tracks
        """
        filtered = [t for t in self._tracks if t.is_in_vz_range(vz_min, vz_max)]
        return TrackCollection(filtered)

    def filter_by_cot_range(self, cot_min: float, cot_max: float) -> 'TrackCollection':
        """
        Filter tracks by cotangent range.

        Args:
            cot_min: Minimum cotangent value
            cot_max: Maximum cotangent value

        Returns:
            New TrackCollection with filtered tracks
        """
        filtered = [t for t in self._tracks if t.is_in_cot_range(cot_min, cot_max)]
        return TrackCollection(filtered)

    def get_reconstructed(self) -> 'TrackCollection':
        """Get only reconstructed tracks."""
        filtered = [t for t in self._tracks if t.is_reconstructed]
        return TrackCollection(filtered)

    def count_reconstructed(self) -> int:
        """Count number of reconstructed tracks."""
        return sum(1 for t in self._tracks if t.is_reconstructed)

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert collection to pandas DataFrame.

        Returns:
            DataFrame with track data
        """
        if not self._tracks:
            return pd.DataFrame()
        return pd.DataFrame([t.to_dict() for t in self._tracks])

    def to_array(self) -> np.ndarray:
        """
        Convert to numpy array.

        Returns:
            Numpy array with track information
        """
        if not self._tracks:
            return np.empty((0, 11))

        data = []
        for t in self._tracks:
            row = [
                t.phi_bin, t.curv_bin, t.eta, t.vz,
                t.number_of_hits, t.pz_over_pt, t.particle_type,
                t.phi, t.pt, t.pz,
                1 if t.is_reconstructed else 0
            ]
            data.append(row)
        return np.array(data)

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> 'TrackCollection':
        """
        Create TrackCollection from pandas DataFrame.

        Args:
            df: DataFrame with track data

        Returns:
            New TrackCollection instance
        """
        tracks = []
        for _, row in df.iterrows():
            track = Track(
                event_id=int(row.get('event_id', 0)),
                phi_bin=float(row['phi_bin']),
                curv_bin=float(row['curv_bin']),
                eta=float(row['eta']),
                vz=float(row['vz']),
                number_of_hits=int(row['number_of_hits']),
                pz_over_pt=float(row['pz_over_pt']),
                particle_type=int(row['particle_type']),
                phi=float(row['phi']),
                pt=float(row['pt']),
                pz=float(row['pz']),
                is_reconstructed=bool(row.get('reco', 0))
            )
            tracks.append(track)
        return cls(tracks)
