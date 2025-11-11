"""
Main entry point for Hough transform analysis (Refactored OOP version).

This is the refactored version using OOP design patterns.
The implementation is clean, maintainable, and follows SOLID principles.

Usage:
    python main_refactored.py
"""

from facades.analysis_facade import HoughAnalysisFacade
from config.analysis_config import AnalysisConfigBuilder


def main():
    """
    Main execution function.

    Thanks to the Facade pattern, the entire analysis
    is now just a few lines of code!
    """
    # Create configuration (can be customized)
    config = AnalysisConfigBuilder.from_legacy_config()

    # Print configuration
    print(config)

    # Create facade and run analysis
    facade = HoughAnalysisFacade(config)
    stats = facade.run_complete_analysis()

    # Analysis complete - facade handles everything!
    print("\n✓ Analysis completed successfully!")


def main_with_custom_config():
    """
    Example of running with custom configuration.

    Demonstrates the Builder pattern for flexible configuration.
    """
    # Build custom configuration
    config = (AnalysisConfigBuilder()
              .with_hough_config(
                  nbin_phi=7000,
                  nbin_qpt=216,
                  square_size=16,
                  tolerance=6.0
              )
              .with_peak_detection_config(
                  threshold_abs=5.0,
                  min_distance=2,
                  smooth_sigma=0.0
              )
              .with_processing_config(
                  slice_list=[-1],
                  num_files=8,
                  min_hits=4
              )
              .with_paths(
                  data_path="/eos/user/t/tbold/EFTracking/HoughML/pg_2mu_pu100_insquare",
                  output_dir="."
              )
              .with_easing_type("InSquare")
              .build())

    # Run analysis
    facade = HoughAnalysisFacade(config)
    stats = facade.run_complete_analysis()

    print(f"\nReconstruction efficiency: {stats.reconstruction_efficiency:.2%}")


def main_simple():
    """
    Simplest possible usage with default configuration.

    One line to run the entire analysis!
    """
    facade = HoughAnalysisFacade.create_with_default_config()
    facade.run_complete_analysis()


if __name__ == "__main__":
    # Run the default analysis
    main()

    # Uncomment to try custom configuration:
    # main_with_custom_config()

    # Uncomment for simplest usage:
    # main_simple()
