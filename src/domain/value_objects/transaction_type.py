"""
TransactionType value object for the StockBook domain.

Represents transaction types (buy/sell) with validation rules and immutability.
"""

from typing import Any


class TransactionType:
    """
    Value object representing a transaction type.

    Encapsulates validation logic for transaction types and ensures immutability.
    Only allows 'buy' and 'sell' transaction types.
    """

    VALID_TYPES = {"buy", "sell"}
    _value: str

    def __init__(self, value: str):
        """
        Initialize TransactionType with validation.

        Args:
            value: The transaction type string

        Raises:
            TypeError: If value is not a string
            ValueError: If transaction type is not 'buy' or 'sell'
        """
        # Type checking is handled by type annotations

        # Normalize to lowercase and strip whitespace
        normalized_value = value.strip().lower()

        if not normalized_value:
            raise ValueError("Transaction type cannot be empty")

        if normalized_value not in self.VALID_TYPES:
            raise ValueError("Transaction type must be 'buy' or 'sell'")

        # Store as private attribute to prevent mutation
        object.__setattr__(self, "_value", normalized_value)

    @property
    def value(self) -> str:
        """Get the transaction type value."""
        return self._value

    def is_buy(self) -> bool:
        """
        Check if this is a buy transaction.

        Returns:
            True if transaction type is 'buy', False otherwise
        """
        return self._value == "buy"

    def is_sell(self) -> bool:
        """
        Check if this is a sell transaction.

        Returns:
            True if transaction type is 'sell', False otherwise
        """
        return self._value == "sell"

    def __str__(self) -> str:
        """String representation of the transaction type."""
        return self._value

    def __repr__(self) -> str:
        """Developer representation of the transaction type."""
        return f"TransactionType({self._value!r})"

    def __eq__(self, other: Any) -> bool:
        """Check equality based on value."""
        if not isinstance(other, TransactionType):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """Hash based on value for use in collections."""
        return hash(self._value)

    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent mutation after initialization."""
        if hasattr(self, "_value"):
            raise AttributeError("TransactionType is immutable")
        super().__setattr__(name, value)
