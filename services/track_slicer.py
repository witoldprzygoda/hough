"""
Track slicing service.

Implements track slicing with configurable easing strategies.
"""

from typing import Tuple, Optional

from domain.track import TrackCollection
from strategies.easing_strategy import EasingStrategy, EasingStrategyFactory
from config.analysis_config import HoughConfig, ProcessingConfig


class TrackSlicerService:
    """
    Service for slicing tracks based on cotangent ranges.

    Responsibilities:
    - Apply easing functions to calculate slice bounds
    - Filter tracks by slice criteria
    - Support multiple easing strategies
    """

    def __init__(self, easing_strategy: EasingStrategy,
                 hough_config: HoughConfig,
                 processing_config: ProcessingConfig):
        """
        Initialize track slicer.

        Args:
            easing_strategy: Strategy for easing calculations
            hough_config: Hough configuration
            processing_config: Processing configuration
        """
        self._easing = easing_strategy
        self._hough_config = hough_config
        self._processing_config = processing_config

    def get_slice_bounds(self, slice_num: int) -> Tuple[Optional[float], Optional[float]]:
        """
        Get cotangent bounds for a slice.

        Args:
            slice_num: Slice number (-1 for full range, 0-32 for specific slices)

        Returns:
            Tuple of (lo_cot, hi_cot) bounds
        """
        if slice_num == -1:
            return None, None
        else:
            lo_cot = self._easing.ease(-32.0 + 2.0 * max(slice_num, 0))
            hi_cot = self._easing.ease(-32.0 + 2.0 * min(slice_num + 1, 32))
            return lo_cot, hi_cot

    def filter_tracks_for_slice(self, tracks: TrackCollection,
                                 slice_num: int) -> TrackCollection:
        """
        Filter tracks that belong to a specific slice.

        Args:
            tracks: Collection of tracks to filter
            slice_num: Slice number

        Returns:
            Filtered TrackCollection
        """
        vz_min, vz_max = self._processing_config.vz_range

        if slice_num > -1:
            # Specific slice (0-32)
            lo_cot, _ = self.get_slice_bounds(0)
            _, hi_cot = self.get_slice_bounds(32)

            filtered = tracks.filter_by_vz_range(vz_min, vz_max)
            filtered = filtered.filter_by_cot_range(lo_cot, hi_cot)

        else:
            # Slice -1: special range
            lo_cot, _ = self.get_slice_bounds(10)
            _, hi_cot = self.get_slice_bounds(22)

            filtered = tracks.filter_by_vz_range(vz_min, vz_max)
            filtered = filtered.filter_by_cot_range(lo_cot, hi_cot)

            # Additional filtering for slice -1
            size = self._hough_config.square_size
            nbin_qpt = self._hough_config.nbin_qpt

            # Filter by curv_bin range
            final_tracks = []
            for track in filtered:
                if (track.curv_bin > 0 + size and
                    track.curv_bin < nbin_qpt - size):
                    final_tracks.append(track)

            from domain.track import Track
            filtered = TrackCollection(final_tracks)

        return filtered

    @classmethod
    def create(cls, easing_type: str, hough_config: HoughConfig,
              processing_config: ProcessingConfig) -> 'TrackSlicerService':
        """
        Factory method to create TrackSlicerService with named strategy.

        Args:
            easing_type: Name of easing strategy
            hough_config: Hough configuration
            processing_config: Processing configuration

        Returns:
            TrackSlicerService instance
        """
        strategy = EasingStrategyFactory.create(easing_type)
        return cls(strategy, hough_config, processing_config)
