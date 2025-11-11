# Hough Transform Analysis

Code to read and write down Hough maxima from particle physics data files.

## Project Structure

The codebase has been reorganized into modular Python files:

```
hough/
├── config.py              # Configuration parameters (binning, thresholds, paths)
├── particle_charges.py    # Particle charge definitions and PDG ID lookup
├── slicer.py             # HoughSlicer class with easing functions
├── peak_detection.py      # Peak finding algorithms (vectorized sliding window)
├── track_analysis.py      # True track analysis and extraction
├── hough_processing.py    # Hough transform operations and matching
├── visualization.py       # Plotting functions for Hough accumulator
├── data_io.py            # Input/output operations (ROOT files, numpy)
├── main.py               # Main execution script
├── requirements.txt       # Python dependencies
└── analyze_ttbar.ipynb   # Original Jupyter notebook (reference)
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Analysis

Execute the main script:
```bash
python main.py
```

### Configuration

Edit `config.py` to adjust:
- Hough accumulator binning (NBIN_PHI, NBIN_QPT)
- Peak finding parameters (THRESHOLD_ABS, MIN_DISTANCE, etc.)
- Data path (PATH)
- Number of files to process (NUM_FILES)
- Slice configuration (SLICE_LIST)

### Module Description

**config.py**
- Central configuration for all parameters
- Easy modification of analysis settings

**particle_charges.py**
- Extended particle charge dictionary with PDG IDs
- Functions: `get_charge_from_pdg()`, `get_charges()`

**slicer.py**
- `HoughSlicer` class with multiple easing functions
- Supports: InSine, InSquare, InCubic, InCirc, Linear

**peak_detection.py**
- Vectorized 2D sliding window peak detection
- Gaussian smoothing and threshold filtering
- Functions: `vectorized_2d_sliding_peaks()`, `find_local_maxima_2d()`

**track_analysis.py**
- Extract true track information from simulation
- Functions: `true_tracks()`, `create_true_tracks_dict()`

**hough_processing.py**
- Process ROOT files with Hough accumulator data
- Match reconstructed peaks with true tracks
- Extract training data squares
- Functions: `process_root_file()`, `match_and_write()`, `get_hough_squares()`

**visualization.py**
- Draw Hough accumulator with peaks
- Function: `draw_hough()`

**data_io.py**
- Load particle data from ROOT files
- Save training data as numpy arrays
- Export true tracks to ROOT ntuples
- Functions: `load_particle_data()`, `save_training_data()`, `dict_to_root_ntuple()`

**main.py**
- Orchestrates the complete analysis workflow
- Provides progress reporting and summary

## Output Files

- `images.npz` - Training data (true and false peak squares)
- `out_true_tracks.root` - ROOT ntuple with true track information

## Testing

To verify the code works the same way as the original notebook, run:
```bash
python main.py
```

Compare the output files with those generated from the original notebook.
