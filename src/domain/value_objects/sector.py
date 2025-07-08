"""Sector value object for the StockBook domain.

Represents a sector classification with validation rules and immutability.
"""

from typing import Any

from src.domain.value_objects.sector_industry_data import (
    SECTOR_INDUSTRY_MAPPING,
    get_all_valid_sectors,
)


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
            ValueError: If sector exceeds maximum length, is empty, or is invalid
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

        # Validate that the sector exists in our domain mapping
        if normalized_value not in get_all_valid_sectors():
            msg = f"Invalid sector '{normalized_value}'"
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

    def is_valid_industry_group(self, industry_group: str) -> bool:
        """Check if an industry group is valid for this sector.

        Args:
            industry_group: The industry group to check

        Returns:
            True if the industry group belongs to this sector, False otherwise
        """
        return industry_group in SECTOR_INDUSTRY_MAPPING.get(self._value, [])

    def get_industry_groups(self) -> list[str]:
        """Get the list of valid industry groups for this sector.

        Returns:
            List of industry group names that belong to this sector
        """
        return SECTOR_INDUSTRY_MAPPING.get(self._value, [])
