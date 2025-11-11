"""
Visualization functions for Hough transform analysis.
"""

import gc
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from config import SIZE, VIS_START_PHI, VIS_END_PHI, VIS_SIZE_TRUE


def draw_hough(values, peaks, slice_num, true_peaks):
    """
    Draw Hough accumulator with reconstructed and true peaks.

    Parameters:
    -----------
    values : numpy.ndarray
        Hough accumulator values
    peaks : list
        List of reconstructed peak coordinates (x, y, height)
    slice_num : int
        Slice number
    true_peaks : numpy.ndarray
        Array of true peak information
    """
    start_phi = VIS_START_PHI
    end_phi = VIS_END_PHI
    size_true = VIS_SIZE_TRUE

    # Create a figure and axes, then display the image
    fig, ax = plt.subplots(figsize=(16, 2*12))
    im = ax.imshow(values[start_phi:end_phi, :], cmap='viridis',
                   interpolation='nearest')

    # Adjust the aspect ratio to allow non-square cells
    ax = plt.gca()  # Get the current axes
    ax.set_aspect('auto')  # Allow non-square pixels

    plt.colorbar(im, label="Counts")  # Add color bar for values
    ax.set_xlabel("q/pT")
    ax.set_ylabel("phi")
    ax.set_title("Hough accumulator")

    # Patch a square around reco peaks
    for peak in peaks:
        # Define the square's properties
        square_x = peak[0] - SIZE  # Bottom-left x-coordinate
        square_y = peak[1] - start_phi - SIZE  # Bottom-left y-coordinate

        # Create a Rectangle patch
        square = patches.Rectangle((square_x, square_y), 2*SIZE, 2*SIZE,
                                    linewidth=3, edgecolor='red', facecolor='none')

        # Add the square to the axes
        ax.add_patch(square)

    # Patch a small square around true peaks
    print(f"True peaks shape: {true_peaks.shape}")

    # Get axis limits (image boundaries)
    xmin, xmax = ax.get_xlim()
    ymax, ymin = ax.get_ylim()

    for i in range(true_peaks.shape[0]):
        # Define the square's properties
        square_x = int(true_peaks[i, 1]) - size_true  # Bottom-left x-coordinate
        square_y = int(true_peaks[i, 0]) - start_phi - size_true  # Bottom-left y-coordinate

        # Create a Rectangle patch
        square = patches.Rectangle((square_x, square_y), 2*size_true, 2*size_true,
                                    linewidth=3, edgecolor="yellow", facecolor='none')

        ax.add_patch(square)

        # Draw number of hits directly on ax
        if xmin < square_x < xmax and ymin < square_y < ymax:
            ax.text(square_x, square_y,
                    f"{int(true_peaks[i, 6])} {round(true_peaks[i, 5], 1)}",
                    fontsize=10, color='white', fontweight='bold')

    plt.show()

    del values
    gc.collect()
