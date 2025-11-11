"""
Main execution script for Hough transform analysis.

This script performs the following steps:
1. Load particle simulation data
2. Create true tracks dictionary
3. Process ROOT files containing Hough accumulator data
4. Find peaks and match with true tracks
5. Save training data and true tracks
"""

import numpy as np
from pathlib import Path

# Import configuration
from config import PATH, NUM_FILES

# Import data I/O functions
from data_io import (load_particle_data, find_root_files,
                      save_training_data, dict_to_root_ntuple)

# Import track analysis functions
from track_analysis import create_true_tracks_dict

# Import processing functions
from hough_processing import process_root_file


def main():
    """Main execution function."""

    print("="*80)
    print("Hough Transform Analysis - Starting Processing")
    print("="*80)

    # -------------------------------------------------------------------------
    # Step 1: Load particle simulation data
    # -------------------------------------------------------------------------
    print("\n[1/5] Loading particle simulation data...")
    df = load_particle_data(PATH)

    # -------------------------------------------------------------------------
    # Step 2: Create true tracks dictionary
    # -------------------------------------------------------------------------
    print("\n[2/5] Creating true tracks dictionary...")
    truetracks = create_true_tracks_dict(df)
    print(f"Created true tracks for {len(truetracks)} events")

    # -------------------------------------------------------------------------
    # Step 3: Find ROOT files with Hough accumulator data
    # -------------------------------------------------------------------------
    print("\n[3/5] Finding ROOT files with Hough accumulator data...")
    root_files = find_root_files(PATH, pattern="out*.root")

    # -------------------------------------------------------------------------
    # Step 4: Process ROOT files
    # -------------------------------------------------------------------------
    print("\n[4/5] Processing ROOT files...")

    # Initialize storage for squares
    true_squares = []
    false_squares = []

    # Counter for true tracks after selection
    n_truetracks = 0

    # List of events processed
    event_list = []

    # Loop through files
    ifile = 0
    for file in root_files:
        print(f"\n{'='*80}")
        print(f"File {ifile+1}/{min(NUM_FILES, len(root_files))}: {file.name}")
        print(f"{'='*80}")

        if ifile < NUM_FILES:
            true_squares, false_squares, event_list, n_truetracks = process_root_file(
                file, truetracks, true_squares, false_squares,
                event_list, n_truetracks)

        ifile += 1

    # -------------------------------------------------------------------------
    # Step 5: Save results
    # -------------------------------------------------------------------------
    print("\n[5/5] Saving results...")

    # Save training data
    print("\nSaving training data...")
    save_training_data(true_squares, false_squares, filename='images.npz')

    print(f"\nTotal number of true tracks: {n_truetracks}")

    # Save true tracks as ROOT ntuple
    print("\nSaving true tracks as ROOT ntuple...")
    combined_truetracks = dict_to_root_ntuple(
        truetracks, event_list, "out_true_tracks.root", add_source_id=False)

    print("\n" + "="*80)
    print("Processing Complete!")
    print("="*80)
    print(f"\nOutput files:")
    print(f"  - images.npz (training data)")
    print(f"  - out_true_tracks.root (true tracks)")
    print(f"\nSummary:")
    print(f"  - True squares: {len(true_squares)}")
    print(f"  - False squares: {len(false_squares)}")
    print(f"  - Events processed: {len(event_list)}")
    print(f"  - True tracks: {n_truetracks}")


if __name__ == "__main__":
    main()
