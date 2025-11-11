"""
Input/output operations for ROOT files and data processing.
"""

import numpy as np
import pandas as pd
import uproot
from pathlib import Path


def load_particle_data(path):
    """
    Load particle data from ROOT files.

    Parameters:
    -----------
    path : str
        Directory path containing ROOT files

    Returns:
    --------
    pandas.DataFrame
        DataFrame containing particle data
    """
    root_files = sorted(Path(path).glob("particles*.root"))

    print(f"Found {len(root_files)} ROOT files in {path}\n")

    # Loop through files and list objects
    for file in root_files:
        print(f"📁 {file.name}")
        tree = uproot.open(file)["particles"]

        # Get data as a dictionary of NumPy arrays
        arrays = tree.arrays(library="np")

    # Convert manually into a DataFrame
    df = pd.DataFrame(arrays)

    print("Column names:")
    print(list(df.columns))

    print("\nFirst few rows:")
    print(df.head())

    return df


def find_root_files(path, pattern="out*.root"):
    """
    Find ROOT files matching pattern in directory.

    Parameters:
    -----------
    path : str
        Directory path
    pattern : str
        Glob pattern for files

    Returns:
    --------
    list
        Sorted list of Path objects
    """
    root_files = sorted(Path(path).glob(pattern))
    print(f"Found {len(root_files)} ROOT files in {path}\n")
    return root_files


def save_training_data(true_squares, false_squares, filename='images.npz'):
    """
    Save training data to compressed numpy file.

    Parameters:
    -----------
    true_squares : list
        List of true positive squares
    false_squares : list
        List of false positive squares
    filename : str
        Output filename

    Returns:
    --------
    tuple
        (combined_array, y_combined) - training data and labels
    """
    # Convert the list of arrays into a single numpy array
    array_true = np.stack(true_squares, axis=0)
    array_false = np.stack(false_squares, axis=0)

    # Add column with class
    y_true = np.ones(array_true.shape[0])
    y_false = np.zeros(array_false.shape[0])

    print(f"True and fake peaks: {array_true.shape[0]}, {array_false.shape[0]}")

    # Combine arrays along the 0 axis
    combined_array = np.vstack((array_true, array_false))
    y_combined = np.hstack((y_true, y_false))

    # Save the array to disk
    np.savez(filename, X=combined_array, y=y_combined)

    print(f"Shapes of output arrays: {combined_array.shape}, {y_combined.shape}")

    return combined_array, y_combined


def dict_to_root_ntuple(df_dict, event_list, filename, treename="ntuple",
                         add_source_id=True):
    """
    Convert dictionary of DataFrames to single DataFrame and save as ROOT ntuple.

    Parameters:
    -----------
    df_dict : dict
        Dictionary of {key: DataFrame}
    event_list : list
        List of events to include
    filename : str
        Output ROOT file name
    treename : str
        Name of the TTree
    add_source_id : bool
        Whether to add a column identifying the source DataFrame

    Returns:
    --------
    pandas.DataFrame
        Combined DataFrame
    """
    # Combine all DataFrames
    combined_dfs = []

    for key, df in df_dict.items():
        if key in event_list:
            df_copy = df.copy()

            # Add identifier column to track original source
            if add_source_id:
                df_copy['source_df'] = key

            combined_dfs.append(df_copy)

    # Concatenate all DataFrames
    combined_df = pd.concat(combined_dfs, ignore_index=True)

    print(f"Combined DataFrame shape: {combined_df.shape}")
    print(f"Columns: {combined_df.columns.tolist()}")

    # Save as ROOT ntuple using uproot
    with uproot.recreate(filename) as file:
        file[treename] = combined_df.to_dict(orient='list')

    print(f"Successfully saved to {filename}")
    return combined_df
