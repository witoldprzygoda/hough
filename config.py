"""
Configuration parameters for Hough transform analysis.
"""

# Binning of the Hough accumulator
NBIN_PHI = 7000
NBIN_QPT = 216

# Size (half-width) of the square
SIZE = 16

# Peak finding parameters
THRESHOLD_ABS = 5      # absolute threshold
THRESHOLD_REL = 0.0    # peaks > 70% of max
MIN_DISTANCE = 2       # at least 2 bins apart
SMOOTH_SIGMA = 0       # smooth before detection

# Tolerance between reco and true peak
TOLERANCE = 6

# Slice configuration
# Options: list(range(-1, 33)), list(range(12, 20)), or [-1]
SLICE_LIST = [-1]

# Number of files to be processed
NUM_FILES = 8

# Data path
# Uncomment the path you want to use:
# PATH = "/eos/user/t/tbold/EFTracking/HoughML/ttbar_pu10_insquare"
# PATH = "/eos/user/t/tbold/EFTracking/HoughML/ttbar_pu10_insquare_full"
# PATH = "/eos/user/t/tbold/EFTracking/HoughML/ttbar_pu100_insquare"
# PATH = "/eos/user/t/tbold/EFTracking/HoughML/ttbar_pu100_insquare_full"
PATH = "/eos/user/t/tbold/EFTracking/HoughML/pg_2mu_pu100_insquare"

# Visualization parameters
VIS_START_PHI = 1000
VIS_END_PHI = 2000
VIS_SIZE_TRUE = 3
