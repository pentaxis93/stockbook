"""
Tests for Stock domain entity.

Following TDD approach - these tests define the expected behavior
of the rich Stock entity with business logic.
"""

# from decimal import Decimal  # Unused import

import pytest

from src.domain.entities.stock import Stock
from src.domain.value_objects import (
    CompanyName,
    Grade,
    IndustryGroup,
    Notes,
)
from src.domain.value_objects.sector import Sector
from src.domain.value_objects.stock_symbol import StockSymbol


class TestStock:
    """Test suite for Stock domain entity."""

    def test_create_stock_with_value_objects(self) -> None:
        """Should create Stock entity with value objects only."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        sector = Sector("Technology")
        industry_group = IndustryGroup("Software")
        grade = Grade("A")
        notes = Notes("Great company")

        stock = Stock(
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
        assert stock.id is not None  # Generated UUID
        assert isinstance(stock.id, str)

    def test_create_stock_with_minimal_data(self) -> None:
        """Should create Stock with only required fields."""
        symbol = StockSymbol("MSFT")
        company_name = CompanyName("Microsoft Corp.")
        stock = Stock(symbol=symbol, company_name=company_name)

        assert stock.symbol == symbol
        assert stock.company_name == company_name
        assert stock.sector is None
        assert stock.industry_group is None
        assert stock.grade is None
        assert stock.notes.value == ""  # Notes defaults to empty

    def test_create_stock_without_company_name(self) -> None:
        """Should create Stock with only symbol (company name is optional)."""
        symbol = StockSymbol("MSFT")
        stock = Stock(symbol=symbol)

        assert stock.symbol == symbol
        assert stock.company_name is None
        assert stock.sector is None
        assert stock.industry_group is None
        assert stock.grade is None
        assert stock.notes.value == ""  # Notes defaults to empty

    def test_stock_stores_value_objects(self) -> None:
        """Should store and return value objects directly."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        sector = Sector("Technology")
        industry_group = IndustryGroup("Software")
        notes = Notes("Great company")

        stock = Stock(
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
        assert stock.company_name is not None
        assert stock.company_name.value == "Apple Inc."
        assert stock.sector is not None
        assert stock.sector is not None
        assert stock.sector.value == "Technology"
        assert stock.industry_group is not None
        assert stock.industry_group.value == "Software"
        assert stock.notes.value == "Great company"

    def test_create_stock_with_empty_name_allowed(self) -> None:
        """Should allow creating stock with empty company name."""
        symbol = StockSymbol("AAPL")
        empty_name = CompanyName("")
        whitespace_name = CompanyName("   ")

        stock_empty_name = Stock(symbol=symbol, company_name=empty_name)
        assert stock_empty_name.symbol == symbol
        assert stock_empty_name.company_name is not None
        assert stock_empty_name.company_name.value == ""

        stock_whitespace_name = Stock(symbol=symbol, company_name=whitespace_name)
        assert stock_whitespace_name.symbol == symbol
        assert stock_whitespace_name.company_name is not None
        assert stock_whitespace_name.company_name.value == ""  # Whitespace is stripped

    def test_create_stock_with_optional_none_values(self) -> None:
        """Should allow creating stock with None for optional value objects."""
        symbol = StockSymbol("AAPL")

        stock = Stock(
            symbol=symbol,
            company_name=None,
            sector=None,
            industry_group=None,
            grade=None,
            notes=None,
        )
        assert stock.symbol == symbol
        assert stock.company_name is None
        assert stock.sector is None
        assert stock.industry_group is None
        assert stock.grade is None
        assert stock.notes.value == ""  # Notes defaults to empty when None

    def test_create_stock_with_invalid_grade_raises_error(self) -> None:
        """Should raise error for invalid grade through Grade value object."""
        with pytest.raises(ValueError, match="Grade must be one of"):
            _ = Grade("Z")  # Error happens at Grade construction

    def test_create_stock_with_too_long_name_raises_error(self) -> None:
        """Should raise error for company name that's too long (delegated to value object)."""
        long_name = "A" * 201  # Max is 200 characters

        with pytest.raises(
            ValueError, match="Company name cannot exceed 200 characters"
        ):
            _ = CompanyName(long_name)  # Error happens at CompanyName construction

    def test_create_stock_with_too_long_industry_raises_error(self) -> None:
        """Should raise error for industry group that's too long (delegated to value object)."""
        long_industry = "A" * 101  # Max is 100 characters

        with pytest.raises(
            ValueError, match="Industry group cannot exceed 100 characters"
        ):
            _ = IndustryGroup(
                long_industry
            )  # Error happens at IndustryGroup construction

    def test_create_stock_with_too_long_notes_raises_error(self) -> None:
        """Should raise error for notes that are too long (delegated to value object)."""
        long_notes = "A" * 1001  # Max is 1000 characters

        with pytest.raises(ValueError, match="Notes cannot exceed 1000 characters"):
            _ = Notes(long_notes)  # Error happens at Notes construction

    def test_stock_equality(self) -> None:
        """Should compare stocks based on ID."""
        symbol1 = StockSymbol("AAPL")
        symbol2 = StockSymbol("AAPL")
        symbol3 = StockSymbol("MSFT")

        name1 = CompanyName("Apple Inc.")
        name2 = CompanyName("Apple Inc.")
        name3 = CompanyName("Microsoft")

        # Different instances with same symbol but different IDs are NOT equal
        stock1 = Stock(symbol=symbol1, company_name=name1)
        stock2 = Stock(symbol=symbol2, company_name=name2)  # Same symbol, different ID
        stock3 = Stock(symbol=symbol3, company_name=name3)  # Different symbol

        assert stock1 != stock2  # Different IDs
        assert stock1 != stock3  # Different IDs

        # Same ID means equal
        stock4 = Stock(symbol=symbol1, company_name=name1, id="same-id")
        stock5 = Stock(symbol=symbol2, company_name=name2, id="same-id")
        assert stock4 == stock5  # Same ID, even with different symbols

    def test_stock_hash(self) -> None:
        """Should be hashable based on ID."""
        symbol1 = StockSymbol("AAPL")
        symbol2 = StockSymbol("AAPL")
        symbol3 = StockSymbol("MSFT")

        name1 = CompanyName("Apple Inc.")
        name2 = CompanyName("Apple Inc.")
        name3 = CompanyName("Microsoft")

        stock1 = Stock(symbol=symbol1, company_name=name1)
        stock2 = Stock(symbol=symbol2, company_name=name2)
        stock3 = Stock(symbol=symbol3, company_name=name3)

        # Different IDs should have different hashes (likely but not guaranteed)
        assert hash(stock1) != hash(stock2)

        # Can be used in set - all have different IDs
        stock_set = {stock1, stock2, stock3}
        assert len(stock_set) == 3  # All stocks are different due to unique IDs

        # Same ID should have same hash
        stock4 = Stock(symbol=symbol1, company_name=name1, id="same-id")
        stock5 = Stock(symbol=symbol2, company_name=name2, id="same-id")
        assert hash(stock4) == hash(stock5)

    def test_stock_string_representation(self) -> None:
        """Should have meaningful string representation."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        stock = Stock(symbol=symbol, company_name=company_name)

        assert str(stock) == "AAPL - Apple Inc."

        # Test with no company name
        stock_no_name = Stock(symbol=symbol)
        assert str(stock_no_name) == "AAPL"

    def test_stock_repr(self) -> None:
        """Should have detailed repr representation."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        grade = Grade("A")
        stock = Stock(symbol=symbol, company_name=company_name, grade=grade)

        expected = "Stock(symbol=StockSymbol('AAPL'), company_name=CompanyName('Apple Inc.'), grade=Grade('A'))"
        assert repr(stock) == expected

        # Test with no company name
        stock_no_name = Stock(symbol=symbol, grade=grade)
        expected_no_name = (
            "Stock(symbol=StockSymbol('AAPL'), company_name=None, grade=Grade('A'))"
        )
        assert repr(stock_no_name) == expected_no_name

    def test_has_notes(self) -> None:
        """Should check if stock has notes."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        notes = Notes("Great company")
        empty_notes = Notes("")

        stock_with_notes = Stock(symbol=symbol, company_name=company_name, notes=notes)
        stock_without_notes = Stock(symbol=symbol, company_name=company_name)
        stock_empty_notes = Stock(
            symbol=symbol, company_name=company_name, notes=empty_notes
        )

        assert stock_with_notes.has_notes() is True
        assert stock_without_notes.has_notes() is False
        assert stock_empty_notes.has_notes() is False

    def test_update_fields_single_field(self) -> None:
        """Should update individual fields using update_fields method."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        grade = Grade("B")
        stock = Stock(symbol=symbol, company_name=company_name, grade=grade)

        # Update grade
        stock.update_fields(grade="A")
        assert stock.grade is not None
        assert stock.grade.value == "A"

        # Update name
        stock.update_fields(name="Apple Inc. Updated")
        assert stock.company_name is not None
        assert stock.company_name.value == "Apple Inc. Updated"

        # Update sector and industry_group
        stock.update_fields(sector="Technology", industry_group="Software")
        assert stock.sector is not None
        assert stock.sector is not None
        assert stock.sector.value == "Technology"
        assert stock.industry_group is not None
        assert stock.industry_group.value == "Software"

        # Update notes
        stock.update_fields(notes="Great company")
        assert stock.notes.value == "Great company"

    def test_update_company_name_to_none(self) -> None:
        """Should allow updating company name to None."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        stock = Stock(symbol=symbol, company_name=company_name)

        # Update name to None
        stock.update_fields(name=None)
        assert stock.company_name is None

        # Update from None to a value
        stock.update_fields(name="Apple Corporation")
        assert stock.company_name is not None
        assert stock.company_name.value == "Apple Corporation"

    def test_update_fields_multiple_fields_atomic(self) -> None:
        """Should update multiple fields atomically."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        stock = Stock(symbol=symbol, company_name=company_name)

        # Update multiple fields at once
        stock.update_fields(
            name="Apple Inc. Updated",
            grade="A",
            sector="Technology",
            industry_group="Software",
            notes="Excellent company",
        )

        assert stock.company_name is not None
        assert stock.company_name.value == "Apple Inc. Updated"
        assert stock.grade is not None
        assert stock.grade.value == "A"
        assert stock.sector is not None
        assert stock.sector is not None
        assert stock.sector.value == "Technology"
        assert stock.industry_group is not None
        assert stock.industry_group.value == "Software"
        assert stock.notes.value == "Excellent company"

    def test_update_fields_validation_failure_rollback(self) -> None:
        """Should rollback all changes if any validation fails."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        grade = Grade("B")
        stock = Stock(symbol=symbol, company_name=company_name, grade=grade)

        # Try to update with invalid grade - should fail and rollback all
        with pytest.raises(ValueError, match="Grade must be one of"):
            stock.update_fields(
                name="Apple Inc. Updated", grade="Z", notes="New notes"  # Invalid grade
            )

        # Original values should be unchanged
        assert stock.company_name is not None
        assert stock.company_name.value == "Apple Inc."
        assert stock.grade is not None
        assert stock.grade.value == "B"
        assert stock.notes.value == ""

    def test_update_fields_with_too_long_values_raises_error(self) -> None:
        """Should raise error for values that are too long."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        stock = Stock(symbol=symbol, company_name=company_name)

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

    def test_create_stock_with_id(self) -> None:
        """Should create stock with provided ID."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        test_id = "stock-id-123"
        stock = Stock(symbol=symbol, company_name=company_name, id=test_id)

        assert stock.id == test_id

    def test_stock_id_immutability(self) -> None:
        """Should not be able to change ID after creation."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        stock = Stock(symbol=symbol, company_name=company_name, id="test-id-1")

        # ID property should not have a setter
        with pytest.raises(AttributeError):
            stock.id = "different-id"  # type: ignore[misc]

    def test_stock_from_persistence(self) -> None:
        """Should create stock from persistence with existing ID."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        test_id = "persistence-id-456"

        stock = Stock.from_persistence(
            test_id,
            symbol=symbol,
            company_name=company_name,
            sector=Sector("Technology"),
            grade=Grade("A"),
        )

        assert stock.id == test_id
        assert stock.symbol.value == "AAPL"
        assert stock.sector is not None
        assert stock.sector.value == "Technology"

    # New tests for sector functionality
    def test_create_stock_with_sector_and_industry_group(self) -> None:
        """Should create Stock entity with sector and industry_group."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        sector = Sector("Technology")
        industry_group = IndustryGroup("Software")
        grade = Grade("A")

        stock = Stock(
            symbol=symbol,
            company_name=company_name,
            sector=sector,
            industry_group=industry_group,
            grade=grade,
        )

        assert stock.symbol == symbol
        assert stock.company_name is not None
        assert stock.company_name.value == "Apple Inc."
        assert stock.sector is not None
        assert stock.sector is not None
        assert stock.sector.value == "Technology"
        assert stock.industry_group is not None
        assert stock.industry_group.value == "Software"
        assert stock.grade is not None
        assert stock.grade.value == "A"
        assert isinstance(stock.sector, Sector)
        assert isinstance(stock.industry_group, IndustryGroup)

    def test_create_stock_with_sector_only(self) -> None:
        """Should create Stock with sector but no industry_group."""
        symbol = StockSymbol("MSFT")
        company_name = CompanyName("Microsoft Corp.")
        sector = Sector("Technology")

        stock = Stock(symbol=symbol, company_name=company_name, sector=sector)

        assert stock.symbol == symbol
        assert stock.company_name is not None
        assert stock.company_name.value == "Microsoft Corp."
        assert stock.sector is not None
        assert stock.sector.value == "Technology"
        assert stock.industry_group is None
        assert isinstance(stock.sector, Sector)
        assert stock.industry_group is None

    def test_create_stock_with_invalid_sector_industry_combination_raises_error(
        self,
    ) -> None:
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
            _ = Stock(
                symbol=symbol,
                company_name=company_name,
                sector=sector,
                industry_group=industry_group,
            )

    def test_create_stock_with_industry_group_but_no_sector_raises_error(self) -> None:
        """Should raise error when industry_group is provided without sector."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        industry_group = IndustryGroup("Software")  # No sector provided

        with pytest.raises(
            ValueError, match="Sector must be provided when industry_group is specified"
        ):
            _ = Stock(
                symbol=symbol,
                company_name=company_name,
                industry_group=industry_group,
            )

    def test_create_stock_with_empty_sector_raises_error(self) -> None:
        """Should raise error for empty sector string."""
        with pytest.raises(ValueError, match="Sector cannot be empty"):
            _ = Sector("")  # Error happens at Sector construction

    def test_create_stock_with_too_long_sector_raises_error(self) -> None:
        """Should raise error for sector that's too long."""
        long_sector = "A" * 101  # Max is 100 characters

        with pytest.raises(ValueError, match="Sector cannot exceed 100 characters"):
            _ = Sector(long_sector)  # Error happens at Sector construction

    def test_update_fields_sector_only(self) -> None:
        """Should update sector without industry_group."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        stock = Stock(symbol=symbol, company_name=company_name)

        stock.update_fields(sector="Technology")
        assert stock.sector is not None
        assert stock.sector.value == "Technology"
        assert stock.industry_group is None

    def test_update_fields_sector_and_industry_group(self) -> None:
        """Should update both sector and industry_group when valid combination."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        stock = Stock(symbol=symbol, company_name=company_name)

        stock.update_fields(sector="Technology", industry_group="Software")
        assert stock.sector is not None
        assert stock.sector is not None
        assert stock.sector.value == "Technology"
        assert stock.industry_group is not None
        assert stock.industry_group.value == "Software"

    def test_update_fields_invalid_sector_industry_combination_rollback(self) -> None:
        """Should rollback all changes if sector-industry combination is invalid."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        sector = Sector("Technology")
        industry_group = IndustryGroup("Software")

        stock = Stock(
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
        assert stock.company_name is not None
        assert stock.company_name.value == "Apple Inc."
        assert stock.sector is not None
        assert stock.sector is not None
        assert stock.sector.value == "Technology"
        assert stock.industry_group is not None
        assert stock.industry_group.value == "Software"
        assert stock.notes.value == ""

    def test_update_fields_add_industry_group_to_existing_sector(self) -> None:
        """Should allow adding industry_group to stock with existing sector."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        sector = Sector("Technology")
        stock = Stock(symbol=symbol, company_name=company_name, sector=sector)

        assert stock.industry_group is None

        stock.update_fields(industry_group="Software")
        assert stock.sector is not None
        assert stock.sector is not None
        assert stock.sector.value == "Technology"
        assert stock.industry_group is not None
        assert stock.industry_group.value == "Software"

    def test_update_fields_change_sector_clears_incompatible_industry_group(
        self,
    ) -> None:
        """Should clear industry_group when changing to incompatible sector."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        sector = Sector("Technology")
        industry_group = IndustryGroup("Software")

        stock = Stock(
            symbol=symbol,
            company_name=company_name,
            sector=sector,
            industry_group=industry_group,
        )

        # Change to Healthcare sector - Software is not valid for Healthcare
        stock.update_fields(sector="Healthcare")
        assert stock.sector is not None
        assert stock.sector.value == "Healthcare"
        assert stock.industry_group is None  # Should be cleared

    def test_update_fields_industry_group_without_sector_raises_error(self) -> None:
        """Should raise error when trying to set industry_group without sector."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        stock = Stock(symbol=symbol, company_name=company_name)

        with pytest.raises(
            ValueError, match="Sector must be provided when industry_group is specified"
        ):
            stock.update_fields(industry_group="Software")


class TestStockLifecycle:
    """Test stock entity lifecycle management and state transitions."""

    def test_stock_creation_lifecycle(self) -> None:
        """Should properly initialize stock through entire creation lifecycle."""
        # Step 1: Create with minimal required data
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        stock = Stock(symbol=symbol, company_name=company_name)

        assert stock.symbol == symbol
        assert stock.company_name == company_name
        assert stock.id is not None
        assert len(stock.id) > 0

        # Step 2: Enhance with additional business data
        stock.update_fields(
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="Initial assessment - strong fundamentals",
        )

        assert stock.sector is not None
        assert stock.sector.value == "Technology"
        assert stock.industry_group is not None
        assert stock.industry_group.value == "Software"
        assert stock.grade is not None
        assert stock.grade.value == "A"
        assert "strong fundamentals" in stock.notes.value

    def test_stock_data_evolution_over_time(self) -> None:
        """Should handle data changes that occur over time."""
        stock = Stock(
            symbol=StockSymbol("AAPL"),
            company_name=CompanyName("Apple Inc."),
            grade=Grade("B"),
            notes=Notes("Initial grade B assessment"),
        )

        # Quarter 1: Upgrade after good performance
        stock.update_fields(
            grade="A", notes="Upgraded to A after excellent Q1 earnings"
        )
        assert stock.grade is not None
        assert stock.grade.value == "A"

        # Quarter 2: Add sector classification
        stock.update_fields(
            sector="Technology",
            industry_group="Software",
            notes="Added sector classification during portfolio rebalancing",
        )
        assert stock.sector is not None
        assert stock.sector.value == "Technology"
        assert stock.industry_group is not None
        assert stock.industry_group.value == "Software"

        # Quarter 3: Company name change (acquisition/rebrand)
        stock.update_fields(
            name="Apple Inc. (Updated)",
            notes="Company name updated after corporate restructuring",
        )
        assert stock.company_name is not None
        assert stock.company_name.value == "Apple Inc. (Updated)"

    def test_stock_persistence_roundtrip(self) -> None:
        """Should maintain data integrity through persistence operations."""
        # Create stock with full data
        original_stock = Stock(
            symbol=StockSymbol("MSFT"),
            company_name=CompanyName("Microsoft Corporation"),
            sector=Sector("Technology"),
            industry_group=IndustryGroup("Software"),
            grade=Grade("A"),
            notes=Notes("Leading cloud provider"),
            id="persistence-test-id",
        )

        # Simulate persistence (saving to database)
        persisted_data = {
            "id": original_stock.id,
            "symbol": original_stock.symbol.value,
            "company_name": (
                original_stock.company_name.value
                if original_stock.company_name
                else None
            ),
            "sector": original_stock.sector.value if original_stock.sector else None,
            "industry_group": (
                original_stock.industry_group.value
                if original_stock.industry_group
                else None
            ),
            "grade": original_stock.grade.value if original_stock.grade else None,
            "notes": original_stock.notes.value,
        }

        # Simulate retrieval from persistence
        assert persisted_data["id"] is not None
        assert persisted_data["symbol"] is not None
        assert persisted_data["company_name"] is not None
        restored_stock = Stock.from_persistence(
            persisted_data["id"],
            symbol=StockSymbol(persisted_data["symbol"]),
            company_name=CompanyName(persisted_data["company_name"]),
            sector=(
                Sector(persisted_data["sector"]) if persisted_data["sector"] else None
            ),
            industry_group=(
                IndustryGroup(persisted_data["industry_group"])
                if persisted_data["industry_group"]
                else None
            ),
            grade=Grade(persisted_data["grade"]) if persisted_data["grade"] else None,
            notes=Notes(persisted_data["notes"]) if persisted_data["notes"] else None,
        )

        # Verify complete data integrity
        assert restored_stock.id == original_stock.id
        assert restored_stock.symbol == original_stock.symbol
        assert restored_stock.company_name == original_stock.company_name
        assert restored_stock.sector == original_stock.sector
        assert restored_stock.industry_group == original_stock.industry_group
        assert restored_stock.grade == original_stock.grade
        assert restored_stock.notes == original_stock.notes
        assert restored_stock == original_stock  # Entity equality

    def test_stock_defensive_copying_patterns(self) -> None:
        """Should ensure value objects maintain immutability through lifecycle."""
        symbol = StockSymbol("GOOGL")
        company_name = CompanyName("Alphabet Inc.")
        sector = Sector("Technology")

        stock = Stock(symbol=symbol, company_name=company_name, sector=sector)

        # Verify that getting value objects returns the same instances
        retrieved_symbol = stock.symbol
        retrieved_sector = stock.sector

        assert retrieved_symbol is symbol  # Same object reference
        assert retrieved_sector is sector  # Same object reference

        # Verify that value objects are immutable
        with pytest.raises(AttributeError):
            retrieved_symbol.value = "CHANGED"  # type: ignore[misc]


class TestStockDomainInvariants:
    """Test domain business rules and invariants enforcement."""

    def test_symbol_uniqueness_invariant(self) -> None:
        """Should enforce symbol uniqueness business rule conceptually."""
        # Note: With ID-based equality, symbol uniqueness must be enforced
        # at the repository level, not through entity equality

        symbol = StockSymbol("AAPL")
        name1 = CompanyName("Apple Inc.")
        name2 = CompanyName("Different Company")

        stock1 = Stock(symbol=symbol, company_name=name1)
        stock2 = Stock(symbol=symbol, company_name=name2)

        # With ID-based equality, stocks with same symbol but different IDs are NOT equal
        assert stock1 != stock2
        assert hash(stock1) != hash(stock2)

        # This demonstrates why repository must enforce uniqueness
        stock_set = {stock1, stock2}
        assert len(stock_set) == 2  # Both stocks are in the set due to different IDs

        # Repository would need to check for symbol uniqueness before allowing insert/update

    def test_sector_industry_consistency_invariant(self) -> None:
        """Should enforce sector-industry group consistency at all times."""
        stock = Stock(
            symbol=StockSymbol("AAPL"),
            company_name=CompanyName("Apple Inc."),
            sector=Sector("Technology"),
            industry_group=IndustryGroup("Software"),
        )

        # Valid updates should work
        stock.update_fields(industry_group="Hardware")  # Still valid for Technology
        assert stock.industry_group is not None
        assert stock.industry_group.value == "Hardware"

        # Invalid updates should fail and maintain consistency
        with pytest.raises(ValueError):
            stock.update_fields(
                industry_group="Pharmaceuticals"
            )  # Invalid for Technology

        # Stock should maintain valid state after failed update
        assert stock.sector is not None
        assert stock.sector.value == "Technology"
        assert stock.industry_group is not None
        assert stock.industry_group.value == "Hardware"  # Still the last valid value

    def test_data_completeness_progression(self) -> None:
        """Should support progressive data enrichment without breaking invariants."""
        # Start with minimal data (valid state)
        stock = Stock(
            symbol=StockSymbol("TSLA"), company_name=CompanyName("Tesla Inc.")
        )
        assert stock.sector is None
        assert stock.industry_group is None

        # Add sector (still valid state)
        stock.update_fields(sector="Consumer Goods")
        assert stock.sector is not None
        assert stock.sector.value == "Consumer Goods"
        assert stock.industry_group is None

        # Add compatible industry group (still valid state)
        stock.update_fields(industry_group="Automotive")
        assert stock.sector is not None
        assert stock.sector.value == "Consumer Goods"
        assert stock.industry_group is not None
        assert stock.industry_group.value == "Automotive"

        # Change to incompatible sector should clear industry group
        stock.update_fields(sector="Technology")
        assert stock.sector is not None
        assert stock.sector.value == "Technology"
        assert stock.industry_group is None  # Cleared automatically

    def test_entity_validation_cascade(self) -> None:
        """Should validate that all value object constraints are enforced through entity."""
        symbol = StockSymbol("TEST")
        company_name = CompanyName("Test Corp")

        stock = Stock(symbol=symbol, company_name=company_name)

        # Test cascading validation failures
        validation_test_cases = [
            # (field, invalid_value, expected_error_pattern)
            ("name", "A" * 201, "Company name cannot exceed 200 characters"),
            ("sector", "A" * 101, "Sector cannot exceed 100 characters"),
            (
                "industry_group",
                "A" * 101,
                "Industry group cannot exceed 100 characters",
            ),
            ("grade", "Z", "Grade must be one of"),
            ("notes", "A" * 1001, "Notes cannot exceed 1000 characters"),
        ]

        for field, invalid_value, error_pattern in validation_test_cases:
            with pytest.raises(ValueError, match=error_pattern):
                stock.update_fields(**{field: invalid_value})

            # Verify stock maintains valid state after each failed validation
            assert stock.symbol == symbol
            assert stock.company_name == company_name


class TestStockBusinessOperations:
    """Test business operations and calculations performed by stock entity."""

    def test_stock_business_logic_methods(self) -> None:
        """Should provide meaningful business logic methods."""
        # Stock with notes
        stock_with_notes = Stock(
            symbol=StockSymbol("NOTED"),
            company_name=CompanyName("Well Documented Corp"),
            notes=Notes("Has detailed analysis notes"),
        )
        assert stock_with_notes.has_notes() is True

        # Stock without notes
        stock_without_notes = Stock(
            symbol=StockSymbol("BARE"), company_name=CompanyName("Minimal Corp")
        )
        assert stock_without_notes.has_notes() is False

        # Stock with empty notes
        stock_empty_notes = Stock(
            symbol=StockSymbol("EMPTY"),
            company_name=CompanyName("Empty Notes Corp"),
            notes=Notes(""),
        )
        assert stock_empty_notes.has_notes() is False


class TestStockConcurrencyScenarios:
    """Test scenarios that might occur in concurrent/multi-user environments."""

    def test_stock_update_idempotency(self) -> None:
        """Should handle repeated identical updates gracefully."""
        stock = Stock(
            symbol=StockSymbol("IDEM"),
            company_name=CompanyName("Idempotent Corp"),
            grade=Grade("B"),
        )

        # Apply same update multiple times
        for _ in range(3):
            stock.update_fields(grade="A", notes="Upgraded rating")

        assert stock.grade is not None
        assert stock.grade.value == "A"
        assert "Upgraded rating" in stock.notes.value

        # Apply update with same values (should be idempotent)
        stock.update_fields(grade="A", notes="Upgraded rating")
        assert stock.grade is not None
        assert stock.grade.value == "A"

    def test_stock_state_consistency_after_partial_failures(self) -> None:
        """Should maintain consistent state even after partial update failures."""
        stock = Stock(
            symbol=StockSymbol("ROBST"),
            company_name=CompanyName("Robust Corp"),
            sector=Sector("Technology"),
            industry_group=IndustryGroup("Software"),
            grade=Grade("A"),
            notes=Notes("Initial notes"),
        )

        # Capture original state
        assert stock.company_name is not None
        original_name = stock.company_name.value
        assert stock.sector is not None
        original_sector = stock.sector.value
        assert stock.industry_group is not None
        original_industry = stock.industry_group.value
        assert stock.grade is not None
        original_grade = stock.grade.value
        original_notes = stock.notes.value

        # Attempt update that will fail due to invalid grade
        with pytest.raises(ValueError):
            stock.update_fields(
                name="Updated Corp",
                sector="Healthcare",
                industry_group="Pharmaceuticals",
                grade="Z",  # Invalid grade - will cause rollback
                notes="Should not be saved",
            )

        # Verify all original values are preserved (atomic update failure)
        assert stock.company_name is not None
        assert stock.company_name.value == original_name
        assert stock.sector is not None
        assert stock.sector.value == original_sector
        assert stock.industry_group is not None
        assert stock.industry_group.value == original_industry
        assert stock.grade is not None
        assert stock.grade.value == original_grade
        assert stock.notes.value == original_notes

    def test_stock_entity_collection_operations(self) -> None:
        """Should work properly in collections (sets, dicts) with ID-based equality."""
        # Create stocks with unique IDs
        aapl1 = Stock(
            symbol=StockSymbol("AAPL"),
            company_name=CompanyName("Apple Inc."),
            grade=Grade("A"),
        )

        aapl2 = Stock(
            symbol=StockSymbol("AAPL"),
            company_name=CompanyName("Apple Inc."),
            grade=Grade("B"),  # Different grade, same symbol, different ID
        )

        msft = Stock(
            symbol=StockSymbol("MSFT"), company_name=CompanyName("Microsoft Corp")
        )

        # Test set operations (no deduplication by symbol anymore)
        stock_set = {aapl1, aapl2, msft}
        assert len(stock_set) == 3  # All stocks have different IDs

        # Test dictionary operations (stock as key)
        portfolio_weights = {aapl1: 0.6, msft: 0.4}

        # With ID-based equality, aapl2 is a different key than aapl1
        assert aapl1 in portfolio_weights
        assert aapl2 not in portfolio_weights  # Different ID means different key
        assert portfolio_weights[aapl1] == 0.6
        assert portfolio_weights[msft] == 0.4

    def test_stock_equality_with_non_stock_object(self) -> None:
        """Test that stock equality returns False for non-Stock objects."""
        stock = Stock(
            symbol=StockSymbol("AAPL"),
            company_name=CompanyName("Apple Inc."),
            sector=Sector("Technology"),
            industry_group=IndustryGroup("Software"),  # Valid for Technology sector
            grade=Grade("A"),
        )

        # Test equality with different types - should return False (covers line 121)
        assert stock != "not a stock"
        assert stock != 123
        assert stock != None
        assert stock != {"symbol": "AAPL", "company_name": "Apple Inc."}
