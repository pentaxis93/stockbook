"""
StockSymbol value object for representing stock ticker symbols.

Provides validation, normalization, and type safety for stock symbols
used throughout the trading application.
"""

import re
from typing import Union


class StockSymbol:
    """
    Immutable value object representing a stock ticker symbol.
    
    Enforces validation rules for stock symbols including:
    - Length constraints (1-5 characters)
    - Character validation (letters only)
    - Case normalization (uppercase)
    - Whitespace handling
    """
    
    # Validation pattern: 1-5 uppercase letters only
    SYMBOL_PATTERN = re.compile(r'^[A-Z]{1,5}$')
    
    def __init__(self, symbol: str):
        """
        Initialize StockSymbol with validation and normalization.
        
        Args:
            symbol: Stock ticker symbol string
            
        Raises:
            ValueError: If symbol is invalid format
        """
        if not isinstance(symbol, str):
            raise ValueError("Stock symbol must be a string")
        
        # Normalize the symbol
        normalized = self.normalize(symbol)
        
        # Validate the normalized symbol
        if not normalized:
            raise ValueError("Stock symbol cannot be empty")
        elif len(normalized) < 1 or len(normalized) > 5:
            raise ValueError("Stock symbol must be between 1 and 5 characters")
        elif not self.SYMBOL_PATTERN.match(normalized):
            raise ValueError("Stock symbol must contain only uppercase letters")
        
        # Use object.__setattr__ to bypass immutability during initialization
        object.__setattr__(self, '_value', normalized)
    
    @property
    def value(self) -> str:
        """Get the stock symbol value."""
        return self._value
    
    def __setattr__(self, name, value):
        """Prevent modification after initialization (immutability)."""
        if hasattr(self, '_value'):  # Object is already initialized
            raise AttributeError(f"Cannot modify immutable StockSymbol object")
        super().__setattr__(name, value)
    
    def __eq__(self, other) -> bool:
        """Check equality with another StockSymbol object."""
        if not isinstance(other, StockSymbol):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        """Make StockSymbol hashable for use in sets/dicts."""
        return hash(self.value)
    
    def __lt__(self, other) -> bool:
        """Less than comparison for ordering."""
        if not isinstance(other, StockSymbol):
            raise TypeError("Cannot compare StockSymbol with non-StockSymbol")
        return self.value < other.value
    
    def __le__(self, other) -> bool:
        """Less than or equal comparison."""
        if not isinstance(other, StockSymbol):
            raise TypeError("Cannot compare StockSymbol with non-StockSymbol")
        return self.value <= other.value
    
    def __gt__(self, other) -> bool:
        """Greater than comparison."""
        if not isinstance(other, StockSymbol):
            raise TypeError("Cannot compare StockSymbol with non-StockSymbol")
        return self.value > other.value
    
    def __ge__(self, other) -> bool:
        """Greater than or equal comparison."""
        if not isinstance(other, StockSymbol):
            raise TypeError("Cannot compare StockSymbol with non-StockSymbol")
        return self.value >= other.value
    
    def __str__(self) -> str:
        """String representation for display."""
        return self.value
    
    def __repr__(self) -> str:
        """Developer representation."""
        return f"StockSymbol('{self.value}')"
    
    @classmethod
    def normalize(cls, symbol: str) -> str:
        """
        Normalize symbol format.
        
        Args:
            symbol: Raw symbol string
            
        Returns:
            Normalized symbol (uppercase, stripped)
        """
        if not isinstance(symbol, str):
            return ""
        
        return symbol.strip().upper()
    
    @classmethod
    def is_valid(cls, symbol: str) -> bool:
        """
        Check if symbol is valid without creating instance.
        
        Args:
            symbol: Symbol string to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            normalized = cls.normalize(symbol)
            return cls._is_valid_format(normalized)
        except (ValueError, TypeError):
            return False
    
    @classmethod
    def _is_valid_format(cls, normalized_symbol: str) -> bool:
        """
        Check if normalized symbol matches required format.
        
        Args:
            normalized_symbol: Already normalized symbol
            
        Returns:
            True if format is valid
        """
        if not normalized_symbol:
            return False
        
        return cls.SYMBOL_PATTERN.match(normalized_symbol) is not None
    
    @classmethod
    def from_string(cls, symbol: str) -> 'StockSymbol':
        """
        Factory method for explicit string conversion.
        
        Args:
            symbol: Symbol string
            
        Returns:
            StockSymbol instance
        """
        return cls(symbol)