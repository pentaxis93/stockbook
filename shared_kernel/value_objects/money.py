"""
Money value object for the shared kernel.

Provides a robust, immutable money representation that handles currency,
arithmetic operations, and business rules consistently across all domains.
"""

import decimal
import re
from decimal import ROUND_HALF_UP, Decimal
from typing import List, Optional, Union


class Money:
    """
    Immutable value object representing monetary amounts with currency.

    Handles arithmetic operations, comparisons, and business rules for money
    in a way that's safe and consistent across all bounded contexts.
    """

    # Valid currency codes for trading (can be extended)
    VALID_CURRENCIES = {"USD", "CAD", "EUR", "GBP", "JPY"}

    def __init__(self, amount: Union[int, float, str, Decimal], currency: str):
        """
        Initialize Money with amount and currency.

        Args:
            amount: Monetary amount (converted to Decimal for precision)
            currency: 3-letter currency code (e.g., 'USD', 'EUR')

        Raises:
            TypeError: If amount cannot be converted to Decimal
            ValueError: If currency is invalid
        """
        try:
            self._amount = Decimal(str(amount))
        except (ValueError, TypeError, decimal.InvalidOperation) as e:
            raise TypeError(
                f"Amount must be numeric, got {type(amount).__name__}"
            ) from e

        if not isinstance(currency, str):
            raise TypeError("Currency must be a string")

        if not currency or not currency.strip():
            raise ValueError("Currency code cannot be empty")

        # Normalize currency to uppercase
        self._currency = currency.strip().upper()

        # Validate currency code format (3 letters)
        if not re.match(r"^[A-Z]{3}$", self._currency):
            raise ValueError("Currency code must be 3 letters")

        # Validate against known currencies for trading context
        if self._currency not in self.VALID_CURRENCIES:
            raise ValueError(f"Currency must be one of {sorted(self.VALID_CURRENCIES)}")

        # Round to currency precision (2 decimal places)
        self._amount = self._amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def amount(self) -> Decimal:
        """Get the monetary amount."""
        return self._amount

    @property
    def currency(self) -> str:
        """Get the currency code."""
        return self._currency

    def __str__(self) -> str:
        """String representation for display."""
        # Format with 2 decimal places for currency display
        formatted_amount = self._amount.quantize(Decimal("0.01"))
        return f"{formatted_amount} {self._currency}"

    def __repr__(self) -> str:
        """Developer representation."""
        # Format with 2 decimal places for consistency
        formatted_amount = self._amount.quantize(Decimal("0.01"))
        return f"Money({formatted_amount}, '{self._currency}')"

    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, Money):
            return False
        return self._amount == other._amount and self._currency == other._currency

    def __hash__(self) -> int:
        """Hash for use in sets and as dict keys."""
        return hash((self._amount, self._currency))

    def __lt__(self, other) -> bool:
        """Less than comparison."""
        self._validate_same_currency(other, "compare")
        return self._amount < other._amount

    def __le__(self, other) -> bool:
        """Less than or equal comparison."""
        self._validate_same_currency(other, "compare")
        return self._amount <= other._amount

    def __gt__(self, other) -> bool:
        """Greater than comparison."""
        self._validate_same_currency(other, "compare")
        return self._amount > other._amount

    def __ge__(self, other) -> bool:
        """Greater than or equal comparison."""
        self._validate_same_currency(other, "compare")
        return self._amount >= other._amount

    def __add__(self, other) -> "Money":
        """Add two Money instances."""
        if not isinstance(other, Money):
            raise TypeError("Can only add Money to Money")
        self._validate_same_currency(other, "add")
        return Money(self._amount + other._amount, self._currency)

    def __sub__(self, other) -> "Money":
        """Subtract two Money instances."""
        if not isinstance(other, Money):
            raise TypeError("Can only subtract Money from Money")
        self._validate_same_currency(other, "subtract")
        return Money(self._amount - other._amount, self._currency)

    def __mul__(self, scalar: Union[int, float, Decimal]) -> "Money":
        """Multiply Money by a scalar."""
        if isinstance(scalar, (int, float, Decimal)):
            return Money(self._amount * Decimal(str(scalar)), self._currency)
        raise TypeError("Can only multiply Money by numeric types")

    def __rmul__(self, scalar: Union[int, float, Decimal]) -> "Money":
        """Right multiplication (scalar * Money)."""
        return self.__mul__(scalar)

    def __truediv__(self, scalar: Union[int, float, Decimal]) -> "Money":
        """Divide Money by a scalar."""
        if isinstance(scalar, (int, float, Decimal)):
            if scalar == 0:
                raise ZeroDivisionError("Cannot divide by zero")
            return Money(self._amount / Decimal(str(scalar)), self._currency)
        raise TypeError("Can only divide Money by numeric types")

    def __neg__(self) -> "Money":
        """Negate Money amount."""
        return Money(-self._amount, self._currency)

    def __abs__(self) -> "Money":
        """Absolute value of Money."""
        return Money(abs(self._amount), self._currency)

    def is_zero(self) -> bool:
        """Check if amount is zero."""
        return self._amount == Decimal("0")

    def is_positive(self) -> bool:
        """Check if amount is positive."""
        return self._amount > Decimal("0")

    def is_negative(self) -> bool:
        """Check if amount is negative."""
        return self._amount < Decimal("0")

    def round_to_currency_precision(self, decimal_places: int = 2) -> "Money":
        """Round to typical currency precision."""
        rounded_amount = self._amount.quantize(
            (
                Decimal("0.01")
                if decimal_places == 2
                else Decimal(f'0.{"0" * decimal_places}1')
            ),
            rounding=ROUND_HALF_UP,
        )
        return Money(rounded_amount, self._currency)

    def convert_to(self, new_currency: str, exchange_rate: Decimal) -> "Money":
        """Convert to another currency using exchange rate."""
        converted_amount = self._amount * exchange_rate
        return Money(converted_amount, new_currency)

    def allocate(self, ratios: List[Union[int, float, Decimal]]) -> List["Money"]:
        """
        Allocate money into portions based on ratios.

        Handles rounding to ensure sum equals original amount.
        """
        if not ratios:
            return []

        # Convert to decimals and calculate total
        decimal_ratios = [Decimal(str(ratio)) for ratio in ratios]
        total_ratio = sum(decimal_ratios)

        if total_ratio == 0:
            return [Money.zero(self._currency) for _ in ratios]

        # Calculate proportional amounts
        portions = []
        remaining = self._amount

        for ratio in decimal_ratios[:-1]:  # All but last
            portion_amount = (self._amount * ratio / total_ratio).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            portions.append(Money(portion_amount, self._currency))
            remaining -= portion_amount

        # Last portion gets the remainder to ensure exact total
        portions.append(Money(remaining, self._currency))

        return portions

    def percentage(self, percent: Union[int, float, Decimal]) -> "Money":
        """Calculate percentage of this money amount."""
        percent_decimal = Decimal(str(percent)) / Decimal("100")
        return Money(self._amount * percent_decimal, self._currency)

    def _validate_same_currency(self, other: "Money", operation: str) -> None:
        """Validate that two Money instances have the same currency."""
        if self._currency != other._currency:
            raise ValueError(
                f"Cannot {operation} money with different currencies: "
                f"{self._currency} and {other._currency}"
            )

    @classmethod
    def zero(cls, currency: str) -> "Money":
        """Create zero money with specified currency."""
        return cls(Decimal("0"), currency)

    @classmethod
    def from_cents(cls, cents: int, currency: str) -> "Money":
        """Create money from cents (smallest currency unit)."""
        amount = Decimal(cents) / Decimal("100")
        return cls(amount, currency)

    def to_cents(self) -> int:
        """
        Convert Money to cents/smallest currency unit.

        Returns:
            Amount in cents as integer
        """
        return int(self._amount * 100)

    @classmethod
    def from_string(cls, money_str: str) -> "Money":
        """Parse money from formatted string like '$125.50' or '€99.99'."""
        # Currency symbol mappings
        currency_symbols = {"$": "USD", "€": "EUR", "£": "GBP", "¥": "JPY", "C$": "CAD"}

        money_str = money_str.strip()

        # Find currency symbol
        currency = "USD"  # Default
        amount_str = money_str

        for symbol, curr in currency_symbols.items():
            if money_str.startswith(symbol):
                currency = curr
                amount_str = money_str[len(symbol) :]
                break

        # Parse amount
        try:
            amount = Decimal(amount_str)
            return cls(amount, currency)
        except ValueError as e:
            raise ValueError(f"Cannot parse money from '{money_str}'") from e

    @classmethod
    def sum(cls, money_list: List["Money"], currency: Optional[str] = None) -> "Money":
        """Sum a list of Money instances."""
        if not money_list:
            if currency is None:
                raise ValueError("Cannot sum empty list without specifying currency")
            return cls.zero(currency)

        # Validate all have same currency
        first_currency = money_list[0].currency
        for money in money_list:
            if money.currency != first_currency:
                raise ValueError("All money amounts must have the same currency")

        total_amount = sum(money.amount for money in money_list)
        return cls(total_amount, first_currency)
