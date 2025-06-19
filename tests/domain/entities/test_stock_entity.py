"""
Tests for Stock domain entity.

Following TDD approach - these tests define the expected behavior
of the rich Stock entity with business logic.
"""

from decimal import Decimal

import pytest

from domain.entities.stock_entity import StockEntity
from domain.value_objects import CompanyName, Grade, IndustryGroup, Notes
from domain.value_objects.sector import Sector
from domain.value_objects.stock_symbol import StockSymbol
from shared_kernel.value_objects import Money, Quantity


class TestStockEntity:
    """Test suite for Stock domain entity."""

    def test_create_stock_with_value_objects(self):
        """Should create Stock entity with value objects only."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        sector = Sector("Technology")
        industry_group = IndustryGroup("Software")
        grade = Grade("A")
        notes = Notes("Great company")

        stock = StockEntity(
            symbol=symbol,
            company_name=company_name,
            sector=sector,
            industry_group=industry_group,
            grade=grade,
            notes=notes,
        )

        assert stock.symbol == symbol
        assert stock.company_name == company_name
        assert stock.sector == sector
        assert stock.industry_group == industry_group
        assert stock.grade == grade
        assert stock.notes == notes
        assert stock.id is None  # Not yet persisted

    def test_create_stock_with_minimal_data(self):
        """Should create Stock with only required fields."""
        symbol = StockSymbol("MSFT")
        company_name = CompanyName("Microsoft Corp.")
        stock = StockEntity(symbol=symbol, company_name=company_name)

        assert stock.symbol == symbol
        assert stock.company_name == company_name
        assert stock.sector is None
        assert stock.industry_group is None
        assert stock.grade is None
        assert stock.notes.value == ""  # Notes defaults to empty

    def test_stock_stores_value_objects(self):
        """Should store and return value objects directly."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        sector = Sector("Technology")
        industry_group = IndustryGroup("Software")
        notes = Notes("Great company")

        stock = StockEntity(
            symbol=symbol,
            company_name=company_name,
            sector=sector,
            industry_group=industry_group,
            notes=notes,
        )

        # Should return the exact same value objects
        assert stock.company_name is company_name
        assert stock.sector is sector
        assert stock.industry_group is industry_group
        assert stock.notes is notes

        # String access through value property
        assert stock.company_name.value == "Apple Inc."
        assert stock.sector.value == "Technology"
        assert stock.industry_group.value == "Software"
        assert stock.notes.value == "Great company"

    def test_create_stock_with_empty_name_allowed(self):
        """Should allow creating stock with empty company name."""
        symbol = StockSymbol("AAPL")
        empty_name = CompanyName("")
        whitespace_name = CompanyName("   ")

        stock_empty_name = StockEntity(symbol=symbol, company_name=empty_name)
        assert stock_empty_name.symbol == symbol
        assert stock_empty_name.company_name.value == ""

        stock_whitespace_name = StockEntity(symbol=symbol, company_name=whitespace_name)
        assert stock_whitespace_name.symbol == symbol
        assert stock_whitespace_name.company_name.value == ""  # Whitespace is stripped

    def test_create_stock_with_optional_none_values(self):
        """Should allow creating stock with None for optional value objects."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")

        stock = StockEntity(
            symbol=symbol,
            company_name=company_name,
            sector=None,
            industry_group=None,
            grade=None,
            notes=None,
        )
        assert stock.symbol == symbol
        assert stock.company_name == company_name
        assert stock.sector is None
        assert stock.industry_group is None
        assert stock.grade is None
        assert stock.notes.value == ""  # Notes defaults to empty when None

    def test_create_stock_with_invalid_grade_raises_error(self):
        """Should raise error for invalid grade through Grade value object."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")

        with pytest.raises(ValueError, match="Grade must be one of"):
            Grade("Z")  # Error happens at Grade construction

    def test_create_stock_with_too_long_name_raises_error(self):
        """Should raise error for company name that's too long (delegated to value object)."""
        long_name = "A" * 201  # Max is 200 characters

        with pytest.raises(
            ValueError, match="Company name cannot exceed 200 characters"
        ):
            CompanyName(long_name)  # Error happens at CompanyName construction

    def test_create_stock_with_too_long_industry_raises_error(self):
        """Should raise error for industry group that's too long (delegated to value object)."""
        long_industry = "A" * 101  # Max is 100 characters

        with pytest.raises(
            ValueError, match="Industry group cannot exceed 100 characters"
        ):
            IndustryGroup(long_industry)  # Error happens at IndustryGroup construction

    def test_create_stock_with_too_long_notes_raises_error(self):
        """Should raise error for notes that are too long (delegated to value object)."""
        long_notes = "A" * 1001  # Max is 1000 characters

        with pytest.raises(ValueError, match="Notes cannot exceed 1000 characters"):
            Notes(long_notes)  # Error happens at Notes construction

    def test_stock_equality(self):
        """Should compare stocks based on symbol (business key)."""
        symbol1 = StockSymbol("AAPL")
        symbol2 = StockSymbol("AAPL")
        symbol3 = StockSymbol("MSFT")

        name1 = CompanyName("Apple Inc.")
        name2 = CompanyName("Apple Inc.")
        name3 = CompanyName("Microsoft")

        stock1 = StockEntity(symbol=symbol1, company_name=name1)
        stock2 = StockEntity(symbol=symbol2, company_name=name2)  # Same symbol
        stock3 = StockEntity(symbol=symbol3, company_name=name3)  # Different symbol

        assert stock1 == stock2  # Same symbol
        assert stock1 != stock3  # Different symbol

    def test_stock_hash(self):
        """Should be hashable based on symbol."""
        symbol1 = StockSymbol("AAPL")
        symbol2 = StockSymbol("AAPL")
        symbol3 = StockSymbol("MSFT")

        name1 = CompanyName("Apple Inc.")
        name2 = CompanyName("Apple Inc.")
        name3 = CompanyName("Microsoft")

        stock1 = StockEntity(symbol=symbol1, company_name=name1)
        stock2 = StockEntity(symbol=symbol2, company_name=name2)
        stock3 = StockEntity(symbol=symbol3, company_name=name3)

        # Same symbol should have same hash
        assert hash(stock1) == hash(stock2)

        # Can be used in set
        stock_set = {stock1, stock2, stock3}
        assert len(stock_set) == 2  # AAPL appears only once

    def test_stock_string_representation(self):
        """Should have meaningful string representation."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        stock = StockEntity(symbol=symbol, company_name=company_name)

        assert str(stock) == "AAPL - Apple Inc."

    def test_stock_repr(self):
        """Should have detailed repr representation."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        grade = Grade("A")
        stock = StockEntity(symbol=symbol, company_name=company_name, grade=grade)

        expected = "StockEntity(symbol=StockSymbol('AAPL'), company_name=CompanyName('Apple Inc.'), grade=Grade('A'))"
        assert repr(stock) == expected

    def test_calculate_position_value(self):
        """Should calculate total position value."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        stock = StockEntity(symbol=symbol, company_name=company_name)

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
        company_name = CompanyName("Apple Inc.")
        notes = Notes("Great company")
        empty_notes = Notes("")

        stock_with_notes = StockEntity(
            symbol=symbol, company_name=company_name, notes=notes
        )
        stock_without_notes = StockEntity(symbol=symbol, company_name=company_name)
        stock_empty_notes = StockEntity(
            symbol=symbol, company_name=company_name, notes=empty_notes
        )

        assert stock_with_notes.has_notes() is True
        assert stock_without_notes.has_notes() is False
        assert stock_empty_notes.has_notes() is False

    def test_update_fields_single_field(self):
        """Should update individual fields using update_fields method."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        grade = Grade("B")
        stock = StockEntity(symbol=symbol, company_name=company_name, grade=grade)

        # Update grade
        stock.update_fields(grade="A")
        assert stock.grade.value == "A"

        # Update name
        stock.update_fields(name="Apple Inc. Updated")
        assert stock.company_name.value == "Apple Inc. Updated"

        # Update sector and industry_group
        stock.update_fields(sector="Technology", industry_group="Software")
        assert stock.sector.value == "Technology"
        assert stock.industry_group.value == "Software"

        # Update notes
        stock.update_fields(notes="Great company")
        assert stock.notes.value == "Great company"

    def test_update_fields_multiple_fields_atomic(self):
        """Should update multiple fields atomically."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        stock = StockEntity(symbol=symbol, company_name=company_name)

        # Update multiple fields at once
        stock.update_fields(
            name="Apple Inc. Updated",
            grade="A",
            sector="Technology",
            industry_group="Software",
            notes="Excellent company",
        )

        assert stock.company_name.value == "Apple Inc. Updated"
        assert stock.grade.value == "A"
        assert stock.sector.value == "Technology"
        assert stock.industry_group.value == "Software"
        assert stock.notes.value == "Excellent company"

    def test_update_fields_validation_failure_rollback(self):
        """Should rollback all changes if any validation fails."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        grade = Grade("B")
        stock = StockEntity(symbol=symbol, company_name=company_name, grade=grade)

        # Try to update with invalid grade - should fail and rollback all
        with pytest.raises(ValueError, match="Grade must be one of"):
            stock.update_fields(
                name="Apple Inc. Updated", grade="Z", notes="New notes"  # Invalid grade
            )

        # Original values should be unchanged
        assert stock.company_name.value == "Apple Inc."
        assert stock.grade.value == "B"
        assert stock.notes.value == ""

    def test_update_fields_with_too_long_values_raises_error(self):
        """Should raise error for values that are too long."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        stock = StockEntity(symbol=symbol, company_name=company_name)

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
        company_name = CompanyName("Apple Inc.")
        stock = StockEntity(symbol=symbol, company_name=company_name)

        assert stock.id is None

        stock.set_id(123)
        assert stock.id == 123

    def test_set_id_with_invalid_id_raises_error(self):
        """Should raise error for invalid ID."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        stock = StockEntity(symbol=symbol, company_name=company_name)

        with pytest.raises(ValueError, match="ID must be a positive integer"):
            stock.set_id(0)

        with pytest.raises(ValueError, match="ID must be a positive integer"):
            stock.set_id(-1)

        with pytest.raises(ValueError, match="ID must be a positive integer"):
            stock.set_id("123")

    def test_set_id_when_already_set_raises_error(self):
        """Should raise error when trying to change existing ID."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        stock = StockEntity(symbol=symbol, company_name=company_name)

        stock.set_id(123)

        with pytest.raises(ValueError, match="ID is already set and cannot be changed"):
            stock.set_id(456)

    # New tests for sector functionality
    def test_create_stock_with_sector_and_industry_group(self):
        """Should create Stock entity with sector and industry_group."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        sector = Sector("Technology")
        industry_group = IndustryGroup("Software")
        grade = Grade("A")

        stock = StockEntity(
            symbol=symbol,
            company_name=company_name,
            sector=sector,
            industry_group=industry_group,
            grade=grade,
        )

        assert stock.symbol == symbol
        assert stock.company_name.value == "Apple Inc."
        assert stock.sector.value == "Technology"
        assert stock.industry_group.value == "Software"
        assert stock.grade.value == "A"
        assert isinstance(stock.sector, Sector)
        assert isinstance(stock.industry_group, IndustryGroup)

    def test_create_stock_with_sector_only(self):
        """Should create Stock with sector but no industry_group."""
        symbol = StockSymbol("MSFT")
        company_name = CompanyName("Microsoft Corp.")
        sector = Sector("Technology")

        stock = StockEntity(symbol=symbol, company_name=company_name, sector=sector)

        assert stock.symbol == symbol
        assert stock.company_name.value == "Microsoft Corp."
        assert stock.sector.value == "Technology"
        assert stock.industry_group is None
        assert isinstance(stock.sector, Sector)
        assert stock.industry_group is None

    def test_create_stock_with_invalid_sector_industry_combination_raises_error(self):
        """Should raise error when industry_group doesn't belong to sector."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        sector = Sector("Technology")
        industry_group = IndustryGroup(
            "Pharmaceuticals"
        )  # Invalid for Technology sector

        with pytest.raises(
            ValueError,
            match="Industry group 'Pharmaceuticals' is not valid for sector 'Technology'",
        ):
            StockEntity(
                symbol=symbol,
                company_name=company_name,
                sector=sector,
                industry_group=industry_group,
            )

    def test_create_stock_with_industry_group_but_no_sector_raises_error(self):
        """Should raise error when industry_group is provided without sector."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        industry_group = IndustryGroup("Software")  # No sector provided

        with pytest.raises(
            ValueError, match="Sector must be provided when industry_group is specified"
        ):
            StockEntity(
                symbol=symbol,
                company_name=company_name,
                industry_group=industry_group,
            )

    def test_create_stock_with_empty_sector_raises_error(self):
        """Should raise error for empty sector string."""
        with pytest.raises(ValueError, match="Sector cannot be empty"):
            Sector("")  # Error happens at Sector construction

    def test_create_stock_with_too_long_sector_raises_error(self):
        """Should raise error for sector that's too long."""
        long_sector = "A" * 101  # Max is 100 characters

        with pytest.raises(ValueError, match="Sector cannot exceed 100 characters"):
            Sector(long_sector)  # Error happens at Sector construction

    def test_update_fields_sector_only(self):
        """Should update sector without industry_group."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        stock = StockEntity(symbol=symbol, company_name=company_name)

        stock.update_fields(sector="Technology")
        assert stock.sector.value == "Technology"
        assert stock.industry_group is None

    def test_update_fields_sector_and_industry_group(self):
        """Should update both sector and industry_group when valid combination."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        stock = StockEntity(symbol=symbol, company_name=company_name)

        stock.update_fields(sector="Technology", industry_group="Software")
        assert stock.sector.value == "Technology"
        assert stock.industry_group.value == "Software"

    def test_update_fields_invalid_sector_industry_combination_rollback(self):
        """Should rollback all changes if sector-industry combination is invalid."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        sector = Sector("Technology")
        industry_group = IndustryGroup("Software")

        stock = StockEntity(
            symbol=symbol,
            company_name=company_name,
            sector=sector,
            industry_group=industry_group,
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
        assert stock.company_name.value == "Apple Inc."
        assert stock.sector.value == "Technology"
        assert stock.industry_group.value == "Software"
        assert stock.notes.value == ""

    def test_update_fields_add_industry_group_to_existing_sector(self):
        """Should allow adding industry_group to stock with existing sector."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        sector = Sector("Technology")
        stock = StockEntity(symbol=symbol, company_name=company_name, sector=sector)

        assert stock.industry_group is None

        stock.update_fields(industry_group="Software")
        assert stock.sector.value == "Technology"
        assert stock.industry_group.value == "Software"

    def test_update_fields_change_sector_clears_incompatible_industry_group(self):
        """Should clear industry_group when changing to incompatible sector."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        sector = Sector("Technology")
        industry_group = IndustryGroup("Software")

        stock = StockEntity(
            symbol=symbol,
            company_name=company_name,
            sector=sector,
            industry_group=industry_group,
        )

        # Change to Healthcare sector - Software is not valid for Healthcare
        stock.update_fields(sector="Healthcare")
        assert stock.sector.value == "Healthcare"
        assert stock.industry_group is None  # Should be cleared

    def test_update_fields_industry_group_without_sector_raises_error(self):
        """Should raise error when trying to set industry_group without sector."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        stock = StockEntity(symbol=symbol, company_name=company_name)

        with pytest.raises(
            ValueError, match="Sector must be provided when industry_group is specified"
        ):
            stock.update_fields(industry_group="Software")
