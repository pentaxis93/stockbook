"""
Tests for Stock domain entity.

Following TDD approach - these tests define the expected behavior
of the rich Stock entity with business logic.
"""

from decimal import Decimal

import pytest

from domain.entities.stock_entity import StockEntity
from domain.value_objects import CompanyName, IndustryGroup, Notes
from domain.value_objects.sector import Sector
from domain.value_objects.stock_symbol import StockSymbol
from shared_kernel.value_objects import Money, Quantity


class TestStockEntity:
    """Test suite for Stock domain entity."""

    def test_create_stock_with_valid_data(self):
        """Should create Stock entity with valid data."""
        symbol = StockSymbol("AAPL")
        stock = StockEntity(
            symbol=symbol,
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
        )

        assert stock.symbol == symbol
        assert stock.name == "Apple Inc."
        assert stock.sector == "Technology"
        assert stock.industry_group == "Software"
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

    def test_stock_returns_value_objects(self):
        """Should return value objects for name, industry_group, and notes."""
        symbol = StockSymbol("AAPL")
        stock = StockEntity(
            symbol=symbol,
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            notes="Great company",
        )

        # Should return value objects, not raw strings
        assert isinstance(stock.company_name, CompanyName)
        assert isinstance(stock.sector_vo, Sector)
        assert isinstance(stock.industry_group_vo, IndustryGroup)
        assert isinstance(stock.notes_vo, Notes)

        # Should also provide string properties for backward compatibility
        assert stock.name == "Apple Inc."
        assert stock.sector == "Technology"
        assert stock.industry_group == "Software"
        assert stock.notes == "Great company"

    def test_create_stock_with_empty_name_allowed(self):
        """Should allow creating stock with empty company name (only symbol required)."""
        symbol = StockSymbol("AAPL")

        stock_empty_name = StockEntity(symbol=symbol, name="")
        assert stock_empty_name.symbol == symbol
        assert stock_empty_name.name == ""

        stock_whitespace_name = StockEntity(symbol=symbol, name="   ")
        assert stock_whitespace_name.symbol == symbol
        assert (
            stock_whitespace_name.name == ""
        )  # Whitespace is stripped during initialization

    def test_create_stock_with_only_symbol(self):
        """Should allow creating stock with only symbol (name defaults to empty)."""
        symbol = StockSymbol("AAPL")

        stock = StockEntity(symbol=symbol)
        assert stock.symbol == symbol
        assert stock.name == ""
        assert stock.industry_group is None
        assert stock.grade is None
        assert stock.notes == ""

    def test_create_stock_with_invalid_grade_raises_error(self):
        """Should raise error for invalid grade."""
        symbol = StockSymbol("AAPL")

        with pytest.raises(ValueError, match="Grade must be one of"):
            StockEntity(symbol=symbol, name="Apple Inc.", grade="Z")

    def test_create_stock_with_too_long_name_raises_error(self):
        """Should raise error for company name that's too long (delegated to value object)."""
        symbol = StockSymbol("AAPL")
        long_name = "A" * 201  # Max is 200 characters

        with pytest.raises(
            ValueError, match="Company name cannot exceed 200 characters"
        ):
            StockEntity(symbol=symbol, name=long_name)

    def test_create_stock_with_too_long_industry_raises_error(self):
        """Should raise error for industry group that's too long (delegated to value object)."""
        symbol = StockSymbol("AAPL")
        long_industry = "A" * 101  # Max is 100 characters

        with pytest.raises(
            ValueError, match="Industry group cannot exceed 100 characters"
        ):
            StockEntity(
                symbol=symbol,
                name="Apple Inc.",
                sector="Technology",
                industry_group=long_industry,
            )

    def test_create_stock_with_too_long_notes_raises_error(self):
        """Should raise error for notes that are too long (delegated to value object)."""
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
        stock3 = StockEntity(symbol=symbol3, name="Microsoft")  # Different symbol

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

        expected = (
            "StockEntity(symbol=StockSymbol('AAPL'), name='Apple Inc.', grade='A')"
        )
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
        # Note: For stock shares, use for_shares factory which enforces positive quantities

        with pytest.raises(ValueError):
            Quantity.for_shares(0)  # This should fail for share quantities

    def test_has_notes(self):
        """Should check if stock has notes."""
        symbol = StockSymbol("AAPL")

        stock_with_notes = StockEntity(
            symbol=symbol, name="Apple Inc.", notes="Great company"
        )
        stock_without_notes = StockEntity(symbol=symbol, name="Apple Inc.")
        stock_empty_notes = StockEntity(symbol=symbol, name="Apple Inc.", notes="")

        assert stock_with_notes.has_notes() is True
        assert stock_without_notes.has_notes() is False
        assert stock_empty_notes.has_notes() is False

    def test_update_fields_single_field(self):
        """Should update individual fields using update_fields method."""
        symbol = StockSymbol("AAPL")
        stock = StockEntity(symbol=symbol, name="Apple Inc.", grade="B")

        # Update grade
        stock.update_fields(grade="A")
        assert stock.grade == "A"

        # Update name
        stock.update_fields(name="Apple Inc. Updated")
        assert stock.name == "Apple Inc. Updated"

        # Update sector and industry_group
        stock.update_fields(sector="Technology", industry_group="Software")
        assert stock.sector == "Technology"
        assert stock.industry_group == "Software"

        # Update notes
        stock.update_fields(notes="Great company")
        assert stock.notes == "Great company"

    def test_update_fields_multiple_fields_atomic(self):
        """Should update multiple fields atomically."""
        symbol = StockSymbol("AAPL")
        stock = StockEntity(symbol=symbol, name="Apple Inc.")

        # Update multiple fields at once
        stock.update_fields(
            name="Apple Inc. Updated",
            grade="A",
            sector="Technology",
            industry_group="Software",
            notes="Excellent company",
        )

        assert stock.name == "Apple Inc. Updated"
        assert stock.grade == "A"
        assert stock.sector == "Technology"
        assert stock.industry_group == "Software"
        assert stock.notes == "Excellent company"

    def test_update_fields_validation_failure_rollback(self):
        """Should rollback all changes if any validation fails."""
        symbol = StockSymbol("AAPL")
        stock = StockEntity(symbol=symbol, name="Apple Inc.", grade="B")

        # Try to update with invalid grade - should fail and rollback all
        with pytest.raises(ValueError, match="Grade must be one of"):
            stock.update_fields(
                name="Apple Inc. Updated", grade="Z", notes="New notes"  # Invalid grade
            )

        # Original values should be unchanged
        assert stock.name == "Apple Inc."
        assert stock.grade == "B"
        assert stock.notes == ""

    def test_update_fields_with_too_long_values_raises_error(self):
        """Should raise error for values that are too long."""
        symbol = StockSymbol("AAPL")
        stock = StockEntity(symbol=symbol, name="Apple Inc.")

        # Test name too long
        long_name = "A" * 201
        with pytest.raises(
            ValueError, match="Company name cannot exceed 200 characters"
        ):
            stock.update_fields(name=long_name)

        # Test industry too long
        long_industry = "A" * 101
        with pytest.raises(
            ValueError, match="Industry group cannot exceed 100 characters"
        ):
            stock.update_fields(sector="Technology", industry_group=long_industry)

        # Test notes too long
        long_notes = "A" * 1001
        with pytest.raises(ValueError, match="Notes cannot exceed 1000 characters"):
            stock.update_fields(notes=long_notes)

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

    # New tests for sector functionality
    def test_create_stock_with_sector_and_industry_group(self):
        """Should create Stock entity with sector and industry_group."""
        symbol = StockSymbol("AAPL")
        stock = StockEntity(
            symbol=symbol,
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
        )

        assert stock.symbol == symbol
        assert stock.name == "Apple Inc."
        assert stock.sector == "Technology"
        assert stock.industry_group == "Software"
        assert stock.grade == "A"
        assert isinstance(stock.sector_vo, Sector)
        assert isinstance(stock.industry_group_vo, IndustryGroup)

    def test_create_stock_with_sector_only(self):
        """Should create Stock with sector but no industry_group."""
        symbol = StockSymbol("MSFT")
        stock = StockEntity(symbol=symbol, name="Microsoft Corp.", sector="Technology")

        assert stock.symbol == symbol
        assert stock.name == "Microsoft Corp."
        assert stock.sector == "Technology"
        assert stock.industry_group is None
        assert isinstance(stock.sector_vo, Sector)
        assert stock.industry_group_vo is None

    def test_create_stock_with_invalid_sector_industry_combination_raises_error(self):
        """Should raise error when industry_group doesn't belong to sector."""
        symbol = StockSymbol("AAPL")

        with pytest.raises(
            ValueError,
            match="Industry group 'Pharmaceuticals' is not valid for sector 'Technology'",
        ):
            StockEntity(
                symbol=symbol,
                name="Apple Inc.",
                sector="Technology",
                industry_group="Pharmaceuticals",  # Invalid for Technology sector
            )

    def test_create_stock_with_industry_group_but_no_sector_raises_error(self):
        """Should raise error when industry_group is provided without sector."""
        symbol = StockSymbol("AAPL")

        with pytest.raises(
            ValueError, match="Sector must be provided when industry_group is specified"
        ):
            StockEntity(
                symbol=symbol,
                name="Apple Inc.",
                industry_group="Software",  # No sector provided
            )

    def test_create_stock_with_empty_sector_raises_error(self):
        """Should raise error for empty sector string."""
        symbol = StockSymbol("AAPL")

        with pytest.raises(ValueError, match="Sector cannot be empty"):
            StockEntity(symbol=symbol, name="Apple Inc.", sector="")

    def test_create_stock_with_too_long_sector_raises_error(self):
        """Should raise error for sector that's too long."""
        symbol = StockSymbol("AAPL")
        long_sector = "A" * 101  # Max is 100 characters

        with pytest.raises(ValueError, match="Sector cannot exceed 100 characters"):
            StockEntity(symbol=symbol, name="Apple Inc.", sector=long_sector)

    def test_update_fields_sector_only(self):
        """Should update sector without industry_group."""
        symbol = StockSymbol("AAPL")
        stock = StockEntity(symbol=symbol, name="Apple Inc.")

        stock.update_fields(sector="Technology")
        assert stock.sector == "Technology"
        assert stock.industry_group is None

    def test_update_fields_sector_and_industry_group(self):
        """Should update both sector and industry_group when valid combination."""
        symbol = StockSymbol("AAPL")
        stock = StockEntity(symbol=symbol, name="Apple Inc.")

        stock.update_fields(sector="Technology", industry_group="Software")
        assert stock.sector == "Technology"
        assert stock.industry_group == "Software"

    def test_update_fields_invalid_sector_industry_combination_rollback(self):
        """Should rollback all changes if sector-industry combination is invalid."""
        symbol = StockSymbol("AAPL")
        stock = StockEntity(
            symbol=symbol,
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
        )

        with pytest.raises(
            ValueError,
            match="Industry group 'Pharmaceuticals' is not valid for sector 'Technology'",
        ):
            stock.update_fields(
                name="Apple Inc. Updated",
                sector="Technology",
                industry_group="Pharmaceuticals",  # Invalid combination
                notes="New notes",
            )

        # Original values should be unchanged
        assert stock.name == "Apple Inc."
        assert stock.sector == "Technology"
        assert stock.industry_group == "Software"
        assert stock.notes == ""

    def test_update_fields_add_industry_group_to_existing_sector(self):
        """Should allow adding industry_group to stock with existing sector."""
        symbol = StockSymbol("AAPL")
        stock = StockEntity(symbol=symbol, name="Apple Inc.", sector="Technology")

        assert stock.industry_group is None

        stock.update_fields(industry_group="Software")
        assert stock.sector == "Technology"
        assert stock.industry_group == "Software"

    def test_update_fields_change_sector_clears_incompatible_industry_group(self):
        """Should clear industry_group when changing to incompatible sector."""
        symbol = StockSymbol("AAPL")
        stock = StockEntity(
            symbol=symbol,
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
        )

        # Change to Healthcare sector - Software is not valid for Healthcare
        stock.update_fields(sector="Healthcare")
        assert stock.sector == "Healthcare"
        assert stock.industry_group is None  # Should be cleared

    def test_update_fields_industry_group_without_sector_raises_error(self):
        """Should raise error when trying to set industry_group without sector."""
        symbol = StockSymbol("AAPL")
        stock = StockEntity(symbol=symbol, name="Apple Inc.")

        with pytest.raises(
            ValueError, match="Sector must be provided when industry_group is specified"
        ):
            stock.update_fields(industry_group="Software")
