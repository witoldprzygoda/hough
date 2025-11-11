"""
Peak detection service.

Encapsulates peak finding algorithms and operations.
"""

import gc
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from scipy.ndimage import gaussian_filter
from scipy.spatial.distance import cdist

from domain.peak import Peak, PeakCollection
from config.analysis_config import PeakDetectionConfig


class PeakDetectorService:
    """
    Service for detecting peaks in 2D Hough accumulator.

    Responsibilities:
    - Detect local maxima in 2D arrays
    - Apply smoothing and thresholds
    - Merge nearby peaks
    """

    def __init__(self, config: PeakDetectionConfig):
        """
        Initialize peak detector with configuration.

        Args:
            config: Peak detection configuration
        """
        self._config = config

    def find_peaks(self, histogram) -> PeakCollection:
        """
        Find peaks in a 2D histogram.

        Args:
            histogram: Uproot histogram object

        Returns:
            PeakCollection containing detected peaks
        """
        values, xedges, yedges = histogram.to_numpy()
        values = values.T
        values = np.nan_to_num(values, nan=0.0, posinf=0.0, neginf=0.0)

        # Apply smoothing if configured
        if self._config.smooth_sigma > 0:
            values = gaussian_filter(values, sigma=self._config.smooth_sigma)

        # Detect peaks
        coords = self._vectorized_sliding_peaks(
            values,
            min_height=self._config.threshold_abs,
            window_size=2 * self._config.min_distance
        )

        # Convert coordinates to peak objects
        xcenters = 0.5 * (xedges[1:] + xedges[:-1])
        ycenters = 0.5 * (yedges[1:] + yedges[:-1])

        peaks = []
        for (y_idx, x_idx) in coords:
            peak = Peak(
                x=float(xcenters[x_idx]),
                y=float(ycenters[y_idx]),
                height=float(values[y_idx, x_idx])
            )
            peaks.append(peak)

        # Cleanup
        del xedges, yedges, xcenters, ycenters, coords
        gc.collect()

        return PeakCollection(peaks)

    def _vectorized_sliding_peaks(self, matrix: np.ndarray,
                                   min_height: float = 6,
                                   window_size: int = 5) -> np.ndarray:
        """
        Vectorized sliding window peak detection.

        Args:
            matrix: 2D array to search for peaks
            min_height: Minimum height threshold
            window_size: Size of sliding window

        Returns:
            Array of peak coordinates
        """
        if window_size % 2 == 0:
            window_size += 1

        half_window = window_size // 2

        # Create sliding window view
        windows_2d = sliding_window_view(matrix, (window_size, window_size))

        # Extract center values
        center_r, center_c = half_window, half_window
        center_values = windows_2d[:, :, center_r, center_c]

        # Vectorized peak detection
        is_peak = np.ones_like(center_values, dtype=bool)

        # Check if center is maximum
        window_maxima = np.max(windows_2d, axis=(2, 3))
        is_peak &= (center_values == window_maxima)

        # Check minimum height
        is_peak &= (center_values >= min_height)

        # Get coordinates
        peak_rows, peak_cols = np.where(is_peak)
        adjusted_rows = peak_rows + half_window
        adjusted_cols = peak_cols + half_window

        # Merge close peaks
        if len(adjusted_rows) > 0:
            peak_coords = np.stack((adjusted_rows, adjusted_cols), axis=1)
            peak_values = matrix[adjusted_rows, adjusted_cols]

            # Calculate distances
            distances = cdist(peak_coords, peak_coords)
            close_pairs = np.where(
                (distances > 0) & (distances <= self._config.min_distance)
            )

            # Keep highest peaks
            peaks_to_keep = set(range(len(peak_coords)))

            for i, j in zip(close_pairs[0], close_pairs[1]):
                if i < j and i in peaks_to_keep and j in peaks_to_keep:
                    if peak_values[i] >= peak_values[j]:
                        peaks_to_keep.remove(j)
                    else:
                        peaks_to_keep.remove(i)

            peaks_to_keep = sorted(peaks_to_keep)
            merged_rows = adjusted_rows[peaks_to_keep]
            merged_cols = adjusted_cols[peaks_to_keep]

            return np.stack((merged_rows, merged_cols), axis=1)
        else:
            return np.empty((0, 2), dtype=int)
