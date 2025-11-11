"""
Strategy pattern for easing functions.

Implements different mathematical easing functions for track slicing.
"""

from abc import ABC, abstractmethod
import math
from typing import Dict, Type


class EasingStrategy(ABC):
    """
    Abstract base class for easing strategies.

    Implements Strategy pattern for different easing algorithms.
    """

    @abstractmethod
    def ease(self, x: float) -> float:
        """
        Apply easing function to input value.

        Args:
            x: Input value

        Returns:
            Eased output value
        """
        pass

    @abstractmethod
    def name(self) -> str:
        """Return the name of the easing strategy."""
        pass


class LinearEasing(EasingStrategy):
    """Linear easing (no transformation)."""

    def ease(self, x: float) -> float:
        """Apply linear easing (identity function)."""
        return x

    def name(self) -> str:
        """Return strategy name."""
        return "Linear"


class InSineEasing(EasingStrategy):
    """Sine-based easing function."""

    def ease(self, x: float) -> float:
        """Apply sine easing."""
        sign = 1 if x > 0 else (-1 if x < 0 else 0)
        return sign * 32 * (1 - math.cos((x * math.pi) / 64))

    def name(self) -> str:
        """Return strategy name."""
        return "InSine"


class InSquareEasing(EasingStrategy):
    """Square-based easing function."""

    def ease(self, x: float) -> float:
        """Apply square easing."""
        sign = 1 if x > 0 else (-1 if x < 0 else 0)
        return sign * 32 * (x * x / 1024)

    def name(self) -> str:
        """Return strategy name."""
        return "InSquare"


class InCubicEasing(EasingStrategy):
    """Cubic-based easing function."""

    def ease(self, x: float) -> float:
        """Apply cubic easing."""
        return 32 * (x * x * x / 32768)

    def name(self) -> str:
        """Return strategy name."""
        return "InCirc"


class InCircEasing(EasingStrategy):
    """Circular-based easing function."""

    def ease(self, x: float) -> float:
        """Apply circular easing."""
        sign = 1 if x > 0 else (-1 if x < 0 else 0)
        return sign * (32 - math.sqrt(1024 - x * x))

    def name(self) -> str:
        """Return strategy name."""
        return "InCirc"


class EasingStrategyFactory:
    """
    Factory for creating easing strategy instances.

    Implements Factory pattern.
    """

    _strategies: Dict[str, Type[EasingStrategy]] = {
        "Linear": LinearEasing,
        "InSine": InSineEasing,
        "InSquare": InSquareEasing,
        "InCubic": InCubicEasing,
        "InCirc": InCircEasing,
    }

    @classmethod
    def create(cls, strategy_name: str) -> EasingStrategy:
        """
        Create an easing strategy by name.

        Args:
            strategy_name: Name of the strategy

        Returns:
            Instance of the requested strategy

        Raises:
            ValueError: If strategy name is unknown
        """
        strategy_class = cls._strategies.get(strategy_name)
        if strategy_class is None:
            available = ", ".join(cls._strategies.keys())
            raise ValueError(
                f"Unknown easing strategy: {strategy_name}. "
                f"Available strategies: {available}"
            )
        return strategy_class()

    @classmethod
    def register_strategy(cls, name: str, strategy_class: Type[EasingStrategy]) -> None:
        """
        Register a custom easing strategy.

        Args:
            name: Name for the strategy
            strategy_class: Class implementing EasingStrategy
        """
        cls._strategies[name] = strategy_class

    @classmethod
    def available_strategies(cls) -> list:
        """Get list of available strategy names."""
        return list(cls._strategies.keys())
