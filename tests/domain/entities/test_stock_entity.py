"""
Tests for Stock domain entity.

Following TDD approach - these tests define the expected behavior
of the rich Stock entity with business logic.
"""

import pytest
from decimal import Decimal
from domain.entities.stock_entity import StockEntity
from domain.value_objects.stock_symbol import StockSymbol
from domain.value_objects.money import Money
from domain.value_objects.quantity import Quantity


class TestStockEntity:
    """Test suite for Stock domain entity."""
    
    def test_create_stock_with_valid_data(self):
        """Should create Stock entity with valid data."""
        symbol = StockSymbol("AAPL")
        stock = StockEntity(
            symbol=symbol,
            name="Apple Inc.",
            industry_group="Technology",
            grade="A"
        )
        
        assert stock.symbol == symbol
        assert stock.name == "Apple Inc."
        assert stock.industry_group == "Technology"
        assert stock.grade == "A"
        assert stock.notes == ""
        assert stock.id is None  # Not yet persisted
    
    def test_create_stock_with_minimal_data(self):
        """Should create Stock with only required fields."""
        symbol = StockSymbol("MSFT")
        stock = StockEntity(symbol=symbol, name="Microsoft Corp.")
        
        assert stock.symbol == symbol
        assert stock.name == "Microsoft Corp."
        assert stock.industry_group is None
        assert stock.grade is None
        assert stock.notes == ""
    
    def test_create_stock_with_empty_name_raises_error(self):
        """Should raise error for empty company name."""
        symbol = StockSymbol("AAPL")
        
        with pytest.raises(ValueError, match="Company name cannot be empty"):
            StockEntity(symbol=symbol, name="")
        
        with pytest.raises(ValueError, match="Company name cannot be empty"):
            StockEntity(symbol=symbol, name="   ")
    
    def test_create_stock_with_invalid_grade_raises_error(self):
        """Should raise error for invalid grade."""
        symbol = StockSymbol("AAPL")
        
        with pytest.raises(ValueError, match="Grade must be one of"):
            StockEntity(symbol=symbol, name="Apple Inc.", grade="Z")
    
    def test_create_stock_with_too_long_name_raises_error(self):
        """Should raise error for company name that's too long."""
        symbol = StockSymbol("AAPL")
        long_name = "A" * 201  # Max is 200 characters
        
        with pytest.raises(ValueError, match="Company name cannot exceed 200 characters"):
            StockEntity(symbol=symbol, name=long_name)
    
    def test_create_stock_with_too_long_industry_raises_error(self):
        """Should raise error for industry group that's too long."""
        symbol = StockSymbol("AAPL")
        long_industry = "A" * 101  # Max is 100 characters
        
        with pytest.raises(ValueError, match="Industry group cannot exceed 100 characters"):
            StockEntity(symbol=symbol, name="Apple Inc.", industry_group=long_industry)
    
    def test_create_stock_with_too_long_notes_raises_error(self):
        """Should raise error for notes that are too long."""
        symbol = StockSymbol("AAPL")
        long_notes = "A" * 1001  # Max is 1000 characters
        
        with pytest.raises(ValueError, match="Notes cannot exceed 1000 characters"):
            StockEntity(symbol=symbol, name="Apple Inc.", notes=long_notes)
    
    def test_stock_equality(self):
        """Should compare stocks based on symbol (business key)."""
        symbol1 = StockSymbol("AAPL")
        symbol2 = StockSymbol("AAPL")
        symbol3 = StockSymbol("MSFT")
        
        stock1 = StockEntity(symbol=symbol1, name="Apple Inc.")
        stock2 = StockEntity(symbol=symbol2, name="Apple Inc.")  # Same symbol
        stock3 = StockEntity(symbol=symbol3, name="Microsoft")   # Different symbol
        
        assert stock1 == stock2  # Same symbol
        assert stock1 != stock3  # Different symbol
    
    def test_stock_hash(self):
        """Should be hashable based on symbol."""
        symbol1 = StockSymbol("AAPL")
        symbol2 = StockSymbol("AAPL")
        symbol3 = StockSymbol("MSFT")
        
        stock1 = StockEntity(symbol=symbol1, name="Apple Inc.")
        stock2 = StockEntity(symbol=symbol2, name="Apple Inc.")
        stock3 = StockEntity(symbol=symbol3, name="Microsoft")
        
        # Same symbol should have same hash
        assert hash(stock1) == hash(stock2)
        
        # Can be used in set
        stock_set = {stock1, stock2, stock3}
        assert len(stock_set) == 2  # AAPL appears only once
    
    def test_stock_string_representation(self):
        """Should have meaningful string representation."""
        symbol = StockSymbol("AAPL")
        stock = StockEntity(symbol=symbol, name="Apple Inc.")
        
        assert str(stock) == "AAPL - Apple Inc."
    
    def test_stock_repr(self):
        """Should have detailed repr representation."""
        symbol = StockSymbol("AAPL")
        stock = StockEntity(symbol=symbol, name="Apple Inc.", grade="A")
        
        expected = "StockEntity(symbol=StockSymbol('AAPL'), name='Apple Inc.', grade='A')"
        assert repr(stock) == expected
    
    def test_calculate_position_value(self):
        """Should calculate total position value."""
        symbol = StockSymbol("AAPL")
        stock = StockEntity(symbol=symbol, name="Apple Inc.")
        
        quantity = Quantity(100)
        price = Money("150.50", "USD")
        
        total_value = stock.calculate_position_value(quantity, price)
        
        assert total_value == Money("15050.00", "USD")
        assert isinstance(total_value, Money)
    
    def test_calculate_position_value_with_zero_quantity(self):
        """Should handle zero quantity gracefully."""
        symbol = StockSymbol("AAPL")
        stock = StockEntity(symbol=symbol, name="Apple Inc.")
        
        # Note: Quantity doesn't allow zero, so this tests error handling
        price = Money("150.50", "USD")
        
        with pytest.raises(ValueError):
            Quantity(0)  # This should fail in Quantity constructor
    
    def test_is_high_grade(self):
        """Should identify high grade stocks."""
        symbol = StockSymbol("AAPL")
        
        stock_a = StockEntity(symbol=symbol, name="Apple Inc.", grade="A")
        stock_b = StockEntity(symbol=symbol, name="Apple Inc.", grade="B")
        stock_c = StockEntity(symbol=symbol, name="Apple Inc.", grade="C")
        stock_no_grade = StockEntity(symbol=symbol, name="Apple Inc.")
        
        assert stock_a.is_high_grade() == True
        assert stock_b.is_high_grade() == False
        assert stock_c.is_high_grade() == False
        assert stock_no_grade.is_high_grade() == False
    
    def test_has_notes(self):
        """Should check if stock has notes."""
        symbol = StockSymbol("AAPL")
        
        stock_with_notes = StockEntity(symbol=symbol, name="Apple Inc.", notes="Great company")
        stock_without_notes = StockEntity(symbol=symbol, name="Apple Inc.")
        stock_empty_notes = StockEntity(symbol=symbol, name="Apple Inc.", notes="")
        
        assert stock_with_notes.has_notes() == True
        assert stock_without_notes.has_notes() == False
        assert stock_empty_notes.has_notes() == False
    
    def test_update_grade(self):
        """Should update stock grade with validation."""
        symbol = StockSymbol("AAPL")
        stock = StockEntity(symbol=symbol, name="Apple Inc.", grade="B")
        
        stock.update_grade("A")
        assert stock.grade == "A"
        
        stock.update_grade(None)
        assert stock.grade is None
    
    def test_update_grade_with_invalid_grade_raises_error(self):
        """Should raise error when updating to invalid grade."""
        symbol = StockSymbol("AAPL")
        stock = StockEntity(symbol=symbol, name="Apple Inc.")
        
        with pytest.raises(ValueError, match="Grade must be one of"):
            stock.update_grade("Z")
    
    def test_update_notes(self):
        """Should update stock notes with validation."""
        symbol = StockSymbol("AAPL")
        stock = StockEntity(symbol=symbol, name="Apple Inc.")
        
        stock.update_notes("Excellent company")
        assert stock.notes == "Excellent company"
        
        stock.update_notes("")
        assert stock.notes == ""
    
    def test_update_notes_with_too_long_notes_raises_error(self):
        """Should raise error when updating with notes that are too long."""
        symbol = StockSymbol("AAPL")
        stock = StockEntity(symbol=symbol, name="Apple Inc.")
        
        long_notes = "A" * 1001  # Max is 1000 characters
        
        with pytest.raises(ValueError, match="Notes cannot exceed 1000 characters"):
            stock.update_notes(long_notes)
    
    def test_set_id(self):
        """Should allow setting ID (for persistence layer)."""
        symbol = StockSymbol("AAPL")
        stock = StockEntity(symbol=symbol, name="Apple Inc.")
        
        assert stock.id is None
        
        stock.set_id(123)
        assert stock.id == 123
    
    def test_set_id_with_invalid_id_raises_error(self):
        """Should raise error for invalid ID."""
        symbol = StockSymbol("AAPL")
        stock = StockEntity(symbol=symbol, name="Apple Inc.")
        
        with pytest.raises(ValueError, match="ID must be a positive integer"):
            stock.set_id(0)
        
        with pytest.raises(ValueError, match="ID must be a positive integer"):
            stock.set_id(-1)
        
        with pytest.raises(ValueError, match="ID must be a positive integer"):
            stock.set_id("123")
    
    def test_set_id_when_already_set_raises_error(self):
        """Should raise error when trying to change existing ID."""
        symbol = StockSymbol("AAPL")
        stock = StockEntity(symbol=symbol, name="Apple Inc.")
        
        stock.set_id(123)
        
        with pytest.raises(ValueError, match="ID is already set and cannot be changed"):
            stock.set_id(456)