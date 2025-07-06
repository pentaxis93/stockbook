"""Notes value object for the StockBook domain.

Represents notes/comments with validation rules and immutability.
"""

from abc import ABC
from typing import Any


class BaseTextValueObject(ABC):
    """Base class for text-based value objects with validation.

    Provides common functionality for text validation, normalization,
    and immutability enforcement.
    """

    _value: str

    def __init__(
        self, value: str, max_length: int | None = None, allow_empty: bool = True
    ):
        """Initialize text value object with validation.

        Args:
            value: The text value
            max_length: Maximum allowed length (None for no limit)
            allow_empty: Whether empty strings are allowed

        Raises:
            TypeError: If value is not a string
            ValueError: If validation fails
        """
        # Strip whitespace
        normalized_value = value.strip()

        # Check empty constraint
        if not allow_empty and not normalized_value:
            raise ValueError(f"{self.__class__.__name__} cannot be empty")

        # Check length constraint
        if max_length is not None and len(normalized_value) > max_length:
            raise ValueError(
                f"{self.__class__.__name__} cannot exceed {max_length} characters"
            )

        # Store as private attribute to prevent mutation
        object.__setattr__(self, "_value", normalized_value)

    @property
    def value(self) -> str:
        """Get the text value."""
        return self._value

    def has_content(self) -> bool:
        """Check if value has content.

        Returns:
            True if value has non-empty content, False otherwise
        """
        return bool(self._value)

    def __str__(self) -> str:
        """String representation of the value."""
        return self._value

    def __repr__(self) -> str:
        """Developer representation of the value."""
        return f"{self.__class__.__name__}({self._value!r})"

    def __eq__(self, other: Any) -> bool:
        """Check equality based on value."""
        if not isinstance(other, self.__class__):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """Hash based on value for use in collections."""
        return hash(self._value)

    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent mutation after initialization."""
        if hasattr(self, "_value"):
            raise AttributeError(f"{self.__class__.__name__} is immutable")
        super().__setattr__(name, value)


class Notes(BaseTextValueObject):
    """Value object representing notes/comments.

    Encapsulates validation logic for notes and ensures immutability.
    """

    MAX_LENGTH = 1000

    def __init__(self, value: str):
        """Initialize Notes with validation.

        Args:
            value: The notes string

        Raises:
            ValueError: If notes exceed maximum length
        """
        try:
            super().__init__(value, max_length=self.MAX_LENGTH, allow_empty=True)
        except ValueError as e:
            if "cannot exceed" in str(e):
                raise ValueError(
                    f"Notes cannot exceed {self.MAX_LENGTH} characters"
                ) from e
            raise
