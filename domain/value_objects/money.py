"""
Money value object for financial calculations.

Represents monetary amounts with currency, ensuring type safety
and proper precision handling for financial operations.
"""

import re
from decimal import ROUND_HALF_UP, Decimal
from typing import Union


class Money:
    """
    Immutable value object representing monetary amounts.

    Ensures proper precision, currency validation, and mathematical operations
    while maintaining immutability and value semantics.
    """

    # Valid currency codes (simplified set for now)
    VALID_CURRENCIES = {"USD", "CAD", "EUR", "GBP", "JPY"}

    # Private attributes for type checking
    _amount: Decimal
    _currency: str

    def __init__(self, amount: Union[Decimal, str, int, float], currency: str):
        """
        Initialize Money with amount and currency.

        Args:
            amount: Monetary amount (will be converted to Decimal)
            currency: 3-letter currency code

        Raises:
            ValueError: If amount is negative or currency is invalid
        """
        # Convert amount to Decimal for precision
        if isinstance(amount, float):
            # Handle float precision issues by converting through string
            amount = Decimal(str(amount))
        else:
            amount = Decimal(amount)

        # Round to 2 decimal places for currency precision
        amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Validate amount (non-negative for trading context)
        if amount < 0:
            raise ValueError("Amount cannot be negative")

        # Validate currency
        if not self._is_valid_currency(currency):
            raise ValueError("Currency must be a valid 3-letter code")

        # Use object.__setattr__ to bypass immutability during initialization
        object.__setattr__(self, "_amount", amount)
        object.__setattr__(self, "_currency", currency.upper())

    @property
    def amount(self) -> Decimal:
        """Get the monetary amount."""
        return self._amount

    @property
    def currency(self) -> str:
        """Get the currency code."""
        return self._currency

    def __setattr__(self, name, value):
        """Prevent modification after initialization (immutability)."""
        if hasattr(self, "_amount"):  # Object is already initialized
            raise AttributeError(f"Cannot modify immutable Money object")
        super().__setattr__(name, value)

    def __eq__(self, other) -> bool:
        """Check equality with another Money object."""
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency

    def __hash__(self) -> int:
        """Make Money hashable for use in sets/dicts."""
        return hash((self.amount, self.currency))

    def __add__(self, other: "Money") -> "Money":
        """Add two Money objects (same currency only)."""
        if not isinstance(other, Money):
            raise TypeError("Can only add Money to Money")

        if self.currency != other.currency:
            raise ValueError("Cannot perform operations on different currencies")

        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        """Subtract two Money objects (same currency only)."""
        if not isinstance(other, Money):
            raise TypeError("Can only subtract Money from Money")

        if self.currency != other.currency:
            raise ValueError("Cannot perform operations on different currencies")

        result_amount = self.amount - other.amount
        if result_amount < 0:
            raise ValueError("Result cannot be negative")

        return Money(result_amount, self.currency)

    def __mul__(self, other: Union[Decimal, int, float]) -> "Money":
        """Multiply Money by a scalar value."""
        if isinstance(other, (int, float)):
            other = Decimal(str(other))
        elif not isinstance(other, Decimal):
            raise TypeError("Can only multiply Money by numeric values")

        return Money(self.amount * other, self.currency)

    def __rmul__(self, other: Union[Decimal, int, float]) -> "Money":
        """Right multiplication (scalar * Money)."""
        return self.__mul__(other)

    def __truediv__(self, other: Union[Decimal, int, float]) -> "Money":
        """Divide Money by a scalar value."""
        if isinstance(other, (int, float)):
            other = Decimal(str(other))
        elif not isinstance(other, Decimal):
            raise TypeError("Can only divide Money by numeric values")

        if other == 0:
            raise ValueError("Cannot divide by zero")

        return Money(self.amount / other, self.currency)

    def __lt__(self, other: "Money") -> bool:
        """Less than comparison."""
        self._validate_same_currency(other)
        return self.amount < other.amount

    def __le__(self, other: "Money") -> bool:
        """Less than or equal comparison."""
        self._validate_same_currency(other)
        return self.amount <= other.amount

    def __gt__(self, other: "Money") -> bool:
        """Greater than comparison."""
        self._validate_same_currency(other)
        return self.amount > other.amount

    def __ge__(self, other: "Money") -> bool:
        """Greater than or equal comparison."""
        self._validate_same_currency(other)
        return self.amount >= other.amount

    def __str__(self) -> str:
        """String representation for display."""
        return f"{self.amount} {self.currency}"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"Money({self.amount}, '{self.currency}')"

    def _validate_same_currency(self, other: "Money") -> None:
        """Validate that another Money object has the same currency."""
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money objects")

        if self.currency != other.currency:
            raise ValueError("Cannot compare different currencies")

    @staticmethod
    def _is_valid_currency(currency: str) -> bool:
        """Validate currency code format and value."""
        if not currency or len(currency) != 3:
            return False

        # Check if it's a valid pattern (3 uppercase letters)
        if not re.match(r"^[A-Z]{3}$", currency.upper()):
            return False

        # Check against known currencies (simplified validation)
        return currency.upper() in Money.VALID_CURRENCIES

    @classmethod
    def zero(cls, currency: str) -> "Money":
        """Factory method to create zero amount Money."""
        return cls(Decimal("0.00"), currency)

    @classmethod
    def from_cents(cls, cents: int, currency: str) -> "Money":
        """
        Factory method to create Money from cents/smallest currency unit.

        Args:
            cents: Amount in cents (e.g., 10050 for $100.50)
            currency: Currency code

        Returns:
            Money object
        """
        amount = Decimal(cents) / Decimal("100")
        return cls(amount, currency)

    def to_cents(self) -> int:
        """
        Convert Money to cents/smallest currency unit.

        Returns:
            Amount in cents as integer
        """
        return int(self.amount * 100)
