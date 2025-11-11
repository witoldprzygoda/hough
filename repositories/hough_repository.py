"""
Repository for Hough accumulator data.
"""

from pathlib import Path
from typing import List, Tuple, Iterator
import uproot


class HoughHistogram:
    """Value object representing a Hough histogram."""

    def __init__(self, name: str, histogram, event_id: int, slice_num: int):
        """
        Initialize Hough histogram.

        Args:
            name: Histogram name
            histogram: Uproot histogram object
            event_id: Event identifier
            slice_num: Slice number
        """
        self.name = name
        self.histogram = histogram
        self.event_id = event_id
        self.slice_num = slice_num


class HoughRepository:
    """
    Repository for accessing Hough accumulator data from ROOT files.

    Responsibilities:
    - Find and open ROOT files with Hough data
    - Load histograms efficiently
    - Parse event and slice information
    """

    def __init__(self, data_path: Path):
        """
        Initialize repository with data path.

        Args:
            data_path: Path to directory containing Hough ROOT files
        """
        self._data_path = data_path

    def find_files(self, pattern: str = "out*.root") -> List[Path]:
        """
        Find Hough ROOT files.

        Args:
            pattern: Glob pattern for file matching

        Returns:
            Sorted list of file paths
        """
        root_files = sorted(self._data_path.glob(pattern))
        print(f"Found {len(root_files)} ROOT files in {self._data_path}\n")
        return root_files

    def iter_histograms(self, file_path: Path) -> Iterator[HoughHistogram]:
        """
        Iterate over 2D histograms in a ROOT file.

        Args:
            file_path: Path to ROOT file

        Yields:
            HoughHistogram objects
        """
        with uproot.open(file_path) as f:
            for key in f.keys():
                obj = f[key]

                if not obj.classname.startswith("TH2"):
                    continue

                # Parse event and slice information
                event_id, slice_num = self._parse_histogram_name(key)

                yield HoughHistogram(
                    name=key,
                    histogram=obj,
                    event_id=event_id,
                    slice_num=slice_num
                )

    def _parse_histogram_name(self, name: str) -> Tuple[int, int]:
        """
        Parse event and slice number from histogram name.

        Args:
            name: Histogram name

        Returns:
            Tuple of (event_id, slice_number)
        """
        # Split by common delimiters
        parts = name.replace('_', ';').split(';')
        return int(parts[1]), int(parts[2])
