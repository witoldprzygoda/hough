"""
True track analysis functions for Hough transform.
"""

import numpy as np
import pandas as pd

from particle_charges import get_charges
from config import NBIN_PHI, NBIN_QPT


def true_tracks(df, event_id):
    """
    Extract true track information for a specific event.

    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing particle data
    event_id : int
        Event ID to extract tracks for

    Returns:
    --------
    pandas.DataFrame
        DataFrame with filtered track information
    """
    result_dfs = []

    for row in df.itertuples(index=False):
        if row.event_id == event_id:
            phi = row.phi
            phi_bin = (phi + np.pi) * NBIN_PHI / (2. * np.pi)
            charges = get_charges(row.particle_type)

            # Mask when charges != 0 and number of hits > 4
            mask = (np.array(charges) != 0) & (np.array(row.number_of_hits) > 4)

            curv = charges / row.pt
            curv_bin = int(NBIN_QPT / 2.) + curv * int(NBIN_QPT / 2.)

            # Apply mask to ALL arrays that need filtering
            filtered_phi_bin = np.array(phi_bin)[mask]
            filtered_curv_bin = np.array(curv_bin)[mask]
            filtered_eta = np.array(row.eta)[mask]
            filtered_vz = np.array(row.vz)[mask]
            filtered_number_of_hits = np.array(row.number_of_hits)[mask]
            filtered_pz_over_pt = np.array(row.pz / row.pt)[mask]
            filtered_particle_type = np.array(row.particle_type)[mask]

            # Also apply mask to other fields that should be filtered
            filtered_phi = np.array(row.phi)[mask] if hasattr(row.phi, '__len__') else np.full(np.sum(mask), row.phi)
            filtered_pt = np.array(row.pt)[mask] if hasattr(row.pt, '__len__') else np.full(np.sum(mask), row.pt)
            filtered_pz = np.array(row.pz)[mask] if hasattr(row.pz, '__len__') else np.full(np.sum(mask), row.pz)
            filtered_event_id = np.full(np.sum(mask), row.event_id)

            # Add 'reco' column with all zeros
            filtered_reco = np.zeros(np.sum(mask))

            # Create DataFrame with ALL filtered fields
            accu_df = pd.DataFrame({
                'phi_bin': filtered_phi_bin,
                'curv_bin': filtered_curv_bin,
                'eta': filtered_eta,
                'vz': filtered_vz,
                'number_of_hits': filtered_number_of_hits,
                'pz_over_pt': filtered_pz_over_pt,
                'particle_type': filtered_particle_type,
                # Add additional fields with proper masking
                'event_id': filtered_event_id,
                'phi': filtered_phi,
                'pt': filtered_pt,
                'pz': filtered_pz,
                'reco': filtered_reco,
            })

            result_dfs.append(accu_df)

    # Combine all DataFrames if multiple rows match the event_id
    if result_dfs:
        return pd.concat(result_dfs, ignore_index=True)
    else:
        return pd.DataFrame()


def create_true_tracks_dict(df):
    """
    Create dictionary of true tracks for all events in DataFrame.

    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing particle data

    Returns:
    --------
    dict
        Dictionary mapping event_id to DataFrame of true tracks
    """
    # Initialize as regular dictionary
    truetracks = {}

    # Your loop - assign directly instead of appending
    for event_id in df["event_id"]:
        truetracks[event_id] = true_tracks(df, event_id)

    return truetracks
