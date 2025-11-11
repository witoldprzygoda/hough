"""
Configuration classes for Hough analysis.

Implements Builder pattern for complex configuration objects.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path


@dataclass(frozen=True)
class HoughConfig:
    """Configuration for Hough transform parameters."""
    nbin_phi: int = 7000
    nbin_qpt: int = 216
    square_size: int = 16
    tolerance: float = 6.0


@dataclass(frozen=True)
class PeakDetectionConfig:
    """Configuration for peak detection parameters."""
    threshold_abs: float = 5.0
    threshold_rel: float = 0.0
    min_distance: int = 2
    smooth_sigma: float = 0.0


@dataclass(frozen=True)
class VisualizationConfig:
    """Configuration for visualization parameters."""
    start_phi: int = 1000
    end_phi: int = 2000
    size_true: int = 3
    enabled: bool = True
    max_plots: int = 200


@dataclass(frozen=True)
class ProcessingConfig:
    """Configuration for data processing."""
    slice_list: List[int] = field(default_factory=lambda: [-1])
    num_files: int = 8
    min_hits: int = 4
    vz_range: tuple = (-200, 200)


@dataclass(frozen=True)
class PathConfig:
    """Configuration for file paths."""
    data_path: str = "/eos/user/t/tbold/EFTracking/HoughML/pg_2mu_pu100_insquare"
    output_dir: str = "."

    @property
    def data_path_obj(self) -> Path:
        """Get data path as Path object."""
        return Path(self.data_path)

    @property
    def output_dir_obj(self) -> Path:
        """Get output directory as Path object."""
        return Path(self.output_dir)


@dataclass(frozen=True)
class AnalysisConfig:
    """
    Complete analysis configuration.

    Immutable configuration object containing all analysis parameters.
    """
    hough: HoughConfig
    peak_detection: PeakDetectionConfig
    visualization: VisualizationConfig
    processing: ProcessingConfig
    paths: PathConfig
    easing_type: str = "InSquare"

    def __str__(self) -> str:
        """String representation of configuration."""
        lines = [
            "=== Analysis Configuration ===",
            f"Easing Type: {self.easing_type}",
            "",
            "Hough Transform:",
            f"  - Phi bins: {self.hough.nbin_phi}",
            f"  - Q/pT bins: {self.hough.nbin_qpt}",
            f"  - Square size: {self.hough.square_size}",
            f"  - Tolerance: {self.hough.tolerance}",
            "",
            "Peak Detection:",
            f"  - Absolute threshold: {self.peak_detection.threshold_abs}",
            f"  - Relative threshold: {self.peak_detection.threshold_rel}",
            f"  - Min distance: {self.peak_detection.min_distance}",
            f"  - Smoothing sigma: {self.peak_detection.smooth_sigma}",
            "",
            "Processing:",
            f"  - Slice list: {self.processing.slice_list}",
            f"  - Number of files: {self.processing.num_files}",
            f"  - Min hits: {self.processing.min_hits}",
            f"  - Vz range: {self.processing.vz_range}",
            "",
            "Paths:",
            f"  - Data path: {self.paths.data_path}",
            f"  - Output dir: {self.paths.output_dir}",
            "=============================="
        ]
        return "\n".join(lines)


class AnalysisConfigBuilder:
    """
    Builder for creating AnalysisConfig instances.

    Implements the Builder pattern for flexible configuration creation.
    """

    def __init__(self):
        """Initialize builder with default values."""
        self._hough: Optional[HoughConfig] = None
        self._peak_detection: Optional[PeakDetectionConfig] = None
        self._visualization: Optional[VisualizationConfig] = None
        self._processing: Optional[ProcessingConfig] = None
        self._paths: Optional[PathConfig] = None
        self._easing_type: str = "InSquare"

    def with_hough_config(
        self,
        nbin_phi: int = 7000,
        nbin_qpt: int = 216,
        square_size: int = 16,
        tolerance: float = 6.0
    ) -> 'AnalysisConfigBuilder':
        """Set Hough transform configuration."""
        self._hough = HoughConfig(
            nbin_phi=nbin_phi,
            nbin_qpt=nbin_qpt,
            square_size=square_size,
            tolerance=tolerance
        )
        return self

    def with_peak_detection_config(
        self,
        threshold_abs: float = 5.0,
        threshold_rel: float = 0.0,
        min_distance: int = 2,
        smooth_sigma: float = 0.0
    ) -> 'AnalysisConfigBuilder':
        """Set peak detection configuration."""
        self._peak_detection = PeakDetectionConfig(
            threshold_abs=threshold_abs,
            threshold_rel=threshold_rel,
            min_distance=min_distance,
            smooth_sigma=smooth_sigma
        )
        return self

    def with_visualization_config(
        self,
        start_phi: int = 1000,
        end_phi: int = 2000,
        size_true: int = 3,
        enabled: bool = True,
        max_plots: int = 200
    ) -> 'AnalysisConfigBuilder':
        """Set visualization configuration."""
        self._visualization = VisualizationConfig(
            start_phi=start_phi,
            end_phi=end_phi,
            size_true=size_true,
            enabled=enabled,
            max_plots=max_plots
        )
        return self

    def with_processing_config(
        self,
        slice_list: List[int] = None,
        num_files: int = 8,
        min_hits: int = 4,
        vz_range: tuple = (-200, 200)
    ) -> 'AnalysisConfigBuilder':
        """Set processing configuration."""
        if slice_list is None:
            slice_list = [-1]
        self._processing = ProcessingConfig(
            slice_list=slice_list,
            num_files=num_files,
            min_hits=min_hits,
            vz_range=vz_range
        )
        return self

    def with_paths(
        self,
        data_path: str = "/eos/user/t/tbold/EFTracking/HoughML/pg_2mu_pu100_insquare",
        output_dir: str = "."
    ) -> 'AnalysisConfigBuilder':
        """Set path configuration."""
        self._paths = PathConfig(
            data_path=data_path,
            output_dir=output_dir
        )
        return self

    def with_easing_type(self, easing_type: str) -> 'AnalysisConfigBuilder':
        """Set easing type."""
        self._easing_type = easing_type
        return self

    def build(self) -> AnalysisConfig:
        """
        Build the final configuration object.

        Returns:
            Immutable AnalysisConfig instance
        """
        # Use defaults if not set
        hough = self._hough or HoughConfig()
        peak_detection = self._peak_detection or PeakDetectionConfig()
        visualization = self._visualization or VisualizationConfig()
        processing = self._processing or ProcessingConfig()
        paths = self._paths or PathConfig()

        return AnalysisConfig(
            hough=hough,
            peak_detection=peak_detection,
            visualization=visualization,
            processing=processing,
            paths=paths,
            easing_type=self._easing_type
        )

    @classmethod
    def default(cls) -> AnalysisConfig:
        """Create configuration with default values."""
        return cls().build()

    @classmethod
    def from_legacy_config(cls) -> AnalysisConfig:
        """
        Create configuration from legacy config.py values.

        Returns:
            AnalysisConfig with legacy values
        """
        return (cls()
                .with_hough_config(
                    nbin_phi=7000,
                    nbin_qpt=216,
                    square_size=16,
                    tolerance=6.0
                )
                .with_peak_detection_config(
                    threshold_abs=5.0,
                    threshold_rel=0.0,
                    min_distance=2,
                    smooth_sigma=0.0
                )
                .with_visualization_config(
                    start_phi=1000,
                    end_phi=2000,
                    size_true=3,
                    enabled=True,
                    max_plots=200
                )
                .with_processing_config(
                    slice_list=[-1],
                    num_files=8,
                    min_hits=4,
                    vz_range=(-200, 200)
                )
                .with_paths(
                    data_path="/eos/user/t/tbold/EFTracking/HoughML/pg_2mu_pu100_insquare",
                    output_dir="."
                )
                .with_easing_type("InSquare")
                .build())
