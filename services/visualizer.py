"""
Visualization service.
"""

import gc
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

from domain.peak import PeakCollection
from domain.track import TrackCollection
from config.analysis_config import HoughConfig, VisualizationConfig


class VisualizerService:
    """
    Service for visualizing Hough accumulator with peaks.

    Responsibilities:
    - Draw Hough accumulator heatmaps
    - Overlay reconstructed and true peaks
    - Control visualization settings
    """

    def __init__(self, hough_config: HoughConfig, vis_config: VisualizationConfig):
        """
        Initialize visualizer.

        Args:
            hough_config: Hough configuration
            vis_config: Visualization configuration
        """
        self._hough_config = hough_config
        self._vis_config = vis_config
        self._plot_count = 0

    def draw_hough_accumulator(
        self,
        values: np.ndarray,
        reconstructed_peaks: PeakCollection,
        true_tracks: TrackCollection,
        slice_num: int
    ) -> None:
        """
        Draw Hough accumulator with peaks.

        Args:
            values: Hough accumulator values
            reconstructed_peaks: Collection of reconstructed peaks
            true_tracks: Collection of true tracks
            slice_num: Slice number for title
        """
        if not self._vis_config.enabled:
            return

        if self._plot_count >= self._vis_config.max_plots:
            return

        start_phi = self._vis_config.start_phi
        end_phi = self._vis_config.end_phi
        size_reco = self._hough_config.square_size
        size_true = self._vis_config.size_true

        # Create figure
        fig, ax = plt.subplots(figsize=(16, 24))
        im = ax.imshow(
            values[start_phi:end_phi, :],
            cmap='viridis',
            interpolation='nearest'
        )

        ax.set_aspect('auto')
        plt.colorbar(im, label="Counts")
        ax.set_xlabel("q/pT")
        ax.set_ylabel("phi")
        ax.set_title(f"Hough Accumulator - Slice {slice_num}")

        # Draw reconstructed peaks (red squares)
        for peak in reconstructed_peaks:
            square_x = peak.x - size_reco
            square_y = peak.y - start_phi - size_reco

            rect = patches.Rectangle(
                (square_x, square_y),
                2*size_reco, 2*size_reco,
                linewidth=3,
                edgecolor='red',
                facecolor='none'
            )
            ax.add_patch(rect)

        # Draw true tracks (yellow squares)
        xmin, xmax = ax.get_xlim()
        ymax, ymin = ax.get_ylim()

        for track in true_tracks:
            square_x = int(track.curv_bin) - size_true
            square_y = int(track.phi_bin) - start_phi - size_true

            rect = patches.Rectangle(
                (square_x, square_y),
                2*size_true, 2*size_true,
                linewidth=3,
                edgecolor="yellow",
                facecolor='none'
            )
            ax.add_patch(rect)

            # Add text annotation
            if xmin < square_x < xmax and ymin < square_y < ymax:
                ax.text(
                    square_x, square_y,
                    f"{track.number_of_hits} {round(track.pz_over_pt, 1)}",
                    fontsize=10,
                    color='white',
                    fontweight='bold'
                )

        plt.show()
        self._plot_count += 1

        # Cleanup
        del values
        gc.collect()

    def reset_plot_count(self) -> None:
        """Reset the plot counter."""
        self._plot_count = 0
