"""
Repository for training data persistence.
"""

from pathlib import Path
from typing import Tuple
import numpy as np

from domain.hough_square import HoughSquareCollection


class TrainingDataRepository:
    """
    Repository for saving and loading training data.

    Responsibilities:
    - Save training data to disk
    - Load training data from disk
    - Manage file formats
    """

    def __init__(self, output_dir: Path):
        """
        Initialize repository with output directory.

        Args:
            output_dir: Directory for saving training data
        """
        self._output_dir = output_dir
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def save_squares(self, collection: HoughSquareCollection,
                     filename: str = "images.npz") -> None:
        """
        Save Hough square collection to compressed numpy file.

        Args:
            collection: HoughSquareCollection to save
            filename: Output filename
        """
        X, y = collection.get_training_data()

        file_path = self._output_dir / filename
        np.savez(file_path, X=X, y=y)

        summary = collection.summary()
        print(f"\nTraining data saved to {file_path}")
        print(f"True positives: {summary['true_positives']}")
        print(f"False positives: {summary['false_positives']}")
        print(f"Total samples: {summary['total']}")
        print(f"Array shapes: X={X.shape}, y={y.shape}")

    def load_squares(self, filename: str = "images.npz") -> Tuple[np.ndarray, np.ndarray]:
        """
        Load training data from file.

        Args:
            filename: Input filename

        Returns:
            Tuple of (X, y) arrays
        """
        file_path = self._output_dir / filename
        data = np.load(file_path)
        return data['X'], data['y']

    def save_arrays(self, X: np.ndarray, y: np.ndarray,
                   filename: str = "images.npz") -> None:
        """
        Save numpy arrays directly.

        Args:
            X: Feature array
            y: Label array
            filename: Output filename
        """
        file_path = self._output_dir / filename
        np.savez(file_path, X=X, y=y)
        print(f"Arrays saved to {file_path}: X={X.shape}, y={y.shape}")
