"""
Tests for CreateStockCommand.

Following TDD approach - these tests define the expected behavior
of the CreateStockCommand used for stock creation operations.
"""

import pytest

from src.application.commands.stock import CreateStockCommand, CreateStockInputs


class TestCreateStockCommand:
    """Test suite for CreateStockCommand."""

    def test_create_stock_command_with_valid_data(self) -> None:
        """Should create command with valid stock data."""
        inputs = CreateStockInputs(
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="Excellent company",
        )
        command = CreateStockCommand(inputs)

        assert command.symbol == "AAPL"
        assert command.name == "Apple Inc."
        assert command.sector == "Technology"
        assert command.industry_group == "Software"
        assert command.grade == "A"
        assert command.notes == "Excellent company"

    def test_create_stock_command_with_minimal_data(self) -> None:
        """Should create command with only required fields."""
        inputs = CreateStockInputs(symbol="MSFT")
        command = CreateStockCommand(inputs)

        assert command.symbol == "MSFT"
        assert command.name is None
        assert command.industry_group is None
        assert command.grade is None
        assert command.notes == ""

    def test_create_stock_command_with_name(self) -> None:
        """Should create command with symbol and name."""
        inputs = CreateStockInputs(symbol="MSFT", name="Microsoft Corp.")
        command = CreateStockCommand(inputs)

        assert command.symbol == "MSFT"
        assert command.name == "Microsoft Corp."
        assert command.industry_group is None
        assert command.grade is None
        assert command.notes == ""

    def test_create_stock_command_normalizes_symbol(self) -> None:
        """Should normalize symbol to uppercase."""
        inputs = CreateStockInputs(symbol="aapl", name="Apple Inc.")
        command = CreateStockCommand(inputs)

        assert command.symbol == "AAPL"

    def test_create_stock_command_strips_whitespace(self) -> None:
        """Should strip whitespace from fields."""
        inputs = CreateStockInputs(
            symbol="  AAPL  ",
            name="  Apple Inc.  ",
            sector="  Technology  ",
            industry_group="  Software  ",
            notes="  Great company  ",
        )
        command = CreateStockCommand(inputs)

        assert command.symbol == "AAPL"
        assert command.name == "Apple Inc."
        assert command.sector == "Technology"
        assert command.industry_group == "Software"
        assert command.notes == "Great company"

    def test_create_stock_command_with_empty_symbol_raises_error(self) -> None:
        """Should raise error for empty symbol."""
        with pytest.raises(ValueError, match="Symbol cannot be empty"):
            inputs = CreateStockInputs(symbol="", name="Apple Inc.")
            _ = CreateStockCommand(inputs)

    def test_create_stock_command_with_empty_name_allowed(self) -> None:
        """Should allow empty name as it's optional."""
        inputs = CreateStockInputs(symbol="AAPL", name="")
        command = CreateStockCommand(inputs)
        assert command.name is None  # Empty string normalized to None

    def test_create_stock_command_with_invalid_symbol_raises_error(self) -> None:
        """Should raise error for invalid symbol format."""
        with pytest.raises(ValueError, match="Invalid symbol format"):
            inputs = CreateStockInputs(symbol="AAPL123", name="Apple Inc.")
            _ = CreateStockCommand(inputs)

    def test_create_stock_command_with_invalid_grade_raises_error(self) -> None:
        """Should raise error for invalid grade."""
        with pytest.raises(ValueError, match="Invalid grade"):
            inputs = CreateStockInputs(symbol="AAPL", name="Apple Inc.", grade="Z")
            _ = CreateStockCommand(inputs)

    def test_create_stock_command_equality(self) -> None:
        """Should compare commands for equality."""
        inputs1 = CreateStockInputs(symbol="AAPL", name="Apple Inc.")
        inputs2 = CreateStockInputs(symbol="AAPL", name="Apple Inc.")
        inputs3 = CreateStockInputs(symbol="MSFT", name="Microsoft")
        command1 = CreateStockCommand(inputs1)
        command2 = CreateStockCommand(inputs2)
        command3 = CreateStockCommand(inputs3)

        assert command1 == command2
        assert command1 != command3

    def test_create_stock_command_string_representation(self) -> None:
        """Should have meaningful string representation."""
        inputs = CreateStockInputs(symbol="AAPL", name="Apple Inc.")
        command = CreateStockCommand(inputs)

        str_repr = str(command)
        assert "CreateStockCommand" in str_repr
        assert "AAPL" in str_repr
        assert "Apple Inc." in str_repr

    def test_create_stock_command_is_immutable(self) -> None:
        """Command should be immutable after creation."""
        inputs = CreateStockInputs(symbol="AAPL", name="Apple Inc.")
        command = CreateStockCommand(inputs)

        with pytest.raises(AttributeError):
            command.symbol = "MSFT"  # type: ignore[misc]

        with pytest.raises(AttributeError):
            command.name = "Microsoft"  # type: ignore[misc]

    def test_create_stock_command_equality_with_non_matching_types(self) -> None:
        """Should return False when compared with non-command objects."""
        inputs = CreateStockInputs(symbol="AAPL", name="Apple Inc.")
        command = CreateStockCommand(inputs)

        # Test against different types - covers hash function and equality branches
        assert command != "string"
        assert command != 123
        assert command is not None
        assert command != {"symbol": "AAPL"}

        # Test hash function is called when using in sets
        command_set = {command}
        assert len(command_set) == 1

    def test_create_stock_command_industry_group_without_sector_error(self) -> None:
        """Should raise ValueError when industry_group provided without sector."""
        with pytest.raises(
            ValueError, match="Sector must be provided when industry_group is specified"
        ):
            inputs = CreateStockInputs(
                symbol="AAPL",
                name="Apple Inc.",
                industry_group="Software",  # No sector provided
            )
            _ = CreateStockCommand(inputs)

    def test_create_stock_command_repr_representation(self) -> None:
        """Should have meaningful repr representation."""
        inputs = CreateStockInputs(
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="Great company",
        )
        command = CreateStockCommand(inputs)

        repr_str = repr(command)
        assert "CreateStockCommand" in repr_str
        assert "symbol='AAPL'" in repr_str
        assert "name='Apple Inc.'" in repr_str
        assert "sector='Technology'" in repr_str
        assert "industry_group='Software'" in repr_str
        assert "grade='A'" in repr_str
        assert "notes='Great company'" in repr_str

    def test_create_stock_command_normalize_empty_sector_and_industry(self) -> None:
        """Should normalize empty strings to None for optional fields."""
        inputs = CreateStockInputs(
            symbol="AAPL",
            name="Apple Inc.",
            sector="",  # Empty string should become None
            industry_group="",  # Empty string should become None
        )
        command = CreateStockCommand(inputs)

        assert command.sector is None
        assert command.industry_group is None

    def test_create_stock_command_normalize_whitespace_only_optional_fields(
        self,
    ) -> None:
        """Should normalize whitespace-only strings to None for optional fields."""
        inputs = CreateStockInputs(
            symbol="AAPL",
            name="Apple Inc.",
            sector="   ",  # Whitespace-only should become None
            industry_group="   ",  # Whitespace-only should become None
        )
        command = CreateStockCommand(inputs)

        assert command.sector is None
        assert command.industry_group is None

    def test_create_stock_command_with_valid_sector_industry_combination(self) -> None:
        """Should accept valid sector-industry combinations."""
        # This tests the domain service validation path
        inputs = CreateStockInputs(
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",  # Valid combination
        )
        command = CreateStockCommand(inputs)

        assert command.sector == "Technology"
        assert command.industry_group == "Software"

    def test_create_stock_command_with_invalid_sector_industry_combination(
        self,
    ) -> None:
        """Should raise error for invalid sector-industry combinations."""
        # This should trigger the domain service validation
        with pytest.raises(ValueError):
            inputs = CreateStockInputs(
                symbol="AAPL",
                name="Apple Inc.",
                sector="Technology",
                industry_group="Banking",  # Invalid combination
            )
            _ = CreateStockCommand(inputs)

    def test_create_stock_command_grade_validation_valid_grades(self) -> None:
        """Should accept all valid grades."""
        for grade in ["A", "B", "C"]:
            inputs = CreateStockInputs(
                symbol="TEST",
                name="Test Company",
                grade=grade,
            )
            command = CreateStockCommand(inputs)
            assert command.grade == grade

    def test_create_stock_command_grade_validation_none_grade(self) -> None:
        """Should accept None grade."""
        inputs = CreateStockInputs(
            symbol="TEST",
            name="Test Company",
            grade=None,
        )
        command = CreateStockCommand(inputs)
        assert command.grade is None

    def test_create_stock_command_base_class_coverage(self) -> None:
        """Test base class coverage for CreateStockCommand missing lines."""
        # Test that normal initialization works (covers line 94 - super().__setattr__)
        inputs = CreateStockInputs(symbol="AAPL", name="Apple Inc.")
        command = CreateStockCommand(inputs)
        assert command.symbol == "AAPL"
        assert command.name == "Apple Inc."

        # The __setattr__ is called during initialization to set internal attributes
        # This test ensures the initialization path is covered

    def test_create_stock_command_setattr_during_initialization(self) -> None:
        """Test that __setattr__ allows setting attributes during initialization."""
        # During initialization, __setattr__ should allow setting attributes
        # This specifically tests the super().__setattr__ branch (line 94)

        # Create a partially initialized object to test __setattr__ behavior
        # We'll use object.__new__ to create an instance without calling __init__
        command = object.__new__(CreateStockCommand)

        # At this point, the object has no _symbol attribute, so __setattr__ should work
        # This directly exercises the super().__setattr__ branch
        command.test_attr = "test_value"

        # Now properly initialize the object
        inputs = CreateStockInputs(
            symbol="MSFT",
            name="Microsoft Corporation",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="Leading software company",
        )
        CreateStockCommand.__init__(command, inputs)

        # Verify all attributes were set correctly
        assert command.symbol == "MSFT"
        assert command.name == "Microsoft Corporation"
        assert command.sector == "Technology"
        assert command.industry_group == "Software"
        assert command.grade == "A"
        assert command.notes == "Leading software company"
