"""Money value object for the shared kernel.

Provides a robust, immutable money representation that handles currency,
arithmetic operations, and business rules consistently across all domains.
"""

import decimal
from abc import ABC
from decimal import ROUND_HALF_UP, Decimal
from typing import Any


class BaseNumericValueObject(ABC):
    """Base class for numeric value objects with common operations.

    Provides shared functionality for validation, arithmetic operations,
    comparisons, and precision handling using Decimal.
    """

    _value: Decimal

    def __init__(
        self,
        value: float | str | Decimal,
        *,
        allow_negative: bool = True,
    ) -> None:
        """Initialize numeric value object with validation.

        Args:
            value: Numeric value (converted to Decimal for precision)
            allow_negative: Whether negative values are allowed

        Raises:
            TypeError: If value cannot be converted to Decimal
            ValueError: If value is negative when not allowed
        """
        try:
            self._value = Decimal(str(value))
        except (ValueError, TypeError, decimal.InvalidOperation) as e:
            msg = f"Value must be numeric, got {type(value).__name__}"
            raise TypeError(msg) from e

        if not allow_negative and self._value < 0:
            msg = f"{self.__class__.__name__} cannot be negative"
            raise ValueError(msg)

    @property
    def value(self) -> Decimal:
        """Get the numeric value."""
        return self._value

    def __str__(self) -> str:
        """String representation for display."""
        return str(self._value)

    def __repr__(self) -> str:
        """Developer representation."""
        return f"{self.__class__.__name__}({self._value})"

    def __eq__(self, other: object) -> bool:
        """Equality comparison."""
        if not isinstance(other, self.__class__):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """Hash for use in sets and as dict keys."""
        return hash(self._value)

    def __lt__(self, other: Any) -> bool:
        """Less than comparison."""
        if not isinstance(other, self.__class__):
            msg = (
                f"Cannot compare {self.__class__.__name__} with {type(other).__name__}"
            )
            raise TypeError(msg)
        return self._value < other._value

    def __le__(self, other: Any) -> bool:
        """Less than or equal comparison."""
        if not isinstance(other, self.__class__):
            msg = (
                f"Cannot compare {self.__class__.__name__} with {type(other).__name__}"
            )
            raise TypeError(msg)
        return self._value <= other._value

    def __gt__(self, other: Any) -> bool:
        """Greater than comparison."""
        if not isinstance(other, self.__class__):
            msg = (
                f"Cannot compare {self.__class__.__name__} with {type(other).__name__}"
            )
            raise TypeError(msg)
        return self._value > other._value

    def __ge__(self, other: Any) -> bool:
        """Greater than or equal comparison."""
        if not isinstance(other, self.__class__):
            msg = (
                f"Cannot compare {self.__class__.__name__} with {type(other).__name__}"
            )
            raise TypeError(msg)
        return self._value >= other._value

    def __add__(self, other: Any) -> "BaseNumericValueObject":
        """Add two instances of the same type."""
        if isinstance(other, self.__class__):
            return self.__class__(self._value + other._value)
        if isinstance(other, int | float | Decimal):
            return self.__class__(self._value + Decimal(str(other)))
        raise TypeError(
            f"Can only add {self.__class__.__name__} to {self.__class__.__name__} "
            + "or numeric types",
        )

    def __sub__(self, other: Any) -> "BaseNumericValueObject":
        """Subtract instances or numeric values."""
        if isinstance(other, self.__class__):
            result_value = self._value - other._value
        elif isinstance(other, int | float | Decimal):
            result_value = self._value - Decimal(str(other))
        else:
            raise TypeError(
                f"Can only subtract {self.__class__.__name__} or numeric types "
                + f"from {self.__class__.__name__}",
            )

        return self.__class__(result_value)

    def __mul__(self, scalar: float | Decimal) -> "BaseNumericValueObject":
        """Multiply by a scalar."""
        return self.__class__(self._value * Decimal(str(scalar)))

    def __rmul__(self, scalar: float | Decimal) -> "BaseNumericValueObject":
        """Right multiplication (scalar * instance)."""
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float | Decimal) -> "BaseNumericValueObject":
        """Divide by a scalar."""
        if scalar == 0:
            msg = "Cannot divide by zero"
            raise ZeroDivisionError(msg)
        return self.__class__(self._value / Decimal(str(scalar)))

    def __neg__(self) -> "BaseNumericValueObject":
        """Negate the value."""
        return self.__class__(-self._value)

    def __abs__(self) -> "BaseNumericValueObject":
        """Absolute value."""
        return self.__class__(abs(self._value))

    def is_zero(self) -> bool:
        """Check if value is zero."""
        return self._value == Decimal("0")

    def is_positive(self) -> bool:
        """Check if value is positive."""
        return self._value > Decimal("0")

    def is_negative(self) -> bool:
        """Check if value is negative."""
        return self._value < Decimal("0")

    @classmethod
    def zero(cls) -> "BaseNumericValueObject":
        """Create zero instance."""
        return cls(Decimal("0"))


class Money(BaseNumericValueObject):
    """Simplified immutable value object representing USD monetary amounts.

    Focused on essential operations for stock tracking without multi-currency
    complexity or advanced allocation features.
    """

    def __init__(self, amount: float | str | Decimal) -> None:
        """Initialize Money with USD amount.

        Args:
            amount: Monetary amount (converted to Decimal for precision)

        Raises:
            TypeError: If amount cannot be converted to Decimal
        """
        super().__init__(amount, allow_negative=True)
        # Round to currency precision (2 decimal places)
        self._value = self._value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def amount(self) -> Decimal:
        """Get the monetary amount (for backward compatibility)."""
        return self._value

    def __str__(self) -> str:
        """String representation for display."""
        formatted_amount = self._value.quantize(Decimal("0.01"))
        return f"${formatted_amount}"

    def __repr__(self) -> str:
        """Developer representation."""
        formatted_amount = self._value.quantize(Decimal("0.01"))
        return f"Money({formatted_amount})"

    def __add__(self, other: Any) -> "Money":
        """Add two Money instances."""
        if not isinstance(other, Money):
            msg = "Can only add Money to Money"
            raise TypeError(msg)
        return Money(self._value + other._value)

    def __sub__(self, other: Any) -> "Money":
        """Subtract two Money instances."""
        if not isinstance(other, Money):
            msg = "Can only subtract Money from Money"
            raise TypeError(msg)
        return Money(self._value - other._value)

    def __mul__(self, scalar: float | Decimal) -> "Money":
        """Multiply Money by a scalar."""
        return Money(self._value * Decimal(str(scalar)))

    def __truediv__(self, scalar: float | Decimal) -> "Money":
        """Divide Money by a scalar."""
        if scalar == 0:
            msg = "Cannot divide by zero"
            raise ZeroDivisionError(msg)
        return Money(self._value / Decimal(str(scalar)))

    def __neg__(self) -> "Money":
        """Negate Money amount."""
        return Money(-self._value)

    def __abs__(self) -> "Money":
        """Absolute value of Money."""
        return Money(abs(self._value))

    @classmethod
    def zero(cls) -> "Money":
        """Create zero money."""
        return cls(Decimal("0"))

    @classmethod
    def from_cents(cls, cents: int) -> "Money":
        """Create money from cents."""
        amount = Decimal(cents) / Decimal("100")
        return cls(amount)

    def to_cents(self) -> int:
        """Convert Money to cents."""
        return int(self._value * 100)
