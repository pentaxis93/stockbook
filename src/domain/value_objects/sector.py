"""Sector value object for the StockBook domain.

Represents a sector classification with validation rules and immutability.
"""

from typing import Any


class Sector:
    """Value object representing a sector.

    Encapsulates validation logic for sectors and ensures immutability.
    """

    MAX_LENGTH = 100
    _value: str

    def __init__(self, value: str) -> None:
        """Initialize Sector with validation.

        Args:
            value: The sector string

        Raises:
            ValueError: If sector exceeds maximum length or is empty
        """
        # Strip whitespace
        normalized_value = value.strip()

        # Validate not empty
        if not normalized_value:
            msg = "Sector cannot be empty"
            raise ValueError(msg)

        # Validate length
        if len(normalized_value) > self.MAX_LENGTH:
            msg = f"Sector cannot exceed {self.MAX_LENGTH} characters"
            raise ValueError(msg)

        # Store as private attribute to prevent mutation
        object.__setattr__(self, "_value", normalized_value)

    @property
    def value(self) -> str:
        """Get the sector value."""
        return self._value

    def __str__(self) -> str:
        """String representation of the sector."""
        return self._value

    def __repr__(self) -> str:
        """Developer representation of the sector."""
        return f"Sector({self._value!r})"

    def __eq__(self, other: object) -> bool:
        """Check equality based on value."""
        if not isinstance(other, Sector):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """Hash based on value for use in collections."""
        return hash(self._value)

    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent mutation after initialization."""
        if hasattr(self, "_value"):
            msg = "Sector is immutable"
            raise AttributeError(msg)
        super().__setattr__(name, value)
