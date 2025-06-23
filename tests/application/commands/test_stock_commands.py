"""
Tests for stock-related command objects.

Following TDD approach - these tests define the expected behavior
of command objects used for stock operations.
"""

import pytest

from src.application.commands.stock_commands import (
    CreateStockCommand,
    UpdateStockCommand,
)


class TestCreateStockCommand:
    """Test suite for CreateStockCommand."""

    def test_create_stock_command_with_valid_data(self) -> None:
        """Should create command with valid stock data."""
        command = CreateStockCommand(
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="Excellent company",
        )

        assert command.symbol == "AAPL"
        assert command.name == "Apple Inc."
        assert command.sector == "Technology"
        assert command.industry_group == "Software"
        assert command.grade == "A"
        assert command.notes == "Excellent company"

    def test_create_stock_command_with_minimal_data(self) -> None:
        """Should create command with only required fields."""
        command = CreateStockCommand(symbol="MSFT", name="Microsoft Corp.")

        assert command.symbol == "MSFT"
        assert command.name == "Microsoft Corp."
        assert command.industry_group is None
        assert command.grade is None
        assert command.notes == ""

    def test_create_stock_command_normalizes_symbol(self) -> None:
        """Should normalize symbol to uppercase."""
        command = CreateStockCommand(symbol="aapl", name="Apple Inc.")

        assert command.symbol == "AAPL"

    def test_create_stock_command_strips_whitespace(self) -> None:
        """Should strip whitespace from fields."""
        command = CreateStockCommand(
            symbol="  AAPL  ",
            name="  Apple Inc.  ",
            sector="  Technology  ",
            industry_group="  Software  ",
            notes="  Great company  ",
        )

        assert command.symbol == "AAPL"
        assert command.name == "Apple Inc."
        assert command.sector == "Technology"
        assert command.industry_group == "Software"
        assert command.notes == "Great company"

    def test_create_stock_command_with_empty_symbol_raises_error(self) -> None:
        """Should raise error for empty symbol."""
        with pytest.raises(ValueError, match="Symbol cannot be empty"):
            _ = CreateStockCommand(symbol="", name="Apple Inc.")

    def test_create_stock_command_with_empty_name_raises_error(self) -> None:
        """Should raise error for empty name."""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            _ = CreateStockCommand(symbol="AAPL", name="")

    def test_create_stock_command_with_invalid_symbol_raises_error(self) -> None:
        """Should raise error for invalid symbol format."""
        with pytest.raises(ValueError, match="Invalid symbol format"):
            _ = CreateStockCommand(symbol="AAPL123", name="Apple Inc.")

    def test_create_stock_command_with_invalid_grade_raises_error(self) -> None:
        """Should raise error for invalid grade."""
        with pytest.raises(ValueError, match="Invalid grade"):
            _ = CreateStockCommand(symbol="AAPL", name="Apple Inc.", grade="Z")

    def test_create_stock_command_equality(self) -> None:
        """Should compare commands for equality."""
        command1 = CreateStockCommand(symbol="AAPL", name="Apple Inc.")
        command2 = CreateStockCommand(symbol="AAPL", name="Apple Inc.")
        command3 = CreateStockCommand(symbol="MSFT", name="Microsoft")

        assert command1 == command2
        assert command1 != command3

    def test_create_stock_command_string_representation(self) -> None:
        """Should have meaningful string representation."""
        command = CreateStockCommand(symbol="AAPL", name="Apple Inc.")

        str_repr = str(command)
        assert "CreateStockCommand" in str_repr
        assert "AAPL" in str_repr
        assert "Apple Inc." in str_repr

    def test_create_stock_command_is_immutable(self) -> None:
        """Command should be immutable after creation."""
        command = CreateStockCommand(symbol="AAPL", name="Apple Inc.")

        with pytest.raises(AttributeError):
            command.symbol = "MSFT"  # type: ignore[misc]

        with pytest.raises(AttributeError):
            command.name = "Microsoft"  # type: ignore[misc]

    def test_create_stock_command_equality_with_non_matching_types(self) -> None:
        """Should return False when compared with non-command objects."""
        command = CreateStockCommand(symbol="AAPL", name="Apple Inc.")

        # Test against different types - covers hash function and equality branches
        assert command != "string"
        assert command != 123
        assert command != None
        assert command != {"symbol": "AAPL"}

        # Test hash function is called when using in sets
        command_set = {command}
        assert len(command_set) == 1

    def test_create_stock_command_industry_group_without_sector_error(self) -> None:
        """Should raise ValueError when industry_group provided without sector."""
        with pytest.raises(
            ValueError, match="Sector must be provided when industry_group is specified"
        ):
            _ = CreateStockCommand(
                symbol="AAPL",
                name="Apple Inc.",
                industry_group="Software",  # No sector provided
            )


class TestUpdateStockCommand:
    """Test suite for UpdateStockCommand."""

    def test_update_stock_command_with_valid_data(self) -> None:
        """Should create command with valid update data."""
        command = UpdateStockCommand(
            stock_id="test-stock-1",
            name="Apple Inc. (Updated)",
            industry_group="Technology",
            grade="A",
            notes="Updated notes",
        )

        assert command.stock_id == "test-stock-1"
        assert command.name == "Apple Inc. (Updated)"
        assert command.industry_group == "Technology"
        assert command.grade == "A"
        assert command.notes == "Updated notes"

    def test_update_stock_command_with_partial_data(self) -> None:
        """Should create command with only some fields to update."""
        command = UpdateStockCommand(
            stock_id="test-stock-1",
            grade="B",
            notes="Updated notes only",
        )

        assert command.stock_id == "test-stock-1"
        assert command.name is None
        assert command.industry_group is None
        assert command.grade == "B"
        assert command.notes == "Updated notes only"

    def test_update_stock_command_strips_whitespace(self) -> None:
        """Should strip whitespace from fields."""
        command = UpdateStockCommand(
            stock_id="test-stock-1",
            name="  Apple Inc.  ",
            industry_group="  Technology  ",
            notes="  Updated notes  ",
        )

        assert command.name == "Apple Inc."
        assert command.industry_group == "Technology"
        assert command.notes == "Updated notes"

    def test_update_stock_command_with_empty_string_sets_none(self) -> None:
        """Should convert empty strings to None for optional fields."""
        command = UpdateStockCommand(
            stock_id="test-stock-1",
            name="Apple Inc.",
            industry_group="",
            notes="",
        )

        assert command.name == "Apple Inc."
        assert command.industry_group is None
        assert command.notes == ""  # Notes should be empty string, not None

    def test_update_stock_command_with_invalid_stock_id_raises_error(self) -> None:
        """Should raise error for invalid stock ID."""
        with pytest.raises(ValueError, match="Stock ID must be a non-empty string"):
            _ = UpdateStockCommand(stock_id="")

        with pytest.raises(ValueError, match="Stock ID must be a non-empty string"):
            _ = UpdateStockCommand(stock_id="   ")  # whitespace-only string

    def test_update_stock_command_with_invalid_grade_raises_error(self) -> None:
        """Should raise error for invalid grade."""
        with pytest.raises(ValueError, match="Invalid grade"):
            _ = UpdateStockCommand(stock_id="test-stock-1", grade="Z")

    def test_update_stock_command_with_empty_name_raises_error(self) -> None:
        """Should raise error for empty name."""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            _ = UpdateStockCommand(stock_id="test-stock-1", name="")

        with pytest.raises(ValueError, match="Name cannot be empty"):
            _ = UpdateStockCommand(stock_id="test-stock-1", name="   ")

    def test_update_stock_command_equality(self) -> None:
        """Should compare commands for equality."""
        command1 = UpdateStockCommand(stock_id="test-stock-1", grade="A")
        command2 = UpdateStockCommand(stock_id="test-stock-1", grade="A")
        command3 = UpdateStockCommand(stock_id="test-stock-2", grade="A")

        assert command1 == command2
        assert command1 != command3

    def test_update_stock_command_string_representation(self) -> None:
        """Should have meaningful string representation."""
        command = UpdateStockCommand(stock_id="test-stock-1", grade="A")

        str_repr = str(command)
        assert "UpdateStockCommand" in str_repr
        assert "stock_id=test-stock-1" in str_repr

    def test_update_stock_command_is_immutable(self) -> None:
        """Command should be immutable after creation."""
        command = UpdateStockCommand(stock_id="test-stock-1", grade="A")

        with pytest.raises(AttributeError):
            command.stock_id = "different-id"  # type: ignore[misc]

        with pytest.raises(AttributeError):
            command.grade = "B"  # type: ignore[misc]

    def test_update_stock_command_has_no_updates_when_all_fields_none(self) -> None:
        """Should detect when no fields are being updated."""
        command = UpdateStockCommand(stock_id="test-stock-1")

        assert not command.has_updates()

    def test_update_stock_command_has_updates_when_fields_provided(self) -> None:
        """Should detect when fields are being updated."""
        command = UpdateStockCommand(stock_id="test-stock-1", grade="A")

        assert command.has_updates()

    def test_update_stock_command_get_update_fields(self) -> None:
        """Should return only fields that are being updated."""
        command = UpdateStockCommand(
            stock_id="test-stock-1",
            name="Apple Inc.",
            grade="A",
        )

        fields = command.get_update_fields()
        assert "name" in fields
        assert "grade" in fields
        assert "industry_group" not in fields
        assert "notes" not in fields
        assert fields["name"] == "Apple Inc."
        assert fields["grade"] == "A"

    def test_update_stock_command_equality_with_non_matching_types(self) -> None:
        """Should return False when compared with non-command objects."""
        command = UpdateStockCommand(stock_id="test-stock-1", grade="A")

        # Test against different types - covers hash function and equality branches
        assert command != "string"
        assert command != 123
        assert command != None
        assert command != {"stock_id": "test-stock-1"}

        # Test hash function is called when using in sets
        command_set = {command}
        assert len(command_set) == 1

    def test_update_stock_command_sector_property_getter(self) -> None:
        """Should return sector value through property getter."""
        command = UpdateStockCommand(stock_id="test-stock-1", sector="Technology")

        # Test sector property getter
        assert command.sector == "Technology"

        # Test None case
        command_no_sector = UpdateStockCommand(stock_id="test-stock-1")
        assert command_no_sector.sector is None

    def test_update_stock_command_normalize_sector_none_case(self) -> None:
        """Should handle None sector normalization correctly."""
        # Test the None case in _normalize_sector method
        command = UpdateStockCommand(stock_id="test-stock-1", sector=None)

        assert command.sector is None

    def test_update_stock_command_with_explicit_none_sector(self) -> None:
        """Should handle explicitly passed None sector."""
        # This tests the return None branch in _normalize_sector
        command = UpdateStockCommand(
            stock_id="test-stock-1",
            name="Test Company",
            sector=None,  # Explicitly None
            grade="A",
        )

        assert command.sector is None
        assert command.name == "Test Company"
        assert command.grade == "A"
