"""
Tests for StockSymbol value object.

Following TDD approach - these tests define the expected behavior
before implementation.
"""

import pytest

from src.domain.value_objects.stock_symbol import StockSymbol


class TestStockSymbol:
    """Test suite for StockSymbol value object."""

    def test_create_stock_symbol_with_valid_symbol(self) -> None:
        """Should create StockSymbol with valid symbol."""
        symbol = StockSymbol("AAPL")
        assert symbol.value == "AAPL"

    def test_create_stock_symbol_converts_to_uppercase(self) -> None:
        """Should convert lowercase symbols to uppercase."""
        symbol = StockSymbol("aapl")
        assert symbol.value == "AAPL"

    def test_create_stock_symbol_strips_whitespace(self) -> None:
        """Should strip leading/trailing whitespace."""
        symbol = StockSymbol("  AAPL  ")
        assert symbol.value == "AAPL"

    def test_create_stock_symbol_with_empty_string_raises_error(self) -> None:
        """Should raise error for empty symbol."""
        with pytest.raises(ValueError, match="Stock symbol cannot be empty"):
            _ = StockSymbol("")

    def test_create_stock_symbol_with_whitespace_only_raises_error(self) -> None:
        """Should raise error for whitespace-only symbol."""
        with pytest.raises(ValueError, match="Stock symbol cannot be empty"):
            _ = StockSymbol("   ")

    def test_create_stock_symbol_with_invalid_characters_raises_error(self) -> None:
        """Should raise error for symbols with invalid characters."""
        with pytest.raises(
            ValueError, match="Stock symbol must be between 1 and 5 characters"
        ):
            _ = StockSymbol("AAPL123")  # Too long takes precedence

        with pytest.raises(
            ValueError, match="Stock symbol must contain only uppercase letters"
        ):
            _ = StockSymbol("AA-PL")

        with pytest.raises(
            ValueError, match="Stock symbol must contain only uppercase letters"
        ):
            _ = StockSymbol("AA.PL")

    def test_create_stock_symbol_with_too_short_symbol_raises_error(self) -> None:
        """Should raise error for symbols that are too short."""
        with pytest.raises(ValueError, match="Stock symbol cannot be empty"):
            _ = StockSymbol("")

    def test_create_stock_symbol_with_too_long_symbol_raises_error(self) -> None:
        """Should raise error for symbols that are too long."""
        with pytest.raises(
            ValueError, match="Stock symbol must be between 1 and 5 characters"
        ):
            _ = StockSymbol("TOOLONG")

    def test_create_stock_symbol_accepts_valid_lengths(self) -> None:
        """Should accept symbols of valid lengths (1-5 characters)."""
        _ = StockSymbol("A")  # 1 character
        _ = StockSymbol("AB")  # 2 characters
        _ = StockSymbol("ABC")  # 3 characters
        _ = StockSymbol("AAPL")  # 4 characters
        _ = StockSymbol("GOOGL")  # 5 characters

    def test_stock_symbol_equality(self) -> None:
        """Should compare StockSymbol objects for equality."""
        symbol1 = StockSymbol("AAPL")
        symbol2 = StockSymbol("aapl")  # Should be equal after normalization
        symbol3 = StockSymbol("MSFT")

        assert symbol1 == symbol2
        assert symbol1 != symbol3

    def test_stock_symbol_equality_with_non_stock_symbol(self) -> None:
        """Should not be equal to non-StockSymbol objects."""
        symbol = StockSymbol("AAPL")
        assert symbol != "AAPL"
        assert symbol != 123
        assert symbol != None
        assert symbol != {"value": "AAPL"}

    def test_stock_symbol_hash(self) -> None:
        """Should be hashable for use in sets/dicts."""
        symbol1 = StockSymbol("AAPL")
        symbol2 = StockSymbol("aapl")
        symbol3 = StockSymbol("MSFT")

        # Same symbols should have same hash
        assert hash(symbol1) == hash(symbol2)

        # Can be used in set
        symbol_set = {symbol1, symbol2, symbol3}
        assert len(symbol_set) == 2  # AAPL appears only once

    def test_stock_symbol_string_representation(self) -> None:
        """Should have proper string representation."""
        symbol = StockSymbol("AAPL")
        assert str(symbol) == "AAPL"

    def test_stock_symbol_repr(self) -> None:
        """Should have proper repr representation."""
        symbol = StockSymbol("AAPL")
        assert repr(symbol) == "StockSymbol('AAPL')"

    def test_stock_symbol_is_immutable(self) -> None:
        """StockSymbol should be immutable."""
        symbol = StockSymbol("AAPL")

        # Attempting to modify should raise AttributeError
        with pytest.raises(AttributeError):
            symbol.value = "MSFT"  # type: ignore[misc] - Testing immutability

    def test_stock_symbol_sorting_with_key_function(self) -> None:
        """Should support sorting using key function (recommended approach)."""
        symbols = [StockSymbol("MSFT"), StockSymbol("AAPL"), StockSymbol("GOOGL")]

        # Sort by symbol value using key parameter
        sorted_symbols = sorted(symbols, key=lambda s: s.value)
        expected_order = ["AAPL", "GOOGL", "MSFT"]

        assert [s.value for s in sorted_symbols] == expected_order

    def test_stock_symbol_is_valid_class_method(self) -> None:
        """Should provide class method to validate symbols without creating instance."""
        assert StockSymbol.is_valid("AAPL") is True
        assert StockSymbol.is_valid("aapl") is True  # Case insensitive
        assert StockSymbol.is_valid("AAPL123") is False
        assert StockSymbol.is_valid("") is False
        assert StockSymbol.is_valid("TOOLONG") is False

        # Test error handling in is_valid method - this will cause TypeError/ValueError
        assert (
            StockSymbol.is_valid("AA-PL") is False
        )  # Special characters cause validation error

    def test_stock_symbol_base_class_coverage(self) -> None:
        """Test base class coverage for StockSymbol missing lines."""
        # Test that normal initialization works (covers __setattr__ during init)
        symbol = StockSymbol("AAPL")
        assert symbol.value == "AAPL"

    def test_stock_symbol_setattr_during_initialization(self) -> None:
        """Test that __setattr__ allows setting attributes during initialization."""
        # Create a partially initialized object
        symbol = object.__new__(StockSymbol)

        # This exercises the super().__setattr__ branch (line 62)
        setattr(symbol, "test_attr", "test_value")

        # Now properly initialize the object
        StockSymbol.__init__(symbol, "AAPL")
        assert symbol.value == "AAPL"

    def test_stock_symbol_is_valid_with_type_error(self) -> None:
        """Test is_valid returns False when normalize raises TypeError."""
        # Pass None which will cause TypeError in normalize
        assert StockSymbol.is_valid(None) is False  # type: ignore[arg-type]

    def test_stock_symbol_is_valid_with_non_string_types(self) -> None:
        """Test is_valid returns False for various non-string types."""
        # These should all cause TypeError in normalize and return False
        assert StockSymbol.is_valid(123) is False  # type: ignore[arg-type]
        assert StockSymbol.is_valid([]) is False  # type: ignore[arg-type]
        assert StockSymbol.is_valid({}) is False  # type: ignore[arg-type]
        assert StockSymbol.is_valid(object()) is False  # type: ignore[arg-type]

        # Test exception handling in is_valid with invalid symbols (covers lines 109-110)
        # This will trigger ValueError that gets caught and returns False
        assert StockSymbol.is_valid("") is False  # Empty string causes validation error

    def test_stock_symbol_normalize_class_method(self) -> None:
        """Should provide class method to normalize symbol format."""
        assert StockSymbol.normalize("aapl") == "AAPL"
        assert StockSymbol.normalize("  MSFT  ") == "MSFT"
        assert StockSymbol.normalize("GOOGL") == "GOOGL"

    def test_stock_symbol_common_symbols_validation(self) -> None:
        """Should accept common stock symbols."""
        common_symbols = [
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "TSLA",
            "META",
            "NVDA",
            "BRK",
            "JNJ",
            "V",
        ]

        for symbol_str in common_symbols:
            symbol = StockSymbol(symbol_str)
            assert symbol.value == symbol_str
