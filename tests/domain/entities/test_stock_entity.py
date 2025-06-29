"""
Tests for Stock domain entity.

Following TDD approach - these tests define the expected behavior
of the rich Stock entity with business logic.
"""

# from decimal import Decimal  # Unused import

import pytest

from src.domain.entities.stock_entity import StockEntity
from src.domain.value_objects import (
    CompanyName,
    Grade,
    IndustryGroup,
    Money,
    Notes,
    Quantity,
)
from src.domain.value_objects.sector import Sector
from src.domain.value_objects.stock_symbol import StockSymbol


class TestStockEntity:
    """Test suite for Stock domain entity."""

    def test_create_stock_with_value_objects(self) -> None:
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
        assert stock.id is not None  # Generated nanoid
        assert isinstance(stock.id, str)

    def test_create_stock_with_minimal_data(self) -> None:
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

    def test_stock_stores_value_objects(self) -> None:
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

        stock_empty_name = StockEntity(symbol=symbol, company_name=empty_name)
        assert stock_empty_name.symbol == symbol
        assert stock_empty_name.company_name.value == ""

        stock_whitespace_name = StockEntity(symbol=symbol, company_name=whitespace_name)
        assert stock_whitespace_name.symbol == symbol
        assert stock_whitespace_name.company_name.value == ""  # Whitespace is stripped

    def test_create_stock_with_optional_none_values(self) -> None:
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

    def test_stock_hash(self) -> None:
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

    def test_stock_string_representation(self) -> None:
        """Should have meaningful string representation."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        stock = StockEntity(symbol=symbol, company_name=company_name)

        assert str(stock) == "AAPL - Apple Inc."

    def test_stock_repr(self) -> None:
        """Should have detailed repr representation."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        grade = Grade("A")
        stock = StockEntity(symbol=symbol, company_name=company_name, grade=grade)

        expected = "StockEntity(symbol=StockSymbol('AAPL'), company_name=CompanyName('Apple Inc.'), grade=Grade('A'))"
        assert repr(stock) == expected

    def test_calculate_position_value(self) -> None:
        """Should calculate total position value."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        stock = StockEntity(symbol=symbol, company_name=company_name)

        quantity = Quantity(100)
        price = Money("150.50")

        total_value = stock.calculate_position_value(quantity, price)

        assert total_value == Money("15050.00")
        assert isinstance(total_value, Money)

    def test_calculate_position_value_with_zero_quantity(self) -> None:
        """Should handle zero quantity gracefully."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        stock = StockEntity(symbol=symbol, company_name=company_name)

        # Zero quantities are allowed
        quantity = Quantity(0)
        price = Money("150.50")

        total_value = stock.calculate_position_value(quantity, price)
        assert total_value == Money("0.00")

    def test_has_notes(self) -> None:
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

    def test_update_fields_single_field(self) -> None:
        """Should update individual fields using update_fields method."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        grade = Grade("B")
        stock = StockEntity(symbol=symbol, company_name=company_name, grade=grade)

        # Update grade
        stock.update_fields(grade="A")
        assert stock.grade is not None
        assert stock.grade.value == "A"

        # Update name
        stock.update_fields(name="Apple Inc. Updated")
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

    def test_update_fields_multiple_fields_atomic(self) -> None:
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
        stock = StockEntity(symbol=symbol, company_name=company_name, grade=grade)

        # Try to update with invalid grade - should fail and rollback all
        with pytest.raises(ValueError, match="Grade must be one of"):
            stock.update_fields(
                name="Apple Inc. Updated", grade="Z", notes="New notes"  # Invalid grade
            )

        # Original values should be unchanged
        assert stock.company_name.value == "Apple Inc."
        assert stock.grade is not None
        assert stock.grade.value == "B"
        assert stock.notes.value == ""

    def test_update_fields_with_too_long_values_raises_error(self) -> None:
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

    def test_create_stock_with_id(self) -> None:
        """Should create stock with provided ID."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        test_id = "stock-id-123"
        stock = StockEntity(symbol=symbol, company_name=company_name, id=test_id)

        assert stock.id == test_id

    def test_stock_id_immutability(self) -> None:
        """Should not be able to change ID after creation."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        stock = StockEntity(symbol=symbol, company_name=company_name, id="test-id-1")

        # ID property should not have a setter
        with pytest.raises(AttributeError):
            stock.id = "different-id"  # type: ignore[misc]

    def test_stock_from_persistence(self) -> None:
        """Should create stock from persistence with existing ID."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        test_id = "persistence-id-456"

        stock = StockEntity.from_persistence(
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

        stock = StockEntity(
            symbol=symbol,
            company_name=company_name,
            sector=sector,
            industry_group=industry_group,
            grade=grade,
        )

        assert stock.symbol == symbol
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

        stock = StockEntity(symbol=symbol, company_name=company_name, sector=sector)

        assert stock.symbol == symbol
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
            _ = StockEntity(
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
            _ = StockEntity(
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
        stock = StockEntity(symbol=symbol, company_name=company_name)

        stock.update_fields(sector="Technology")
        assert stock.sector is not None
        assert stock.sector.value == "Technology"
        assert stock.industry_group is None

    def test_update_fields_sector_and_industry_group(self) -> None:
        """Should update both sector and industry_group when valid combination."""
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        stock = StockEntity(symbol=symbol, company_name=company_name)

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
        stock = StockEntity(symbol=symbol, company_name=company_name, sector=sector)

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

        stock = StockEntity(
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
        stock = StockEntity(symbol=symbol, company_name=company_name)

        with pytest.raises(
            ValueError, match="Sector must be provided when industry_group is specified"
        ):
            stock.update_fields(industry_group="Software")


class TestStockEntityLifecycle:
    """Test stock entity lifecycle management and state transitions."""

    def test_stock_creation_lifecycle(self) -> None:
        """Should properly initialize stock through entire creation lifecycle."""
        # Step 1: Create with minimal required data
        symbol = StockSymbol("AAPL")
        company_name = CompanyName("Apple Inc.")
        stock = StockEntity(symbol=symbol, company_name=company_name)

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
        stock = StockEntity(
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
        assert stock.company_name.value == "Apple Inc. (Updated)"

    def test_stock_persistence_roundtrip(self) -> None:
        """Should maintain data integrity through persistence operations."""
        # Create stock with full data
        original_stock = StockEntity(
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
            "company_name": original_stock.company_name.value,
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
        restored_stock = StockEntity.from_persistence(
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

        stock = StockEntity(symbol=symbol, company_name=company_name, sector=sector)

        # Verify that getting value objects returns the same instances
        retrieved_symbol = stock.symbol
        retrieved_sector = stock.sector

        assert retrieved_symbol is symbol  # Same object reference
        assert retrieved_sector is sector  # Same object reference

        # Verify that value objects are immutable
        with pytest.raises(AttributeError):
            retrieved_symbol.value = "CHANGED"  # type: ignore[misc]


class TestStockEntityDomainInvariants:
    """Test domain business rules and invariants enforcement."""

    def test_symbol_uniqueness_invariant(self) -> None:
        """Should enforce symbol uniqueness business rule conceptually."""
        # Note: This tests the entity design, actual uniqueness enforcement
        # would be at repository level

        symbol = StockSymbol("AAPL")
        name1 = CompanyName("Apple Inc.")
        name2 = CompanyName("Different Company")

        stock1 = StockEntity(symbol=symbol, company_name=name1)
        stock2 = StockEntity(symbol=symbol, company_name=name2)

        # Both stocks have same symbol, so they should be equal by business key
        assert stock1 == stock2
        assert hash(stock1) == hash(stock2)

        # This demonstrates why repository must enforce uniqueness
        stock_set = {stock1, stock2}
        assert len(stock_set) == 1  # Only one stock per symbol

    def test_sector_industry_consistency_invariant(self) -> None:
        """Should enforce sector-industry group consistency at all times."""
        stock = StockEntity(
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
        stock = StockEntity(
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

        stock = StockEntity(symbol=symbol, company_name=company_name)

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


class TestStockEntityBusinessOperations:
    """Test business operations and calculations performed by stock entity."""

    def test_position_value_calculation_accuracy(self) -> None:
        """Should calculate position values with financial precision."""
        stock = StockEntity(
            symbol=StockSymbol("AAPL"), company_name=CompanyName("Apple Inc.")
        )

        # Test various quantity and price combinations
        test_cases = [
            (Quantity(100), Money("150.50"), Money("15050.00")),
            (Quantity(33), Money("99.99"), Money("3299.67")),
            (Quantity(1000), Money("0.01"), Money("10.00")),  # Penny stock
            (Quantity(1), Money("9999.99"), Money("9999.99")),  # Expensive stock
            (Quantity(0), Money("150.50"), Money("0.00")),  # Zero quantity
        ]

        for quantity, price, expected_value in test_cases:
            calculated_value = stock.calculate_position_value(quantity, price)
            assert calculated_value == expected_value
            assert isinstance(calculated_value, Money)

    def test_position_value_calculation_edge_cases(self) -> None:
        """Should handle edge cases in position value calculations."""
        stock = StockEntity(
            symbol=StockSymbol("EDGE"), company_name=CompanyName("Edge Case Corp")
        )

        # Very small quantities (fractional shares)
        fractional_value = stock.calculate_position_value(
            Quantity(0.1), Money("1000.00")
        )
        assert fractional_value == Money("100.00")

        # Very large quantities
        large_value = stock.calculate_position_value(Quantity(1000000), Money("0.01"))
        assert large_value == Money("10000.00")

        # Very precise prices
        precise_value = stock.calculate_position_value(Quantity(3), Money("33.333333"))
        assert precise_value == Money("99.99")  # 33.333333 * 3 = 99.999999 -> 99.99

    def test_stock_business_logic_methods(self) -> None:
        """Should provide meaningful business logic methods."""
        # Stock with notes
        stock_with_notes = StockEntity(
            symbol=StockSymbol("NOTED"),
            company_name=CompanyName("Well Documented Corp"),
            notes=Notes("Has detailed analysis notes"),
        )
        assert stock_with_notes.has_notes() is True

        # Stock without notes
        stock_without_notes = StockEntity(
            symbol=StockSymbol("BARE"), company_name=CompanyName("Minimal Corp")
        )
        assert stock_without_notes.has_notes() is False

        # Stock with empty notes
        stock_empty_notes = StockEntity(
            symbol=StockSymbol("EMPTY"),
            company_name=CompanyName("Empty Notes Corp"),
            notes=Notes(""),
        )
        assert stock_empty_notes.has_notes() is False


class TestStockEntityConcurrencyScenarios:
    """Test scenarios that might occur in concurrent/multi-user environments."""

    def test_stock_update_idempotency(self) -> None:
        """Should handle repeated identical updates gracefully."""
        stock = StockEntity(
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
        stock = StockEntity(
            symbol=StockSymbol("ROBST"),
            company_name=CompanyName("Robust Corp"),
            sector=Sector("Technology"),
            industry_group=IndustryGroup("Software"),
            grade=Grade("A"),
            notes=Notes("Initial notes"),
        )

        # Capture original state
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
        assert stock.company_name.value == original_name
        assert stock.sector is not None
        assert stock.sector.value == original_sector
        assert stock.industry_group is not None
        assert stock.industry_group.value == original_industry
        assert stock.grade is not None
        assert stock.grade.value == original_grade
        assert stock.notes.value == original_notes

    def test_stock_entity_collection_operations(self) -> None:
        """Should work properly in collections (sets, dicts) for business operations."""
        # Create stocks that should be considered equal and different
        aapl1 = StockEntity(
            symbol=StockSymbol("AAPL"),
            company_name=CompanyName("Apple Inc."),
            grade=Grade("A"),
        )

        aapl2 = StockEntity(
            symbol=StockSymbol("AAPL"),
            company_name=CompanyName("Apple Inc."),
            grade=Grade("B"),  # Different grade, same symbol
        )

        msft = StockEntity(
            symbol=StockSymbol("MSFT"), company_name=CompanyName("Microsoft Corp")
        )

        # Test set operations (should deduplicate by symbol)
        stock_set = {aapl1, aapl2, msft}
        assert len(stock_set) == 2  # AAPL appears once, MSFT once

        # Test dictionary operations (stock as key)
        portfolio_weights = {aapl1: 0.6, msft: 0.4}

        # Should be able to retrieve using different AAPL instance with same symbol
        assert portfolio_weights[aapl2] == 0.6  # aapl2 should map to same key as aapl1
        assert portfolio_weights[msft] == 0.4

    def test_stock_equality_with_non_stock_object(self) -> None:
        """Test that stock equality returns False for non-StockEntity objects."""
        stock = StockEntity(
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
