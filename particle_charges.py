"""
Particle charge definitions and lookup functions.
Extended particle charge dictionary with PDG ID mappings.
"""

# Extended particle charge dictionary
PARTICLE_CHARGES = {
    # Gauge bosons
    22: 0,       # photon
    23: 0,       # Z boson
    24: 1,       # W+
    -24: -1,     # W-
    21: 0,       # gluon

    # Leptons
    11: -1,      # e-
    -11: 1,      # e+
    12: 0,       # ν_e
    -12: 0,      # ν_e bar
    13: -1,      # μ-
    -13: 1,      # μ+
    14: 0,       # ν_μ
    -14: 0,      # ν_μ bar
    15: -1,      # τ-
    -15: 1,      # τ+
    16: 0,       # ν_τ
    -16: 0,      # ν_τ bar

    # Quarks
    1: -1/3,     # d
    -1: 1/3,     # d bar
    2: 2/3,      # u
    -2: -2/3,    # u bar
    3: -1/3,     # s
    -3: 1/3,     # s bar
    4: 2/3,      # c
    -4: -2/3,    # c bar
    5: -1/3,     # b
    -5: 1/3,     # b bar
    6: 2/3,      # t
    -6: -2/3,    # t bar

    # Light mesons
    111: 0,      # π⁰
    211: 1,      # π+
    -211: -1,    # π-
    113: 0,      # ρ⁰
    213: 1,      # ρ+
    -213: -1,    # ρ-
    221: 0,      # η
    331: 0,      # η'
    130: 0,      # K_L⁰
    310: 0,      # K_S⁰
    311: 0,      # K⁰
    -311: 0,     # K⁰ bar
    321: 1,      # K+
    -321: -1,    # K-

    # Charmed mesons
    411: 1,      # D+
    -411: -1,    # D-
    421: 0,      # D⁰
    -421: 0,     # D⁰ bar

    # Bottom mesons
    511: 0,      # B⁰
    -511: 0,     # B⁰ bar
    521: 1,      # B+
    -521: -1,    # B-

    # Baryons
    2212: 1,     # proton
    -2212: -1,   # antiproton
    2112: 0,     # neutron
    -2112: 0,    # antineutron
    3122: 0,     # Λ
    -3122: 0,    # Λ bar
    3222: 1,     # Σ+
    -3222: -1,   # Σ+ bar
    3212: 0,     # Σ⁰
    -3212: 0,    # Σ⁰ bar
    3112: -1,    # Σ-
    -3112: 1,    # Σ- bar
    3312: -1,    # Ξ⁻
    -3312: 1,    # Ξ⁻ bar
    3322: 0,     # Ξ⁰
    -3322: 0,    # Ξ⁰ bar
}


def get_charge_from_pdg(pdg_id):
    """
    Get electric charge from PDG ID.

    Parameters:
    -----------
    pdg_id : int
        PDG particle ID code

    Returns:
    --------
    float or None
        Electric charge in units of e, or None if unknown
    """
    if pdg_id in PARTICLE_CHARGES:
        return PARTICLE_CHARGES[pdg_id]
    else:
        # Try to handle antiparticles automatically
        if pdg_id < 0 and -pdg_id in PARTICLE_CHARGES:
            return -PARTICLE_CHARGES[-pdg_id]
        return None


def get_charge_safe(pdg_id):
    """
    Get charge, return 0 for unknown particles.

    Parameters:
    -----------
    pdg_id : int
        PDG particle ID code

    Returns:
    --------
    float
        Electric charge in units of e, 0 if unknown
    """
    charge = get_charge_from_pdg(pdg_id)
    return charge if charge is not None else 0


def get_charges(particle_ids):
    """
    Return a list of charges for a list of PDG IDs.
    If an ID is not known in the PDG database, returns None for that entry.

    Parameters:
    -----------
    particle_ids : array-like
        List of PDG particle ID codes

    Returns:
    --------
    list
        List of charges (float or None for each particle)
    """
    charges = []
    for pid in particle_ids:
        try:
            charges.append(get_charge_from_pdg(pid))
        except Exception:
            charges.append(None)  # unknown ID
    return charges
