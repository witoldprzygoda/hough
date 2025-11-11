"""
Observer pattern for progress tracking.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List
from datetime import datetime


@dataclass
class AnalysisStatistics:
    """
    Value object for analysis statistics.

    Tracks cumulative statistics during analysis.
    """
    total_files: int = 0
    processed_files: int = 0
    total_events: int = 0
    processed_histograms: int = 0
    true_tracks_total: int = 0
    true_squares: int = 0
    false_squares: int = 0
    start_time: datetime = None
    event_ids: List[int] = field(default_factory=list)

    def add_event(self, event_id: int) -> None:
        """Add a new event ID."""
        if event_id not in self.event_ids:
            self.event_ids.append(event_id)
            self.total_events += 1

    def add_true_tracks(self, count: int) -> None:
        """Add to true tracks count."""
        self.true_tracks_total += count

    def add_squares(self, true_count: int, false_count: int) -> None:
        """Add to square counts."""
        self.true_squares += true_count
        self.false_squares += false_count

    def increment_files(self) -> None:
        """Increment processed files count."""
        self.processed_files += 1

    def increment_histograms(self) -> None:
        """Increment processed histograms count."""
        self.processed_histograms += 1

    @property
    def total_squares(self) -> int:
        """Get total number of squares."""
        return self.true_squares + self.false_squares

    @property
    def reconstruction_efficiency(self) -> float:
        """Calculate reconstruction efficiency."""
        if self.true_tracks_total == 0:
            return 0.0
        return self.true_squares / self.true_tracks_total


class ProgressObserver(ABC):
    """
    Abstract base class for progress observers.

    Implements Observer pattern.
    """

    @abstractmethod
    def on_file_start(self, filename: str, file_num: int, total_files: int) -> None:
        """Called when starting to process a file."""
        pass

    @abstractmethod
    def on_file_complete(self, filename: str, stats: AnalysisStatistics) -> None:
        """Called when file processing is complete."""
        pass

    @abstractmethod
    def on_event_discovered(self, event_id: int) -> None:
        """Called when a new event is discovered."""
        pass

    @abstractmethod
    def on_slice_start(self, event_id: int, slice_num: int) -> None:
        """Called when starting to process a slice."""
        pass

    @abstractmethod
    def on_slice_complete(
        self,
        event_id: int,
        slice_num: int,
        peaks_found: int,
        true_tracks_in_slice: int,
        matched_tracks: int
    ) -> None:
        """Called when slice processing is complete."""
        pass

    @abstractmethod
    def on_analysis_start(self, total_files: int) -> None:
        """Called when analysis starts."""
        pass

    @abstractmethod
    def on_analysis_complete(self, stats: AnalysisStatistics) -> None:
        """Called when analysis is complete."""
        pass


class ConsoleProgressObserver(ProgressObserver):
    """
    Console-based progress observer.

    Prints progress information to console.
    """

    def __init__(self, verbose: bool = True):
        """
        Initialize console observer.

        Args:
            verbose: Whether to print detailed information
        """
        self._verbose = verbose

    def on_file_start(self, filename: str, file_num: int, total_files: int) -> None:
        """Print file start message."""
        print(f"\n{'='*80}")
        print(f"File {file_num}/{total_files}: {filename}")
        print(f"{'='*80}")

    def on_file_complete(self, filename: str, stats: AnalysisStatistics) -> None:
        """Print file completion message."""
        if self._verbose:
            print(f"\n✓ Completed {filename}")
            print(f"  Events processed: {stats.total_events}")
            print(f"  True squares: {stats.true_squares}")
            print(f"  False squares: {stats.false_squares}")

    def on_event_discovered(self, event_id: int) -> None:
        """Print event discovery message."""
        print(f"\nEvent: {event_id}")

    def on_slice_start(self, event_id: int, slice_num: int) -> None:
        """Print slice start message."""
        if self._verbose:
            print(f"\n####### Slice number: {slice_num}")

    def on_slice_complete(
        self,
        event_id: int,
        slice_num: int,
        peaks_found: int,
        true_tracks_in_slice: int,
        matched_tracks: int
    ) -> None:
        """Print slice completion message."""
        print(f"Peaks found: {peaks_found}")
        print(f"True tracks in slice: {true_tracks_in_slice}")
        print(f"Matched tracks: {matched_tracks}")

    def on_analysis_start(self, total_files: int) -> None:
        """Print analysis start message."""
        print("="*80)
        print("Hough Transform Analysis - Starting Processing")
        print("="*80)
        print(f"\nTotal files to process: {total_files}")

    def on_analysis_complete(self, stats: AnalysisStatistics) -> None:
        """Print analysis completion summary."""
        print("\n" + "="*80)
        print("Processing Complete!")
        print("="*80)

        print(f"\nSummary:")
        print(f"  - Files processed: {stats.processed_files}/{stats.total_files}")
        print(f"  - Events processed: {stats.total_events}")
        print(f"  - Histograms processed: {stats.processed_histograms}")
        print(f"  - True tracks found: {stats.true_tracks_total}")
        print(f"  - True squares: {stats.true_squares}")
        print(f"  - False squares: {stats.false_squares}")
        print(f"  - Total squares: {stats.total_squares}")
        print(f"  - Reconstruction efficiency: {stats.reconstruction_efficiency:.2%}")


class NullProgressObserver(ProgressObserver):
    """Observer that does nothing (Null Object pattern)."""

    def on_file_start(self, filename: str, file_num: int, total_files: int) -> None:
        pass

    def on_file_complete(self, filename: str, stats: AnalysisStatistics) -> None:
        pass

    def on_event_discovered(self, event_id: int) -> None:
        pass

    def on_slice_start(self, event_id: int, slice_num: int) -> None:
        pass

    def on_slice_complete(
        self,
        event_id: int,
        slice_num: int,
        peaks_found: int,
        true_tracks_in_slice: int,
        matched_tracks: int
    ) -> None:
        pass

    def on_analysis_start(self, total_files: int) -> None:
        pass

    def on_analysis_complete(self, stats: AnalysisStatistics) -> None:
        pass
