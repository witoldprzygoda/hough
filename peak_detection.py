"""
Peak detection algorithms for Hough transform analysis.
"""

import gc
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from scipy.ndimage import gaussian_filter
from scipy.spatial.distance import cdist

from config import MIN_DISTANCE


def vectorized_2d_sliding_peaks(matrix, min_height=6, window_size=5):
    """
    Fully vectorized sliding window peak detection for 2D arrays.

    Parameters:
    -----------
    matrix : numpy.ndarray
        2D array to search for peaks
    min_height : float
        Minimum height threshold for peaks
    window_size : int
        Size of sliding window (will be made odd if even)

    Returns:
    --------
    numpy.ndarray
        Array of peak coordinates (row, col)
    """
    if window_size % 2 == 0:
        window_size += 1  # Ensure odd window size

    half_window = window_size // 2
    peaks = []

    # Create 2D sliding window view - this is the key optimization
    # Shape: (rows, cols, window_size, window_size)
    windows_2d = sliding_window_view(matrix, (window_size, window_size))

    # Center position in each window
    center_r, center_c = half_window, half_window

    # Extract center values and neighbors
    center_values = windows_2d[:, :, center_r, center_c]

    # Vectorized peak detection conditions
    is_peak = np.ones_like(center_values, dtype=bool)

    # Check if center is maximum in the window
    window_maxima = np.max(windows_2d, axis=(2, 3))
    is_peak &= (center_values == window_maxima)

    # Check minimum height
    is_peak &= (center_values >= min_height)

    # Get coordinates of peaks
    peak_rows, peak_cols = np.where(is_peak)

    # Adjust coordinates (sliding window shifts indices)
    adjusted_rows = peak_rows + half_window
    adjusted_cols = peak_cols + half_window

    # Merge close peaks
    if len(adjusted_rows) > 0:
        # Create array of peak coordinates and values
        peak_coords = np.stack((adjusted_rows, adjusted_cols), axis=1)
        peak_values = matrix[adjusted_rows, adjusted_cols]

        # Calculate distance matrix between all peaks
        distances = cdist(peak_coords, peak_coords)

        # Find peaks that are too close to each other
        close_pairs = np.where((distances > 0) & (distances <= MIN_DISTANCE))

        # Create a set of peaks to keep (initially all)
        peaks_to_keep = set(range(len(peak_coords)))

        # Merge close peaks by keeping the one with highest value
        for i, j in zip(close_pairs[0], close_pairs[1]):
            if i < j and i in peaks_to_keep and j in peaks_to_keep:
                if peak_values[i] >= peak_values[j]:
                    peaks_to_keep.remove(j)
                else:
                    peaks_to_keep.remove(i)

        # Convert back to sorted list of indices
        peaks_to_keep = sorted(peaks_to_keep)

        # Get the merged peaks
        merged_rows = adjusted_rows[peaks_to_keep]
        merged_cols = adjusted_cols[peaks_to_keep]

        return np.stack((merged_rows, merged_cols), axis=1)
    else:
        return np.empty((0, 2), dtype=int)


def find_local_maxima_2d(hist_obj, threshold_abs=None, threshold_rel=0.1,
                          min_distance=5, smooth_sigma=1.5):
    """
    Find local maxima in a 2D ROOT histogram (TH2F/TH2D).

    Parameters:
    -----------
    hist_obj : uproot histogram object
        2D histogram from ROOT file
    threshold_abs : float
        Absolute threshold for peak detection
    threshold_rel : float
        Relative threshold (fraction of maximum)
    min_distance : int
        Minimum distance between peaks
    smooth_sigma : float
        Gaussian smoothing sigma (0 for no smoothing)

    Returns:
    --------
    tuple
        (peaks, values) where peaks is list of (x, y, height) tuples
        and values is the 2D array
    """
    values, xedges, yedges = hist_obj.to_numpy()
    values = values.T
    values = np.nan_to_num(values, nan=0.0, posinf=0.0, neginf=0.0)

    # Smooth histogram to suppress noise
    if smooth_sigma > 0:
        values = gaussian_filter(values, sigma=smooth_sigma)

    # Find peaks
    coords = vectorized_2d_sliding_peaks(values, min_height=threshold_abs,
                                          window_size=2*min_distance)

    xcenters = 0.5 * (xedges[1:] + xedges[:-1])
    ycenters = 0.5 * (yedges[1:] + yedges[:-1])

    peaks = []
    for (y_idx, x_idx) in coords:
        peaks.append((xcenters[x_idx], ycenters[y_idx], values[y_idx, x_idx]))

    del xedges, yedges, xcenters, ycenters, coords
    gc.collect()

    return peaks, values
