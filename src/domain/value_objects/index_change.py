"""
IndexChange value object for the StockBook domain.

Represents percentage change in portfolio index with validation rules and immutability.
"""

from typing import Any


class IndexChange:
    """
    Value object representing a portfolio index change percentage.

    Encapsulates validation logic for index changes and ensures immutability.
    Valid changes are between -100% and +100%.
    """

    MIN_CHANGE = -100.0
    MAX_CHANGE = 100.0
    _value: float

    def __init__(self, value: int | float):
        """
        Initialize IndexChange with validation.

        Args:
            value: The index change percentage as a float

        Raises:
            ValueError: If index change is outside valid range
        """
        # Type checking is handled by type annotations

        # Convert to float and round to 2 decimal places
        normalized_value = round(float(value), 2)

        if normalized_value < self.MIN_CHANGE or normalized_value > self.MAX_CHANGE:
            raise ValueError(
                f"Index change cannot exceed {self.MAX_CHANGE}% or be less than {self.MIN_CHANGE}%"
            )

        # Store as private attribute to prevent mutation
        object.__setattr__(self, "_value", normalized_value)

    @property
    def value(self) -> float:
        """Get the index change value."""
        return self._value

    def is_positive(self) -> bool:
        """Check if the change is positive."""
        return self._value > 0.0

    def is_negative(self) -> bool:
        """Check if the change is negative."""
        return self._value < 0.0

    def is_neutral(self) -> bool:
        """Check if the change is neutral (zero)."""
        return self._value == 0.0

    def __str__(self) -> str:
        """String representation of the index change."""
        return f"{self._value:+.2f}%"

    def __repr__(self) -> str:
        """Developer representation of the index change."""
        return f"IndexChange({self._value})"

    def __eq__(self, other: Any) -> bool:
        """Check equality based on value."""
        if not isinstance(other, IndexChange):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """Hash based on value for use in collections."""
        return hash(self._value)

    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent mutation after initialization."""
        if hasattr(self, "_value"):
            raise AttributeError("IndexChange is immutable")
        super().__setattr__(name, value)
