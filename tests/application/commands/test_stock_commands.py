"""
Tests for stock-related command objects.

Following TDD approach - these tests define the expected behavior
of command objects used for stock operations.
"""

import pytest
from application.commands.stock_commands import CreateStockCommand


class TestCreateStockCommand:
    """Test suite for CreateStockCommand."""

    def test_create_stock_command_with_valid_data(self):
        """Should create command with valid stock data."""
        command = CreateStockCommand(
            symbol="AAPL",
            name="Apple Inc.",
            industry_group="Technology",
            grade="A",
            notes="Excellent company",
        )

        assert command.symbol == "AAPL"
        assert command.name == "Apple Inc."
        assert command.industry_group == "Technology"
        assert command.grade == "A"
        assert command.notes == "Excellent company"

    def test_create_stock_command_with_minimal_data(self):
        """Should create command with only required fields."""
        command = CreateStockCommand(symbol="MSFT", name="Microsoft Corp.")

        assert command.symbol == "MSFT"
        assert command.name == "Microsoft Corp."
        assert command.industry_group is None
        assert command.grade is None
        assert command.notes == ""

    def test_create_stock_command_normalizes_symbol(self):
        """Should normalize symbol to uppercase."""
        command = CreateStockCommand(symbol="aapl", name="Apple Inc.")

        assert command.symbol == "AAPL"

    def test_create_stock_command_strips_whitespace(self):
        """Should strip whitespace from fields."""
        command = CreateStockCommand(
            symbol="  AAPL  ",
            name="  Apple Inc.  ",
            industry_group="  Technology  ",
            notes="  Great company  ",
        )

        assert command.symbol == "AAPL"
        assert command.name == "Apple Inc."
        assert command.industry_group == "Technology"
        assert command.notes == "Great company"

    def test_create_stock_command_with_empty_symbol_raises_error(self):
        """Should raise error for empty symbol."""
        with pytest.raises(ValueError, match="Symbol cannot be empty"):
            CreateStockCommand(symbol="", name="Apple Inc.")

    def test_create_stock_command_with_empty_name_raises_error(self):
        """Should raise error for empty name."""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            CreateStockCommand(symbol="AAPL", name="")

    def test_create_stock_command_with_invalid_symbol_raises_error(self):
        """Should raise error for invalid symbol format."""
        with pytest.raises(ValueError, match="Invalid symbol format"):
            CreateStockCommand(symbol="AAPL123", name="Apple Inc.")

    def test_create_stock_command_with_invalid_grade_raises_error(self):
        """Should raise error for invalid grade."""
        with pytest.raises(ValueError, match="Invalid grade"):
            CreateStockCommand(symbol="AAPL", name="Apple Inc.", grade="Z")

    def test_create_stock_command_equality(self):
        """Should compare commands for equality."""
        command1 = CreateStockCommand(symbol="AAPL", name="Apple Inc.")
        command2 = CreateStockCommand(symbol="AAPL", name="Apple Inc.")
        command3 = CreateStockCommand(symbol="MSFT", name="Microsoft")

        assert command1 == command2
        assert command1 != command3

    def test_create_stock_command_string_representation(self):
        """Should have meaningful string representation."""
        command = CreateStockCommand(symbol="AAPL", name="Apple Inc.")

        str_repr = str(command)
        assert "CreateStockCommand" in str_repr
        assert "AAPL" in str_repr
        assert "Apple Inc." in str_repr

    def test_create_stock_command_is_immutable(self):
        """Command should be immutable after creation."""
        command = CreateStockCommand(symbol="AAPL", name="Apple Inc.")

        with pytest.raises(AttributeError):
            command.symbol = "MSFT"

        with pytest.raises(AttributeError):
            command.name = "Microsoft"
