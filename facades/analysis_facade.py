"""
Facade for Hough analysis workflow.

Provides simplified high-level API for complete analysis.
"""

import gc
from datetime import datetime
from typing import Optional

from config.analysis_config import AnalysisConfig
from repositories.particle_repository import ParticleRepository
from repositories.hough_repository import HoughRepository
from repositories.training_data_repository import TrainingDataRepository
from services.peak_detector import PeakDetectorService
from services.track_slicer import TrackSlicerService
from services.hough_matcher import HoughMatcherService
from services.visualizer import VisualizerService
from utils.observers import (
    ProgressObserver,
    ConsoleProgressObserver,
    AnalysisStatistics
)
from domain.hough_square import HoughSquareCollection


class HoughAnalysisFacade:
    """
    Facade providing simplified API for Hough transform analysis.

    Implements Facade pattern to hide system complexity.
    Orchestrates all services, repositories, and domain objects.
    """

    def __init__(
        self,
        config: AnalysisConfig,
        observer: Optional[ProgressObserver] = None
    ):
        """
        Initialize analysis facade.

        Args:
            config: Analysis configuration
            observer: Progress observer (creates default if None)
        """
        self._config = config
        self._observer = observer or ConsoleProgressObserver(verbose=True)
        self._stats = AnalysisStatistics()

        # Initialize repositories
        self._particle_repo = ParticleRepository(config.paths.data_path_obj)
        self._hough_repo = HoughRepository(config.paths.data_path_obj)
        self._training_repo = TrainingDataRepository(config.paths.output_dir_obj)

        # Initialize services
        self._peak_detector = PeakDetectorService(config.peak_detection)
        self._track_slicer = TrackSlicerService.create(
            config.easing_type,
            config.hough,
            config.processing
        )
        self._hough_matcher = HoughMatcherService(config.hough)
        self._visualizer = VisualizerService(config.hough, config.visualization)

        # Storage for analysis results
        self._tracks_dict = {}
        self._square_collection = HoughSquareCollection()

    def run_complete_analysis(self) -> AnalysisStatistics:
        """
        Run complete end-to-end analysis.

        Returns:
            AnalysisStatistics with results summary
        """
        self._stats.start_time = datetime.now()

        # Step 1: Load particle data
        print("\n[1/4] Loading particle simulation data...")
        df = self._particle_repo.load_particles()

        # Step 2: Create true tracks dictionary
        print("\n[2/4] Creating true tracks dictionary...")
        self._tracks_dict = self._particle_repo.create_tracks_dict(
            nbin_phi=self._config.hough.nbin_phi,
            nbin_qpt=self._config.hough.nbin_qpt,
            min_hits=self._config.processing.min_hits
        )
        print(f"Created tracks for {len(self._tracks_dict)} events")

        # Step 3: Process Hough files
        print("\n[3/4] Processing Hough accumulator files...")
        self._process_hough_files()

        # Step 4: Save results
        print("\n[4/4] Saving results...")
        self._save_results()

        # Notify completion
        self._observer.on_analysis_complete(self._stats)

        return self._stats

    def _process_hough_files(self) -> None:
        """Process all Hough ROOT files."""
        # Find files
        files = self._hough_repo.find_files()
        self._stats.total_files = min(len(files), self._config.processing.num_files)

        self._observer.on_analysis_start(self._stats.total_files)

        # Process each file
        for file_idx, file_path in enumerate(files):
            if file_idx >= self._config.processing.num_files:
                break

            self._process_single_file(file_path, file_idx + 1)
            self._stats.increment_files()

    def _process_single_file(self, file_path, file_num: int) -> None:
        """
        Process a single ROOT file.

        Args:
            file_path: Path to ROOT file
            file_num: File number for progress tracking
        """
        self._observer.on_file_start(
            file_path.name,
            file_num,
            self._stats.total_files
        )

        # Iterate over histograms in file
        for hough_hist in self._hough_repo.iter_histograms(file_path):
            self._process_histogram(hough_hist)
            self._stats.increment_histograms()

            # Cleanup
            gc.collect()

        self._observer.on_file_complete(file_path.name, self._stats)

    def _process_histogram(self, hough_hist) -> None:
        """
        Process a single Hough histogram.

        Args:
            hough_hist: HoughHistogram object
        """
        event_id = hough_hist.event_id
        slice_num = hough_hist.slice_num

        # Track event
        if event_id not in self._stats.event_ids:
            self._stats.add_event(event_id)
            self._observer.on_event_discovered(event_id)

        # Check if slice should be processed
        if slice_num not in self._config.processing.slice_list:
            return

        self._observer.on_slice_start(event_id, slice_num)

        # Get true tracks for this event
        if event_id not in self._tracks_dict:
            return

        true_tracks = self._tracks_dict[event_id]

        # Filter tracks for this slice
        filtered_tracks = self._track_slicer.filter_tracks_for_slice(
            true_tracks,
            slice_num
        )

        # Update true tracks count
        self._stats.add_true_tracks(len(filtered_tracks))

        # Detect peaks
        peaks = self._peak_detector.find_peaks(hough_hist.histogram)

        # Get accumulator values for matching
        values, _, _ = hough_hist.histogram.to_numpy()
        values = values.T

        # Match peaks with tracks and extract squares
        squares, assignment_mask = self._hough_matcher.match_and_extract_squares(
            values,
            peaks,
            filtered_tracks
        )

        # Update track reconstruction status
        matched_count = self._hough_matcher.update_track_reconstruction_status(
            filtered_tracks,  # Update filtered collection (changes propagate to original)
            assignment_mask
        )

        # Add squares to global collection
        for square in [s for s in [squares._true_positives, squares._false_positives] for s in s]:
            self._square_collection.add_square(square)

        # Update statistics
        self._stats.add_squares(
            squares.true_positive_count,
            squares.false_positive_count
        )

        # Visualize if enabled
        self._visualizer.draw_hough_accumulator(
            values,
            peaks,
            filtered_tracks,
            slice_num
        )

        # Report slice completion
        self._observer.on_slice_complete(
            event_id,
            slice_num,
            len(peaks),
            len(filtered_tracks),
            matched_count
        )

        # Cleanup
        del values
        gc.collect()

    def _save_results(self) -> None:
        """Save analysis results."""
        # Save training data
        print("\nSaving training data...")
        self._training_repo.save_squares(
            self._square_collection,
            filename="images.npz"
        )

        # Save true tracks
        print("\nSaving true tracks to ROOT file...")
        self._particle_repo.save_tracks_to_root(
            self._tracks_dict,
            self._stats.event_ids,
            filename=str(self._config.paths.output_dir_obj / "out_true_tracks.root"),
            treename="ntuple"
        )

        print(f"\nOutput files created in {self._config.paths.output_dir}")

    def get_statistics(self) -> AnalysisStatistics:
        """Get current statistics."""
        return self._stats

    def get_square_collection(self) -> HoughSquareCollection:
        """Get the square collection."""
        return self._square_collection

    def get_tracks_dict(self) -> dict:
        """Get the tracks dictionary."""
        return self._tracks_dict

    @classmethod
    def create_with_default_config(cls) -> 'HoughAnalysisFacade':
        """
        Create facade with default configuration.

        Returns:
            HoughAnalysisFacade instance
        """
        from config.analysis_config import AnalysisConfigBuilder
        config = AnalysisConfigBuilder.from_legacy_config()
        return cls(config)

    @classmethod
    def create_with_custom_config(
        cls,
        **config_kwargs
    ) -> 'HoughAnalysisFacade':
        """
        Create facade with custom configuration.

        Args:
            **config_kwargs: Configuration parameters

        Returns:
            HoughAnalysisFacade instance
        """
        from config.analysis_config import AnalysisConfigBuilder
        builder = AnalysisConfigBuilder()

        # Apply configuration parameters
        if 'data_path' in config_kwargs or 'output_dir' in config_kwargs:
            builder.with_paths(
                data_path=config_kwargs.get('data_path',
                    "/eos/user/t/tbold/EFTracking/HoughML/pg_2mu_pu100_insquare"),
                output_dir=config_kwargs.get('output_dir', ".")
            )

        if 'num_files' in config_kwargs or 'slice_list' in config_kwargs:
            builder.with_processing_config(
                num_files=config_kwargs.get('num_files', 8),
                slice_list=config_kwargs.get('slice_list', [-1])
            )

        config = builder.build()
        return cls(config)
