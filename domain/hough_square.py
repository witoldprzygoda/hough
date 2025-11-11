"""
Hough square domain models for training data.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List
import numpy as np


class SquareClassification(Enum):
    """Classification of Hough squares."""
    TRUE_POSITIVE = "true_positive"
    FALSE_POSITIVE = "false_positive"
    UNCLASSIFIED = "unclassified"


@dataclass(frozen=True)
class HoughSquare:
    """
    Immutable value object representing a square region in Hough space.

    Attributes:
        data: 2D numpy array of intensity values
        classification: Classification of the square
        center_x: X-coordinate of center
        center_y: Y-coordinate of center
    """
    data: np.ndarray
    classification: SquareClassification
    center_x: float
    center_y: float

    def __post_init__(self):
        """Validate data dimensions."""
        if self.data.ndim != 2:
            raise ValueError("Square data must be 2-dimensional")
        if self.data.shape[0] != self.data.shape[1]:
            raise ValueError("Square data must have equal dimensions")

    @property
    def size(self) -> int:
        """Get size of square (width/height)."""
        return self.data.shape[0]

    @property
    def is_true_positive(self) -> bool:
        """Check if square is classified as true positive."""
        return self.classification == SquareClassification.TRUE_POSITIVE

    @property
    def is_false_positive(self) -> bool:
        """Check if square is classified as false positive."""
        return self.classification == SquareClassification.FALSE_POSITIVE

    def get_max_value(self) -> float:
        """Get maximum intensity value in square."""
        return np.max(self.data)

    def get_mean_value(self) -> float:
        """Get mean intensity value in square."""
        return np.mean(self.data)

    def to_flat_array(self) -> np.ndarray:
        """Flatten square data to 1D array."""
        return self.data.flatten()


class HoughSquareCollection:
    """
    Collection of Hough squares for training data.

    Manages true positive and false positive squares separately.
    """

    def __init__(self):
        """Initialize empty collections."""
        self._true_positives: List[HoughSquare] = []
        self._false_positives: List[HoughSquare] = []

    def add_true_positive(self, square: HoughSquare) -> None:
        """Add a true positive square."""
        if not square.is_true_positive:
            raise ValueError("Square must be classified as TRUE_POSITIVE")
        self._true_positives.append(square)

    def add_false_positive(self, square: HoughSquare) -> None:
        """Add a false positive square."""
        if not square.is_false_positive:
            raise ValueError("Square must be classified as FALSE_POSITIVE")
        self._false_positives.append(square)

    def add_square(self, square: HoughSquare) -> None:
        """Add square based on its classification."""
        if square.is_true_positive:
            self.add_true_positive(square)
        elif square.is_false_positive:
            self.add_false_positive(square)
        else:
            raise ValueError("Cannot add unclassified square")

    @property
    def true_positive_count(self) -> int:
        """Get count of true positive squares."""
        return len(self._true_positives)

    @property
    def false_positive_count(self) -> int:
        """Get count of false positive squares."""
        return len(self._false_positives)

    @property
    def total_count(self) -> int:
        """Get total count of all squares."""
        return self.true_positive_count + self.false_positive_count

    def get_training_data(self) -> tuple:
        """
        Get training data as numpy arrays.

        Returns:
            Tuple of (X, y) where X is feature array and y is label array
        """
        if self.total_count == 0:
            return np.empty((0, 0)), np.empty(0)

        # Stack true positives
        true_data = np.stack([sq.data for sq in self._true_positives], axis=0)
        true_labels = np.ones(len(self._true_positives))

        # Stack false positives
        false_data = np.stack([sq.data for sq in self._false_positives], axis=0)
        false_labels = np.zeros(len(self._false_positives))

        # Combine
        X = np.vstack([true_data, false_data])
        y = np.hstack([true_labels, false_labels])

        return X, y

    def clear(self) -> None:
        """Clear all squares from collection."""
        self._true_positives.clear()
        self._false_positives.clear()

    def summary(self) -> dict:
        """
        Get summary statistics.

        Returns:
            Dictionary with summary information
        """
        return {
            'true_positives': self.true_positive_count,
            'false_positives': self.false_positive_count,
            'total': self.total_count,
            'true_positive_ratio': (
                self.true_positive_count / self.total_count
                if self.total_count > 0 else 0.0
            )
        }
