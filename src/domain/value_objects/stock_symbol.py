"""StockSymbol value object for representing stock ticker symbols.

Provides validation, normalization, and type safety for stock symbols
used throughout the trading application.
"""

import re
from typing import Any


class StockSymbol:
    """Immutable value object representing a stock ticker symbol.

    Enforces validation rules for stock symbols including:
    - Length constraints (1-5 characters)
    - Character validation (letters only)
    - Case normalization (uppercase)
    - Whitespace handling
    """

    # Validation pattern: 1-5 uppercase letters only
    MAX_SYMBOL_LENGTH = 5
    SYMBOL_PATTERN = re.compile(r"^[A-Z]{1,5}$")

    # Private attributes for type checking
    _value: str

    def __init__(self, symbol: str) -> None:
        """Initialize StockSymbol with validation and normalization.

        Args:
            symbol: Stock ticker symbol string

        Raises:
            ValueError: If symbol is invalid format
        """
        # Normalize the symbol
        normalized = self.normalize(symbol)

        # Validate the normalized symbol
        if not normalized:
            msg = "Stock symbol cannot be empty"
            raise ValueError(msg)
        if len(normalized) < 1 or len(normalized) > self.MAX_SYMBOL_LENGTH:
            raise ValueError(
                f"Stock symbol must be between 1 and {self.MAX_SYMBOL_LENGTH} "
                + "characters",
            )
        if not self.SYMBOL_PATTERN.match(normalized):
            msg = "Stock symbol must contain only uppercase letters"
            raise ValueError(msg)

        # Use object.__setattr__ to bypass immutability during initialization
        object.__setattr__(self, "_value", normalized)

    @property
    def value(self) -> str:
        """Get the stock symbol value."""
        return self._value

    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent modification after initialization (immutability)."""
        if hasattr(self, "_value"):  # Object is already initialized
            msg = "Cannot modify immutable StockSymbol object"
            raise AttributeError(msg)
        super().__setattr__(name, value)

    def __eq__(self, other: Any) -> bool:
        """Check equality with another StockSymbol object."""
        if not isinstance(other, StockSymbol):
            return False
        return self.value == other.value

    def __hash__(self) -> int:
        """Make StockSymbol hashable for use in sets/dicts."""
        return hash(self.value)

    def __str__(self) -> str:
        """String representation for display."""
        return self.value

    def __repr__(self) -> str:
        """Developer representation."""
        return f"StockSymbol({self.value!r})"

    @classmethod
    def normalize(cls, symbol: str) -> str:
        """Normalize symbol format.

        Args:
            symbol: Raw symbol string

        Returns:
            Normalized symbol (uppercase, stripped)
        """
        return symbol.strip().upper()

    @classmethod
    def is_valid(cls, symbol: str) -> bool:
        """Check if symbol is valid without creating instance.

        Args:
            symbol: Symbol string to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            normalized = cls.normalize(symbol)
            return cls._is_valid_format(normalized)
        except (ValueError, TypeError, AttributeError):
            return False

    @classmethod
    def _is_valid_format(cls, normalized_symbol: str) -> bool:
        """Check if normalized symbol matches required format.

        Args:
            normalized_symbol: Already normalized symbol

        Returns:
            True if format is valid
        """
        if not normalized_symbol:
            return False

        return cls.SYMBOL_PATTERN.match(normalized_symbol) is not None
