"""
HoughSlicer class for track slicing with different easing functions.
"""

import math
from dataclasses import dataclass


@dataclass
class HoughMeasurementStruct:
    """Structure to hold Hough measurement data."""
    cot: float
    vz: float


class HoughSlicer:
    """
    Implements track slicing with various easing functions.

    Attributes:
    -----------
    easing_type : str
        Type of easing function ('InSine', 'InSquare', 'InCubic', 'InCirc', or 'Linear')
    """

    def __init__(self, easing_type: str = "InSquare"):
        """
        Initialize HoughSlicer with specified easing type.

        Parameters:
        -----------
        easing_type : str
            Type of easing function to use
        """
        self.easing_type = easing_type

    def easing(self, x: float) -> float:
        """
        Apply easing function to input value.

        Parameters:
        -----------
        x : float
            Input value

        Returns:
        --------
        float
            Eased output value
        """
        if self.easing_type == "InSine":
            sign = 1 if x > 0 else (-1 if x < 0 else 0)
            return sign * 32 * (1 - math.cos((x * math.pi) / 64))
        elif self.easing_type == "InSquare":
            sign = 1 if x > 0 else (-1 if x < 0 else 0)
            return sign * 32 * (x * x / 1024)
        elif self.easing_type == "InCubic":
            return 32 * (x * x * x / 32768)
        elif self.easing_type == "InCirc":
            sign = 1 if x > 0 else (-1 if x < 0 else 0)
            return sign * (32 - math.sqrt(1024 - x * x))
        else:  # Linear
            return x

    def __call__(self, slice_num: int) -> tuple:
        """
        Calculate cotangent bounds for a given slice.

        Parameters:
        -----------
        slice_num : int
            Slice number (-1 for full range, 0-32 for specific slices)

        Returns:
        --------
        tuple
            (lo_cot, hi_cot) - Lower and upper cotangent bounds
        """
        if slice_num == -1:
            # For slice -1, return None to indicate full vz range check
            return None, None
        else:
            lo_cot = self.easing(-32.0 + 2.0 * max(slice_num, 0))
            # We take true tracks from 1 neighbouring slice
            hi_cot = self.easing(-32.0 + 2.0 * min(slice_num + 1, 32))
            return lo_cot, hi_cot
