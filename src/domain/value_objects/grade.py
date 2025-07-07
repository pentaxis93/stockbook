"""Grade value object for the StockBook domain.

Represents a stock grade with validation rules and immutability.
"""

from typing import Any, ClassVar


class Grade:
    """Value object representing a stock grade.

    Encapsulates validation logic for grades and ensures immutability.
    """

    VALID_GRADES: ClassVar[set[str]] = {"A", "B", "C", "D", "F"}
    _value: str

    def __init__(self, value: str) -> None:
        """Initialize Grade with validation.

        Args:
            value: The grade string (A, B, C, D, F)

        Raises:
            ValueError: If grade is not a valid grade or is empty
        """
        # Strip whitespace and normalize to uppercase
        normalized_value = value.strip().upper()

        # Validate not empty
        if not normalized_value:
            raise ValueError("Grade cannot be empty")

        # Validate grade is valid
        if normalized_value not in self.VALID_GRADES:
            raise ValueError(f"Grade must be one of {self.VALID_GRADES}")

        # Store as private attribute to prevent mutation
        object.__setattr__(self, "_value", normalized_value)

    @property
    def value(self) -> str:
        """Get the grade value."""
        return self._value

    def __str__(self) -> str:
        """String representation of the grade."""
        return self._value

    def __repr__(self) -> str:
        """Developer representation of the grade."""
        return f"Grade({self._value!r})"

    def __eq__(self, other: Any) -> bool:
        """Check equality based on value."""
        if not isinstance(other, Grade):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """Hash based on value for use in collections."""
        return hash(self._value)

    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent mutation after initialization."""
        if hasattr(self, "_value"):
            raise AttributeError("Grade is immutable")
        super().__setattr__(name, value)
