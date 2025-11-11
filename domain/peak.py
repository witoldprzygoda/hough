"""
Peak domain models for Hough transform analysis.
"""

from dataclasses import dataclass
from typing import List, Tuple
import numpy as np


@dataclass(frozen=True)
class Peak:
    """
    Immutable value object representing a peak in Hough space.

    Attributes:
        x: X-coordinate (curv_bin)
        y: Y-coordinate (phi_bin)
        height: Peak height/intensity
    """
    x: float
    y: float
    height: float

    def distance_to(self, other: 'Peak') -> float:
        """
        Calculate Euclidean distance to another peak.

        Args:
            other: Another Peak instance

        Returns:
            Euclidean distance
        """
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def is_within_tolerance(self, other: 'Peak', tolerance: float) -> bool:
        """
        Check if another peak is within tolerance distance.

        Args:
            other: Another Peak instance
            tolerance: Distance tolerance

        Returns:
            True if within tolerance, False otherwise
        """
        return self.distance_to(other) <= tolerance

    def to_tuple(self) -> Tuple[float, float, float]:
        """Convert to tuple representation."""
        return (self.x, self.y, self.height)


class PeakCollection:
    """
    Collection of peaks with operations.

    Implements the Collection pattern.
    """

    def __init__(self, peaks: List[Peak] = None):
        """
        Initialize peak collection.

        Args:
            peaks: Initial list of peaks
        """
        self._peaks: List[Peak] = peaks if peaks is not None else []

    def add(self, peak: Peak) -> None:
        """Add a peak to the collection."""
        self._peaks.append(peak)

    def __len__(self) -> int:
        """Return number of peaks."""
        return len(self._peaks)

    def __iter__(self):
        """Iterate over peaks."""
        return iter(self._peaks)

    def __getitem__(self, index: int) -> Peak:
        """Get peak by index."""
        return self._peaks[index]

    def filter_by_height(self, min_height: float) -> 'PeakCollection':
        """
        Filter peaks by minimum height.

        Args:
            min_height: Minimum peak height threshold

        Returns:
            New PeakCollection with filtered peaks
        """
        filtered = [p for p in self._peaks if p.height >= min_height]
        return PeakCollection(filtered)

    def find_nearest(self, target: Peak) -> Tuple[Peak, float]:
        """
        Find nearest peak to target.

        Args:
            target: Target peak

        Returns:
            Tuple of (nearest_peak, distance)
        """
        if not self._peaks:
            raise ValueError("Cannot find nearest peak in empty collection")

        nearest = min(self._peaks, key=lambda p: target.distance_to(p))
        return nearest, target.distance_to(nearest)

    def find_within_tolerance(self, target: Peak, tolerance: float) -> List[Peak]:
        """
        Find all peaks within tolerance of target.

        Args:
            target: Target peak
            tolerance: Distance tolerance

        Returns:
            List of peaks within tolerance
        """
        return [p for p in self._peaks if target.is_within_tolerance(p, tolerance)]

    def to_array(self) -> np.ndarray:
        """
        Convert to numpy array.

        Returns:
            Numpy array of shape (n_peaks, 3) with columns (x, y, height)
        """
        if not self._peaks:
            return np.empty((0, 3))
        return np.array([p.to_tuple() for p in self._peaks])

    @classmethod
    def from_array(cls, arr: np.ndarray) -> 'PeakCollection':
        """
        Create PeakCollection from numpy array.

        Args:
            arr: Numpy array of shape (n, 3) with columns (x, y, height)

        Returns:
            New PeakCollection instance
        """
        peaks = [Peak(x=row[0], y=row[1], height=row[2]) for row in arr]
        return cls(peaks)

    @classmethod
    def from_tuples(cls, tuples: List[Tuple[float, float, float]]) -> 'PeakCollection':
        """
        Create PeakCollection from list of tuples.

        Args:
            tuples: List of (x, y, height) tuples

        Returns:
            New PeakCollection instance
        """
        peaks = [Peak(x=t[0], y=t[1], height=t[2]) for t in tuples]
        return cls(peaks)
