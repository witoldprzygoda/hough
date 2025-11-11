# Quick Start Guide - OOP Version

Welcome to the refactored OOP version of the Hough Transform Analysis system!

## Installation

```bash
pip install -r requirements.txt
```

## Basic Usage

### Option 1: Simplest Usage (Default Configuration)

```python
from facades.analysis_facade import HoughAnalysisFacade

# One line to run complete analysis!
facade = HoughAnalysisFacade.create_with_default_config()
stats = facade.run_complete_analysis()

print(f"Reconstruction efficiency: {stats.reconstruction_efficiency:.2%}")
```

### Option 2: Run with Script

```bash
python main_refactored.py
```

### Option 3: Custom Configuration

```python
from facades.analysis_facade import HoughAnalysisFacade
from config.analysis_config import AnalysisConfigBuilder

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
              data_path="/path/to/your/data",
              output_dir="./output"
          )
          .with_easing_type("InSquare")
          .build())

# Run analysis
facade = HoughAnalysisFacade(config)
stats = facade.run_complete_analysis()
```

## Common Tasks

### Change Data Path

```python
facade = HoughAnalysisFacade.create_with_custom_config(
    data_path="/eos/user/t/tbold/EFTracking/HoughML/ttbar_pu100_insquare",
    num_files=10
)
facade.run_complete_analysis()
```

### Process Different Slices

```python
config = (AnalysisConfigBuilder()
          .with_processing_config(
              slice_list=[10, 11, 12, 13, 14],  # Process specific slices
              num_files=5
          )
          .build())

facade = HoughAnalysisFacade(config)
facade.run_complete_analysis()
```

### Use Different Easing Strategy

```python
config = (AnalysisConfigBuilder()
          .with_easing_type("InCubic")  # Options: InSquare, InSine, InCubic, InCirc, Linear
          .build())

facade = HoughAnalysisFacade(config)
facade.run_complete_analysis()
```

### Custom Progress Tracking

```python
from utils.observers import ProgressObserver

class MyProgressObserver(ProgressObserver):
    def on_slice_complete(self, event_id, slice_num, peaks, tracks, matched):
        print(f"✓ Event {event_id}, Slice {slice_num}: {matched} tracks matched")

    # Implement other methods as needed
    def on_file_start(self, filename, file_num, total): pass
    def on_file_complete(self, filename, stats): pass
    def on_event_discovered(self, event_id): pass
    def on_slice_start(self, event_id, slice_num): pass
    def on_analysis_start(self, total_files): pass
    def on_analysis_complete(self, stats): pass

# Use custom observer
observer = MyProgressObserver()
facade = HoughAnalysisFacade(config, observer)
facade.run_complete_analysis()
```

### Disable Visualization

```python
config = (AnalysisConfigBuilder()
          .with_visualization_config(
              enabled=False  # Disable plots
          )
          .build())

facade = HoughAnalysisFacade(config)
facade.run_complete_analysis()
```

## Accessing Results

### Get Statistics

```python
facade = HoughAnalysisFacade.create_with_default_config()
stats = facade.run_complete_analysis()

print(f"Total events: {stats.total_events}")
print(f"True tracks: {stats.true_tracks_total}")
print(f"True squares: {stats.true_squares}")
print(f"False squares: {stats.false_squares}")
print(f"Efficiency: {stats.reconstruction_efficiency:.2%}")
```

### Access Square Collection

```python
facade = HoughAnalysisFacade.create_with_default_config()
facade.run_complete_analysis()

# Get the square collection
squares = facade.get_square_collection()

# Get training data
X, y = squares.get_training_data()
print(f"Training data shape: X={X.shape}, y={y.shape}")

# Get summary
summary = squares.summary()
print(f"Summary: {summary}")
```

### Access Tracks

```python
facade = HoughAnalysisFacade.create_with_default_config()
facade.run_complete_analysis()

# Get tracks dictionary
tracks_dict = facade.get_tracks_dict()

# Get tracks for specific event
event_tracks = tracks_dict[123]  # Event ID 123

# Get reconstructed tracks
reconstructed = event_tracks.get_reconstructed()
print(f"Reconstructed tracks: {len(reconstructed)}")
```

## Using Individual Services

You can also use services independently for custom workflows:

### Peak Detection

```python
from services.peak_detector import PeakDetectorService
from config.analysis_config import PeakDetectionConfig
import uproot

# Create service
config = PeakDetectionConfig(threshold_abs=5.0, min_distance=2)
detector = PeakDetectorService(config)

# Find peaks in histogram
with uproot.open("data.root") as f:
    histogram = f["histogram_name"]
    peaks = detector.find_peaks(histogram)

print(f"Found {len(peaks)} peaks")
```

### Track Slicing

```python
from services.track_slicer import TrackSlicerService
from domain.track import TrackCollection

# Create slicer
slicer = TrackSlicerService.create("InSquare", hough_config, processing_config)

# Filter tracks for slice
filtered_tracks = slicer.filter_tracks_for_slice(all_tracks, slice_num=10)
print(f"Tracks in slice: {len(filtered_tracks)}")
```

### Matching

```python
from services.hough_matcher import HoughMatcherService

# Create matcher
matcher = HoughMatcherService(hough_config)

# Match peaks with tracks
squares, mask = matcher.match_and_extract_squares(
    accumulator_values,
    reconstructed_peaks,
    true_tracks
)

print(f"True positives: {squares.true_positive_count}")
print(f"False positives: {squares.false_positive_count}")
```

## Advanced: Adding Custom Easing Strategy

```python
from strategies.easing_strategy import EasingStrategy, EasingStrategyFactory

# Define custom strategy
class MyCustomEasing(EasingStrategy):
    def ease(self, x: float) -> float:
        # Your custom algorithm
        return x ** 1.5

    def name(self) -> str:
        return "MyCustom"

# Register it
EasingStrategyFactory.register_strategy("MyCustom", MyCustomEasing)

# Use it
config = (AnalysisConfigBuilder()
          .with_easing_type("MyCustom")
          .build())

facade = HoughAnalysisFacade(config)
facade.run_complete_analysis()
```

## Output Files

After running the analysis, you'll find:

- `images.npz` - Training data (X and y arrays)
- `out_true_tracks.root` - ROOT file with true track information

## Configuration Options Reference

### Hough Configuration
- `nbin_phi` - Number of phi bins (default: 7000)
- `nbin_qpt` - Number of q/pT bins (default: 216)
- `square_size` - Half-width of extraction square (default: 16)
- `tolerance` - Distance tolerance for matching (default: 6.0)

### Peak Detection Configuration
- `threshold_abs` - Absolute intensity threshold (default: 5.0)
- `threshold_rel` - Relative threshold fraction (default: 0.0)
- `min_distance` - Minimum distance between peaks (default: 2)
- `smooth_sigma` - Gaussian smoothing sigma (default: 0.0)

### Processing Configuration
- `slice_list` - List of slices to process (default: [-1])
- `num_files` - Number of files to process (default: 8)
- `min_hits` - Minimum hits per track (default: 4)
- `vz_range` - Vertex z range tuple (default: (-200, 200))

### Visualization Configuration
- `start_phi` - Starting phi for visualization (default: 1000)
- `end_phi` - Ending phi for visualization (default: 2000)
- `size_true` - Size of true peak markers (default: 3)
- `enabled` - Enable/disable visualization (default: True)
- `max_plots` - Maximum number of plots (default: 200)

### Path Configuration
- `data_path` - Path to input data directory
- `output_dir` - Path to output directory (default: ".")

### Easing Type
- `"InSquare"` - Square easing (default)
- `"InSine"` - Sine easing
- `"InCubic"` - Cubic easing
- `"InCirc"` - Circular easing
- `"Linear"` - No easing

## Troubleshooting

### Import Errors

Make sure you're in the correct directory:
```bash
cd /path/to/hough
python main_refactored.py
```

Or add to PYTHONPATH:
```bash
export PYTHONPATH=/path/to/hough:$PYTHONPATH
python main_refactored.py
```

### Data Path Not Found

Check your data path configuration:
```python
config = AnalysisConfigBuilder().with_paths(
    data_path="/correct/path/to/data"
).build()
```

### No Output Files

Check that output directory exists and is writable:
```python
config = AnalysisConfigBuilder().with_paths(
    output_dir="./output"
).build()

# Directory will be created automatically
```

## Getting Help

- See `OOP_ARCHITECTURE.md` for detailed architecture documentation
- See `REFACTORING_SUMMARY.md` for comparison with legacy version
- Check the original `README.md` for general project information

## Comparison with Legacy Version

| Feature | Legacy (main.py) | OOP (main_refactored.py) |
|---------|------------------|--------------------------|
| Lines of code | ~200 | ~10 |
| Configuration | Hardcoded globals | Builder pattern |
| Testability | Difficult | Easy |
| Extensibility | Hard | Easy |
| Maintainability | Low | High |
| Reusability | Limited | High |

The OOP version provides the same functionality with dramatically improved code quality and usability!
