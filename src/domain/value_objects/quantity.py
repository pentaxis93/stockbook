"""
Quantity value object for the shared kernel.

Provides a robust, immutable quantity representation that handles numeric
operations and business rules consistently across all domains.
"""

from decimal import Decimal
from typing import Union

from .money import BaseNumericValueObject


class Quantity(BaseNumericValueObject):
    """
    Simplified immutable value object representing quantities.

    Focused on essential operations for stock share quantities and basic
    numeric values without complex mathematical operations.
    """

    def __init__(self, value: Union[int, float, str, Decimal]):
        """
        Initialize Quantity with a numeric value.

        Args:
            value: Numeric value (converted to Decimal for precision)

        Raises:
            TypeError: If value cannot be converted to Decimal
            ValueError: If value is negative
        """
        super().__init__(value, allow_negative=False)

    def __add__(self, other) -> "Quantity":
        """Add two Quantity instances."""
        if isinstance(other, Quantity):
            return Quantity(self._value + other._value)
        if isinstance(other, (int, float, Decimal)):
            return Quantity(self._value + Decimal(str(other)))

        raise TypeError("Can only add Quantity or numeric types to Quantity")

    def __sub__(self, other) -> "Quantity":
        """Subtract Quantity from this Quantity."""
        if isinstance(other, Quantity):
            result_value = self._value - other._value
        elif isinstance(other, (int, float, Decimal)):
            result_value = self._value - Decimal(str(other))
        else:
            raise TypeError("Can only subtract Quantity or numeric types from Quantity")

        if result_value < 0:
            raise ValueError("Resulting quantity cannot be negative")

        return Quantity(result_value)

    def __mul__(self, scalar) -> "Quantity":
        """Multiply Quantity by a scalar."""
        if isinstance(scalar, (int, float, Decimal)):
            return Quantity(self._value * Decimal(str(scalar)))
        raise TypeError("Can only multiply Quantity by numeric types")

    def __truediv__(self, scalar) -> "Quantity":
        """Divide Quantity by a scalar."""
        if isinstance(scalar, (int, float, Decimal)):
            if scalar == 0:
                raise ZeroDivisionError("Cannot divide by zero")
            return Quantity(self._value / Decimal(str(scalar)))
        raise TypeError("Can only divide Quantity by numeric types")

    def is_whole(self) -> bool:
        """Check if quantity is a whole number."""
        return self._value % 1 == 0

    @classmethod
    def zero(cls) -> "Quantity":
        """Create zero quantity."""
        return cls(Decimal("0"))
