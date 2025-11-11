"""
Hough matching service.

Matches reconstructed peaks with true tracks and extracts training squares.
"""

import numpy as np
from typing import Tuple

from domain.peak import PeakCollection, Peak
from domain.track import TrackCollection
from domain.hough_square import (
    HoughSquare, HoughSquareCollection, SquareClassification
)
from config.analysis_config import HoughConfig


class HoughMatcherService:
    """
    Service for matching peaks with true tracks and extracting squares.

    Responsibilities:
    - Match reconstructed peaks with true tracks
    - Extract square regions around peaks
    - Classify squares as true/false positives
    """

    def __init__(self, config: HoughConfig):
        """
        Initialize matcher with configuration.

        Args:
            config: Hough configuration
        """
        self._config = config

    def match_and_extract_squares(
        self,
        accumulator_values: np.ndarray,
        reconstructed_peaks: PeakCollection,
        true_tracks: TrackCollection
    ) -> Tuple[HoughSquareCollection, np.ndarray]:
        """
        Match peaks with tracks and extract squares.

        Args:
            accumulator_values: 2D Hough accumulator array
            reconstructed_peaks: Collection of reconstructed peaks
            true_tracks: Collection of true tracks

        Returns:
            Tuple of (square_collection, assignment_mask)
            where assignment_mask indicates which true tracks were matched
        """
        square_collection = HoughSquareCollection()

        # Track which true tracks have been assigned
        assignment_mask = np.zeros(len(true_tracks), dtype=int)
        true_tracks_list = list(true_tracks)

        for peak in reconstructed_peaks:
            square, has_match, matched_idx = self._extract_and_classify_square(
                accumulator_values, peak, true_tracks_list, assignment_mask
            )

            if square is not None:
                square_collection.add_square(square)

                # Mark true track as matched
                if has_match and matched_idx is not None:
                    assignment_mask[matched_idx] = 1

        return square_collection, assignment_mask

    def _extract_and_classify_square(
        self,
        values: np.ndarray,
        peak: Peak,
        true_tracks: list,
        assignment_mask: np.ndarray
    ) -> Tuple[HoughSquare, bool, int]:
        """
        Extract square around peak and classify it.

        Args:
            values: Hough accumulator values
            peak: Peak to extract square around
            true_tracks: List of true tracks
            assignment_mask: Current assignment status

        Returns:
            Tuple of (square, has_match, matched_index)
        """
        size = self._config.square_size
        tolerance = self._config.tolerance

        # Calculate square bounds
        square_x = peak.x - size
        square_y = peak.y - size

        # Calculate center
        center_x = square_x + size
        center_y = square_y + size

        # Extract region
        x_start = max(0, int(square_y))
        x_end = min(values.shape[0], int(square_y + 2*size))
        y_start = max(0, int(square_x))
        y_end = min(values.shape[1], int(square_x + 2*size))

        if x_end <= x_start or y_end <= y_start:
            return None, False, None

        square_region = np.copy(values[x_start:x_end, y_start:y_end])

        # Check for correct size
        if square_region.shape != (2*size, 2*size):
            return None, False, None

        # Check for matching true track
        has_match = False
        matched_idx = None

        for idx, track in enumerate(true_tracks):
            # Skip if already assigned
            if assignment_mask[idx] > 0:
                continue

            # Create peak from track position
            track_peak = Peak(
                x=track.curv_bin,
                y=track.phi_bin,
                height=0  # Height not used for matching
            )

            # Check if within tolerance
            if peak.is_within_tolerance(track_peak, tolerance):
                has_match = True
                matched_idx = idx
                break

        # Create HoughSquare with classification
        classification = (
            SquareClassification.TRUE_POSITIVE if has_match
            else SquareClassification.FALSE_POSITIVE
        )

        square = HoughSquare(
            data=square_region.astype(int),
            classification=classification,
            center_x=center_x,
            center_y=center_y
        )

        return square, has_match, matched_idx

    def update_track_reconstruction_status(
        self,
        tracks: TrackCollection,
        assignment_mask: np.ndarray
    ) -> int:
        """
        Update reconstruction status of tracks based on assignment mask.

        Args:
            tracks: TrackCollection to update
            assignment_mask: Binary mask indicating matched tracks

        Returns:
            Number of newly reconstructed tracks
        """
        newly_reconstructed = 0

        for idx, track in enumerate(tracks):
            if assignment_mask[idx] > 0 and not track.is_reconstructed:
                track.mark_reconstructed()
                newly_reconstructed += 1

        return newly_reconstructed
