"""
Tests for StockSymbol value object.

Following TDD approach - these tests define the expected behavior
before implementation.
"""

import pytest
from domain.value_objects.stock_symbol import StockSymbol


class TestStockSymbol:
    """Test suite for StockSymbol value object."""
    
    def test_create_stock_symbol_with_valid_symbol(self):
        """Should create StockSymbol with valid symbol."""
        symbol = StockSymbol("AAPL")
        assert symbol.value == "AAPL"
    
    def test_create_stock_symbol_converts_to_uppercase(self):
        """Should convert lowercase symbols to uppercase."""
        symbol = StockSymbol("aapl")
        assert symbol.value == "AAPL"
    
    def test_create_stock_symbol_strips_whitespace(self):
        """Should strip leading/trailing whitespace."""
        symbol = StockSymbol("  AAPL  ")
        assert symbol.value == "AAPL"
    
    def test_create_stock_symbol_with_empty_string_raises_error(self):
        """Should raise error for empty symbol."""
        with pytest.raises(ValueError, match="Stock symbol cannot be empty"):
            StockSymbol("")
    
    def test_create_stock_symbol_with_whitespace_only_raises_error(self):
        """Should raise error for whitespace-only symbol."""
        with pytest.raises(ValueError, match="Stock symbol cannot be empty"):
            StockSymbol("   ")
    
    def test_create_stock_symbol_with_invalid_characters_raises_error(self):
        """Should raise error for symbols with invalid characters."""
        with pytest.raises(ValueError, match="Stock symbol must be between 1 and 5 characters"):
            StockSymbol("AAPL123")  # Too long takes precedence
        
        with pytest.raises(ValueError, match="Stock symbol must contain only uppercase letters"):
            StockSymbol("AA-PL")
        
        with pytest.raises(ValueError, match="Stock symbol must contain only uppercase letters"):
            StockSymbol("AA.PL")
    
    def test_create_stock_symbol_with_too_short_symbol_raises_error(self):
        """Should raise error for symbols that are too short."""
        with pytest.raises(ValueError, match="Stock symbol cannot be empty"):
            StockSymbol("")
    
    def test_create_stock_symbol_with_too_long_symbol_raises_error(self):
        """Should raise error for symbols that are too long."""
        with pytest.raises(ValueError, match="Stock symbol must be between 1 and 5 characters"):
            StockSymbol("TOOLONG")
    
    def test_create_stock_symbol_accepts_valid_lengths(self):
        """Should accept symbols of valid lengths (1-5 characters)."""
        StockSymbol("A")      # 1 character
        StockSymbol("AB")     # 2 characters
        StockSymbol("ABC")    # 3 characters
        StockSymbol("AAPL")   # 4 characters
        StockSymbol("GOOGL")  # 5 characters
    
    def test_stock_symbol_equality(self):
        """Should compare StockSymbol objects for equality."""
        symbol1 = StockSymbol("AAPL")
        symbol2 = StockSymbol("aapl")  # Should be equal after normalization
        symbol3 = StockSymbol("MSFT")
        
        assert symbol1 == symbol2
        assert symbol1 != symbol3
    
    def test_stock_symbol_equality_with_non_stock_symbol(self):
        """Should not be equal to non-StockSymbol objects."""
        symbol = StockSymbol("AAPL")
        assert symbol != "AAPL"
        assert symbol != 123
        assert symbol != None
    
    def test_stock_symbol_hash(self):
        """Should be hashable for use in sets/dicts."""
        symbol1 = StockSymbol("AAPL")
        symbol2 = StockSymbol("aapl")
        symbol3 = StockSymbol("MSFT")
        
        # Same symbols should have same hash
        assert hash(symbol1) == hash(symbol2)
        
        # Can be used in set
        symbol_set = {symbol1, symbol2, symbol3}
        assert len(symbol_set) == 2  # AAPL appears only once
    
    def test_stock_symbol_string_representation(self):
        """Should have proper string representation."""
        symbol = StockSymbol("AAPL")
        assert str(symbol) == "AAPL"
    
    def test_stock_symbol_repr(self):
        """Should have proper repr representation."""
        symbol = StockSymbol("AAPL")
        assert repr(symbol) == "StockSymbol('AAPL')"
    
    def test_stock_symbol_is_immutable(self):
        """StockSymbol should be immutable."""
        symbol = StockSymbol("AAPL")
        
        # Attempting to modify should raise AttributeError
        with pytest.raises(AttributeError):
            symbol.value = "MSFT"
    
    def test_stock_symbol_ordering(self):
        """Should support lexicographic ordering."""
        aapl = StockSymbol("AAPL")
        msft = StockSymbol("MSFT")
        googl = StockSymbol("GOOGL")
        
        assert aapl < googl < msft
        assert msft > googl > aapl
        assert aapl <= aapl
        assert msft >= msft
    
    def test_stock_symbol_ordering_with_non_stock_symbol_raises_error(self):
        """Should raise error when comparing with non-StockSymbol objects."""
        symbol = StockSymbol("AAPL")
        
        with pytest.raises(TypeError):
            symbol < "MSFT"
        
        with pytest.raises(TypeError):
            symbol > 123
    
    def test_stock_symbol_is_valid_class_method(self):
        """Should provide class method to validate symbols without creating instance."""
        assert StockSymbol.is_valid("AAPL") == True
        assert StockSymbol.is_valid("aapl") == True  # Case insensitive
        assert StockSymbol.is_valid("AAPL123") == False
        assert StockSymbol.is_valid("") == False
        assert StockSymbol.is_valid("TOOLONG") == False
    
    def test_stock_symbol_normalize_class_method(self):
        """Should provide class method to normalize symbol format."""
        assert StockSymbol.normalize("aapl") == "AAPL"
        assert StockSymbol.normalize("  MSFT  ") == "MSFT"
        assert StockSymbol.normalize("GOOGL") == "GOOGL"
    
    def test_stock_symbol_from_string_factory_method(self):
        """Should provide factory method for explicit string conversion."""
        symbol = StockSymbol.from_string("aapl")
        assert symbol.value == "AAPL"
        assert isinstance(symbol, StockSymbol)
    
    def test_stock_symbol_common_symbols_validation(self):
        """Should accept common stock symbols."""
        common_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "BRK", "JNJ", "V"]
        
        for symbol_str in common_symbols:
            symbol = StockSymbol(symbol_str)
            assert symbol.value == symbol_str