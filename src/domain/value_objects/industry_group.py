"""IndustryGroup value object for the StockBook domain.

Represents an industry group classification with validation rules and immutability.
"""

from typing import Any

from src.domain.value_objects.sector_industry_data import (
    get_all_valid_industry_groups,
    get_sector_for_industry,
)


class IndustryGroup:
    """Value object representing an industry group.

    Encapsulates validation logic for industry groups and ensures immutability.
    """

    MAX_LENGTH = 100
    _value: str
    _sector: str | None

    def __init__(self, value: str, *, sector: str | None = None) -> None:
        """Initialize IndustryGroup with validation.

        Args:
            value: The industry group string
            sector: Optional sector to validate against

        Raises:
            ValueError: If industry group exceeds maximum length, is invalid,
                      or doesn't match the provided sector
        """
        # Strip whitespace
        normalized_value = value.strip()

        # Validate length
        if len(normalized_value) > self.MAX_LENGTH:
            msg = f"Industry group cannot exceed {self.MAX_LENGTH} characters"
            raise ValueError(msg)

        # Validate that the industry group exists in our domain mapping
        # Empty string is allowed
        if normalized_value and normalized_value not in get_all_valid_industry_groups():
            msg = f"Invalid industry group '{normalized_value}'"
            raise ValueError(msg)

        # Get the sector this industry group belongs to
        expected_sector = (
            get_sector_for_industry(normalized_value) if normalized_value else None
        )

        # If sector is provided, validate it matches
        if (
            sector is not None
            and expected_sector is not None
            and sector != expected_sector
        ):
            msg = (
                f"Industry Group '{normalized_value}' belongs to sector "
                f"'{expected_sector}', not '{sector}'"
            )
            raise ValueError(msg)

        # Store as private attributes to prevent mutation
        object.__setattr__(self, "_value", normalized_value)
        object.__setattr__(self, "_sector", expected_sector)

    @property
    def value(self) -> str:
        """Get the industry group value."""
        return self._value

    @property
    def sector(self) -> str | None:
        """Get the sector this industry group belongs to."""
        return self._sector

    def __str__(self) -> str:
        """String representation of the industry group."""
        return self._value

    def __repr__(self) -> str:
        """Developer representation of the industry group."""
        return f"IndustryGroup({self._value!r})"

    def __eq__(self, other: object) -> bool:
        """Check equality based on value."""
        if not isinstance(other, IndustryGroup):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """Hash based on value for use in collections."""
        return hash(self._value)

    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent mutation after initialization."""
        if hasattr(self, "_value"):
            msg = "IndustryGroup is immutable"
            raise AttributeError(msg)
        super().__setattr__(name, value)
