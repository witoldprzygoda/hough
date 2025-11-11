"""
Hough transform processing and matching functions.
"""

import gc
import numpy as np
import uproot
from pathlib import Path

from config import (SIZE, TOLERANCE, NBIN_QPT, THRESHOLD_ABS, THRESHOLD_REL,
                    MIN_DISTANCE, SMOOTH_SIGMA, SLICE_LIST)
from peak_detection import find_local_maxima_2d
from slicer import HoughSlicer


def event_slice(text):
    """
    Extract event and slice number from histogram name.

    Parameters:
    -----------
    text : str
        Histogram name containing event and slice info

    Returns:
    --------
    tuple
        (event_id, slice_number)
    """
    # Split by common delimiters and check for exact match
    parts = text.replace('_', ';').split(';')
    return int(parts[1]), int(parts[2])


def get_hough_squares(values, peaks, slice_num, true_peaks_with_mask,
                       true_squares, false_squares):
    """
    Extract square regions around peaks and classify them.

    Parameters:
    -----------
    values : numpy.ndarray
        Hough accumulator values
    peaks : list
        List of reconstructed peak coordinates
    slice_num : int
        Current slice number
    true_peaks_with_mask : tuple
        (true_peaks array, mask array)
    true_squares : list
        List to append true positive squares
    false_squares : list
        List to append false positive squares

    Returns:
    --------
    tuple
        (true_squares, false_squares, result_mask)
    """
    # true_peaks_with_mask is a tuple (true_peaks, mask)
    true_peaks, mask = true_peaks_with_mask

    # Process reconstructed peaks and extract squares
    # Mask of the true peaks assigned to the reconstructed peaks
    true_peaks_mask = np.zeros(len(true_peaks), dtype=int)

    for peak in peaks:
        square_x = peak[0] - SIZE
        square_y = peak[1] - SIZE

        # Calculate center of the square
        center_x = square_x + SIZE
        center_y = square_y + SIZE

        # Extract the square region from the values array
        x_start = max(0, int(square_y))
        x_end = min(values.shape[0], int(square_y + 2*SIZE))
        y_start = max(0, int(square_x))
        y_end = min(values.shape[1], int(square_x + 2*SIZE))

        # Copy the region to a new array
        if x_end > x_start and y_end > y_start:
            square_region = np.copy(values[x_start:x_end, y_start:y_end])

            # Check if there's a true peak within tolerance
            has_true_peak = False
            for i in range(true_peaks.shape[0]):
                true_x = true_peaks[i, 1]  # x coordinate of true peak
                true_y = true_peaks[i, 0]  # y coordinate

                # Calculate distance from center of square to true peak
                distance = np.sqrt((center_x - true_x)**2 + (center_y - true_y)**2)
                # One-to-one assignment between reconstructed peaks and true tracks
                if distance <= TOLERANCE and true_peaks_mask[i] < 0.5:
                    has_true_peak = True
                    true_peaks_mask[i] = 1

            # Classify as true or false square
            if square_region.shape == (2*SIZE, 2*SIZE):
                if has_true_peak:
                    true_squares.append(square_region.astype(int))
                else:
                    false_squares.append(square_region.astype(int))

    # Get indices in the original true_peaks array
    mask_indices = np.where(mask)[0]

    # Map back to original array indices
    result_indices = mask_indices[true_peaks_mask.astype(bool)]

    # Create an array of 0 and 1
    result_mask = np.zeros(len(mask))
    result_mask[result_indices.astype(int)] = 1

    return true_squares, false_squares, result_mask


def match_and_write(values, peaks, event, slice_num, truetracks,
                     true_squares, false_squares, n_truetracks, draw=True):
    """
    Match reconstructed peaks with true tracks and extract squares.

    Parameters:
    -----------
    values : numpy.ndarray
        Hough accumulator values
    peaks : list
        List of reconstructed peak coordinates
    event : int
        Event ID
    slice_num : int
        Slice number
    truetracks : dict
        Dictionary of true tracks
    true_squares : list
        List to append true positive squares
    false_squares : list
        List to append false positive squares
    n_truetracks : int
        Running count of true tracks
    draw : bool
        Whether to draw the Hough accumulator

    Returns:
    --------
    tuple
        (true_squares, false_squares, n_truetracks)
    """
    from visualization import draw_hough

    true_peaks = np.squeeze(np.array(truetracks[event]))

    # Create slicer and check whether the true track fits to the slice
    slicer = HoughSlicer(easing_type="InSquare")

    if slice_num > -1:  # slice 0-32
        lo_cot, _ = slicer(0)
        _, hi_cot = slicer(32)
        mask = ((abs(true_peaks[:, 3]) < 200) &
                (lo_cot < true_peaks[:, 5]) &
                (true_peaks[:, 5] < hi_cot))
    else:  # slice = -1
        lo_cot, _ = slicer(10)
        _, hi_cot = slicer(22)
        mask = ((abs(true_peaks[:, 3]) < 200) &
                (lo_cot < true_peaks[:, 5]) &
                (true_peaks[:, 5] < hi_cot) &
                (true_peaks[:, 1] > 0 + SIZE) &
                (true_peaks[:, 1] < NBIN_QPT - SIZE))

    # Increase the n_truetracks
    n_truetracks = n_truetracks + len(true_peaks[mask])

    if draw:
        draw_hough(values, peaks, slice_num, true_peaks[mask])

    # Get squares around peaks and indices of the associated true tracks
    true_squares, false_squares, result_mask = get_hough_squares(
        values, peaks, slice_num, (true_peaks[mask], mask),
        true_squares, false_squares)

    print(f"True tracks in event: {len(true_peaks[mask])}, "
          f"True peaks total: {len(true_squares)}")
    print(f"Number of ones in result_mask: {np.count_nonzero(result_mask)}")

    # Fill the "reco" column in truetracks marking the reconstructed true tracks
    if len(result_mask) == len(truetracks[event]):
        truetracks[event]['reco'] = (result_mask.astype(int) |
                                      truetracks[event]['reco'].astype(int))
    else:
        print(f"Error! Length of truetracks[event]['reco'] and result_mask differ: "
              f"{len(truetracks[event]['reco'])}, {len(result_mask)}")

    print(f"Number of ones in reco: {np.count_nonzero(truetracks[event]['reco'])}")

    return true_squares, false_squares, n_truetracks


def process_root_file(file_path, truetracks, true_squares, false_squares,
                       event_list, n_truetracks):
    """
    Process a single ROOT file and find peaks in all 2D histograms.

    Parameters:
    -----------
    file_path : Path
        Path to ROOT file
    truetracks : dict
        Dictionary of true tracks
    true_squares : list
        List of true positive squares
    false_squares : list
        List of false positive squares
    event_list : list
        List of processed events
    n_truetracks : int
        Running count of true tracks

    Returns:
    --------
    tuple
        (true_squares, false_squares, event_list, n_truetracks)
    """
    print(f"Processing file: {file_path}")

    results = {}
    ikey = 0

    with uproot.open(file_path) as f:
        for key in f.keys():  # iterate only over keys
            ikey += 1

            obj = f[key]  # load only one object at a time

            if not obj.classname.startswith("TH2"):
                continue

            # Find true maxima
            event, slice_num = event_slice(key)

            # Add event into the event list
            if event not in event_list:
                event_list.append(event)
                print(f"Event: {event}")

            # Match true and found peaks
            if slice_num in SLICE_LIST:
                peaks, values = find_local_maxima_2d(
                    obj,
                    threshold_abs=THRESHOLD_ABS,
                    threshold_rel=THRESHOLD_REL,
                    min_distance=MIN_DISTANCE,
                    smooth_sigma=SMOOTH_SIGMA)

                print(f"####### Slice number: {slice_num}")
                print(f"Peaks: {len(peaks)}")

                true_squares, false_squares, n_truetracks = match_and_write(
                    values, peaks, event, slice_num, truetracks,
                    true_squares, false_squares, n_truetracks, ikey < 200)

                del values

            # Cleanup per histogram
            del obj
            gc.collect()

    gc.collect()
    return true_squares, false_squares, event_list, n_truetracks
