"""PortfolioName value object for the StockBook domain.

Represents portfolio names with validation rules and immutability.
"""

from typing import Any


class PortfolioName:
    """Value object representing a portfolio name.

    Encapsulates validation logic for portfolio names and ensures immutability.
    Portfolio names must be non-empty and cannot exceed 100 characters.
    """

    MAX_LENGTH = 100
    _value: str

    def __init__(self, value: str) -> None:
        """Initialize PortfolioName with validation.

        Args:
            value: The portfolio name string

        Raises:
            TypeError: If value is not a string
            ValueError: If portfolio name is empty or exceeds maximum length
        """
        # Strip whitespace
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError("Portfolio name cannot be empty")

        if len(normalized_value) > self.MAX_LENGTH:
            raise ValueError(
                f"Portfolio name cannot exceed {self.MAX_LENGTH} characters"
            )

        # Store as private attribute to prevent mutation
        object.__setattr__(self, "_value", normalized_value)

    @property
    def value(self) -> str:
        """Get the portfolio name value."""
        return self._value

    def __str__(self) -> str:
        """String representation of the portfolio name."""
        return self._value

    def __repr__(self) -> str:
        """Developer representation of the portfolio name."""
        return f"PortfolioName({self._value!r})"

    def __eq__(self, other: Any) -> bool:
        """Check equality based on value."""
        if not isinstance(other, PortfolioName):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """Hash based on value for use in collections."""
        return hash(self._value)

    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent mutation after initialization."""
        if hasattr(self, "_value"):
            raise AttributeError("PortfolioName is immutable")
        super().__setattr__(name, value)
