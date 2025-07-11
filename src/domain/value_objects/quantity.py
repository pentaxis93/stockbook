"""Quantity value object for the shared kernel.

Provides a robust, immutable quantity representation that handles numeric
operations and business rules consistently across all domains.
"""

from decimal import Decimal
from typing import Any

from .money import BaseNumericValueObject


class Quantity(BaseNumericValueObject):
    """Simplified immutable value object representing quantities.

    Focused on essential operations for stock share quantities and basic
    numeric values without complex mathematical operations.
    """

    def __init__(self, value: float | str | Decimal) -> None:
        """Initialize Quantity with a numeric value.

        Args:
            value: Numeric value (converted to Decimal for precision)

        Raises:
            TypeError: If value cannot be converted to Decimal
            ValueError: If value is negative
        """
        super().__init__(value, allow_negative=False)

    def __add__(self, other: Any) -> "Quantity":
        """Add two Quantity instances."""
        if isinstance(other, Quantity):
            return Quantity(self._value + other._value)
        if isinstance(other, int | float | Decimal):
            return Quantity(self._value + Decimal(str(other)))

        msg = "Can only add Quantity or numeric types to Quantity"
        raise TypeError(msg)

    def __sub__(self, other: Any) -> "Quantity":
        """Subtract Quantity from this Quantity."""
        if isinstance(other, Quantity):
            result_value = self._value - other._value
        elif isinstance(other, int | float | Decimal):
            result_value = self._value - Decimal(str(other))
        else:
            msg = "Can only subtract Quantity or numeric types from Quantity"
            raise TypeError(msg)

        if result_value < 0:
            msg = "Resulting quantity cannot be negative"
            raise ValueError(msg)

        return Quantity(result_value)

    def __mul__(self, scalar: float | Decimal) -> "Quantity":
        """Multiply Quantity by a scalar."""
        return Quantity(self._value * Decimal(str(scalar)))

    def __truediv__(self, scalar: float | Decimal) -> "Quantity":
        """Divide Quantity by a scalar."""
        if scalar == 0:
            msg = "Cannot divide by zero"
            raise ZeroDivisionError(msg)
        return Quantity(self._value / Decimal(str(scalar)))

    def is_whole(self) -> bool:
        """Check if quantity is a whole number."""
        return self._value % 1 == 0

    @classmethod
    def zero(cls) -> "Quantity":
        """Create zero quantity."""
        return cls(Decimal("0"))
