"""
Tests for stock-related command objects.

Following TDD approach - these tests define the expected behavior
of command objects used for stock operations.
"""

import pytest

from src.application.commands.stock import (
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
        command = CreateStockCommand(symbol="MSFT")

        assert command.symbol == "MSFT"
        assert command.name is None
        assert command.industry_group is None
        assert command.grade is None
        assert command.notes == ""

    def test_create_stock_command_with_name(self) -> None:
        """Should create command with symbol and name."""
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

    def test_create_stock_command_with_empty_name_allowed(self) -> None:
        """Should allow empty name as it's optional."""
        command = CreateStockCommand(symbol="AAPL", name="")
        assert command.name is None  # Empty string normalized to None

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
            _ = CreateStockCommand(
                symbol="AAPL",
                name="Apple Inc.",
                industry_group="Software",  # No sector provided
            )

    def test_create_stock_command_repr_representation(self) -> None:
        """Should have meaningful repr representation."""
        command = CreateStockCommand(
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="Great company",
        )

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
        command = CreateStockCommand(
            symbol="AAPL",
            name="Apple Inc.",
            sector="",  # Empty string should become None
            industry_group="",  # Empty string should become None
        )

        assert command.sector is None
        assert command.industry_group is None

    def test_create_stock_command_normalize_whitespace_only_optional_fields(
        self,
    ) -> None:
        """Should normalize whitespace-only strings to None for optional fields."""
        command = CreateStockCommand(
            symbol="AAPL",
            name="Apple Inc.",
            sector="   ",  # Whitespace-only should become None
            industry_group="   ",  # Whitespace-only should become None
        )

        assert command.sector is None
        assert command.industry_group is None

    def test_create_stock_command_with_valid_sector_industry_combination(self) -> None:
        """Should accept valid sector-industry combinations."""
        # This tests the domain service validation path
        command = CreateStockCommand(
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",  # Valid combination
        )

        assert command.sector == "Technology"
        assert command.industry_group == "Software"

    def test_create_stock_command_with_invalid_sector_industry_combination(
        self,
    ) -> None:
        """Should raise error for invalid sector-industry combinations."""
        # This should trigger the domain service validation
        with pytest.raises(ValueError):
            _ = CreateStockCommand(
                symbol="AAPL",
                name="Apple Inc.",
                sector="Technology",
                industry_group="Banking",  # Invalid combination
            )

    def test_create_stock_command_grade_validation_valid_grades(self) -> None:
        """Should accept all valid grades."""
        for grade in ["A", "B", "C"]:
            command = CreateStockCommand(
                symbol="TEST",
                name="Test Company",
                grade=grade,
            )
            assert command.grade == grade

    def test_create_stock_command_grade_validation_none_grade(self) -> None:
        """Should accept None grade."""
        command = CreateStockCommand(
            symbol="TEST",
            name="Test Company",
            grade=None,
        )
        assert command.grade is None

    def test_create_stock_command_base_class_coverage(self) -> None:
        """Test base class coverage for CreateStockCommand missing lines."""
        # Test that normal initialization works (covers line 94 - super().__setattr__)
        command = CreateStockCommand(symbol="AAPL", name="Apple Inc.")
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
        CreateStockCommand.__init__(
            command,
            symbol="MSFT",
            name="Microsoft Corporation",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="Leading software company",
        )

        # Verify all attributes were set correctly
        assert command.symbol == "MSFT"
        assert command.name == "Microsoft Corporation"
        assert command.sector == "Technology"
        assert command.industry_group == "Software"
        assert command.grade == "A"
        assert command.notes == "Leading software company"


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

    def test_update_stock_command_with_empty_name_allowed(self) -> None:
        """Should allow empty name as it's optional."""
        command = UpdateStockCommand(stock_id="test-stock-1", name="")
        assert command.name is None  # Empty string normalized to None

        command2 = UpdateStockCommand(stock_id="test-stock-1", name="   ")
        assert command2.name is None  # Whitespace normalized to None

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
        assert command is not None
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

    def test_update_stock_command_repr_representation(self) -> None:
        """Should have meaningful repr representation."""
        command = UpdateStockCommand(
            stock_id="test-stock-1",
            name="Apple Inc.",
            industry_group="Software",
            grade="A",
            notes="Updated notes",
        )

        repr_str = repr(command)
        assert "UpdateStockCommand" in repr_str
        assert "stock_id=test-stock-1" in repr_str
        assert "name='Apple Inc.'" in repr_str
        assert "industry_group='Software'" in repr_str
        assert "grade='A'" in repr_str
        assert "notes='Updated notes'" in repr_str

    def test_update_stock_command_hash_consistency(self) -> None:
        """Should be hashable and work in sets/dicts."""
        command1 = UpdateStockCommand(stock_id="test-stock-1", grade="A")
        command2 = UpdateStockCommand(stock_id="test-stock-1", grade="A")

        # Should be able to use in sets
        command_set = {command1, command2}
        assert len(command_set) == 1  # Same data should result in one item

        # Should be able to use as dict keys
        command_dict = {command1: "value"}
        assert command_dict[command2] == "value"  # Same data should work as key

    def test_update_stock_command_equality_with_sector_field(self) -> None:
        """Should test equality with sector field properly included in __eq__."""
        # Test that sector field is properly compared in __eq__ method
        command1 = UpdateStockCommand(stock_id="test-stock-1", sector="Technology")
        command2 = UpdateStockCommand(stock_id="test-stock-1", sector="Healthcare")

        # These should NOT be equal because they have different sectors
        assert command1 != command2

        # Test with same sector - should be equal
        command3 = UpdateStockCommand(stock_id="test-stock-1", sector="Technology")
        assert command1 == command3

        # Test with None sectors - should be equal
        command4 = UpdateStockCommand(stock_id="test-stock-1", sector=None)
        command5 = UpdateStockCommand(stock_id="test-stock-1", sector=None)
        assert command4 == command5

    def test_update_stock_command_whitespace_only_stock_id_validation(self) -> None:
        """Should validate stock_id for whitespace-only strings."""
        with pytest.raises(ValueError, match="Stock ID must be a non-empty string"):
            _ = UpdateStockCommand(stock_id="   ")  # Whitespace-only

    def test_update_stock_command_whitespace_only_name_validation(self) -> None:
        """Should allow whitespace-only name as it's optional."""
        command = UpdateStockCommand(stock_id="test-stock-1", name="   ")
        assert command.name is None  # Whitespace normalized to None

    def test_update_stock_command_industry_group_empty_string_normalization(
        self,
    ) -> None:
        """Should normalize empty industry_group string to None."""
        command = UpdateStockCommand(
            stock_id="test-stock-1",
            industry_group="",  # Empty string
        )

        assert command.industry_group is None

    def test_update_stock_command_industry_group_whitespace_normalization(self) -> None:
        """Should normalize whitespace-only industry_group to None."""
        command = UpdateStockCommand(
            stock_id="test-stock-1",
            industry_group="   ",  # Whitespace-only
        )

        assert command.industry_group is None

    def test_update_stock_command_all_grade_values(self) -> None:
        """Should accept all valid grade values."""
        for grade in ["A", "B", "C", None]:
            command = UpdateStockCommand(
                stock_id="test-stock-1",
                grade=grade,
            )
            assert command.grade == grade

    def test_update_stock_command_get_update_fields_all_fields(self) -> None:
        """Should return all fields when all are provided."""
        command = UpdateStockCommand(
            stock_id="test-stock-1",
            name="Test Company",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="Test notes",
        )

        fields = command.get_update_fields()
        expected_fields = {"name", "sector", "industry_group", "grade", "notes"}
        assert set(fields.keys()) == expected_fields
        assert fields["name"] == "Test Company"
        assert fields["sector"] == "Technology"
        assert fields["industry_group"] == "Software"
        assert fields["grade"] == "A"
        assert fields["notes"] == "Test notes"

    def test_update_stock_command_get_update_fields_empty(self) -> None:
        """Should return empty dict when no fields are provided."""
        command = UpdateStockCommand(stock_id="test-stock-1")

        fields = command.get_update_fields()
        assert not fields

    def test_update_stock_command_has_updates_each_field_individually(self) -> None:
        """Should detect updates for each field individually."""
        # Test each field individually
        fields_to_test = [
            ("name", "Test Company"),
            ("sector", "Technology"),
            ("industry_group", "Software"),
            ("grade", "A"),
            ("notes", "Test notes"),
        ]

        for field_name, field_value in fields_to_test:
            kwargs = {"stock_id": "test-stock-1", field_name: field_value}
            command = UpdateStockCommand(**kwargs)
            assert (
                command.has_updates()
            ), f"Failed to detect update for field {field_name}"

    def test_update_stock_command_with_explicit_none_name(self) -> None:
        """Should handle explicitly passed None name."""
        # This ensures coverage of None branch in _normalize_name
        command = UpdateStockCommand(stock_id="test-stock-1", name=None)
        assert command.name is None

    def test_update_stock_command_base_class_coverage(self) -> None:
        """Test base class coverage for UpdateStockCommand missing lines."""
        # Test that normal initialization works (covers line 378 - super().__setattr__)
        command = UpdateStockCommand(stock_id="test-stock-1", name="Updated Name")
        assert command.stock_id == "test-stock-1"
        assert command.name == "Updated Name"

        # The __setattr__ is called during initialization to set internal attributes
        # This test ensures the initialization path is covered

    def test_update_stock_command_setattr_during_initialization(self) -> None:
        """Test that __setattr__ allows setting attributes during initialization."""
        # During initialization, __setattr__ should allow setting attributes
        # This specifically tests the super().__setattr__ branch (line 378)

        # Create a partially initialized object to test __setattr__ behavior
        # We'll use object.__new__ to create an instance without calling __init__
        command = object.__new__(UpdateStockCommand)

        # At this point, the object has no _stock_id attribute, so __setattr__ should work
        # This directly exercises the super().__setattr__ branch
        command.test_attr = "test_value"

        # Now properly initialize the object
        UpdateStockCommand.__init__(
            command,
            stock_id="test-id-123",
            name="Updated Company Name",
            sector="Healthcare",
            industry_group="Pharmaceuticals",
            grade="B",
            notes="Updated notes with more details",
        )

        # Verify all attributes were set correctly
        assert command.stock_id == "test-id-123"
        assert command.name == "Updated Company Name"
        assert command.sector == "Healthcare"
        assert command.industry_group == "Pharmaceuticals"
        assert command.grade == "B"
        assert command.notes == "Updated notes with more details"

    def test_update_stock_command_with_symbol(self) -> None:
        """Should handle symbol updates."""
        command = UpdateStockCommand(stock_id="test-stock-1", symbol="AAPL")
        assert command.symbol == "AAPL"
        assert command.has_updates() is True
        update_fields = command.get_update_fields()
        assert "symbol" in update_fields
        assert update_fields["symbol"] == "AAPL"

    def test_update_stock_command_symbol_normalization(self) -> None:
        """Should normalize symbol to uppercase."""
        command = UpdateStockCommand(stock_id="test-stock-1", symbol="aapl")
        assert command.symbol == "AAPL"

    def test_update_stock_command_invalid_symbol(self) -> None:
        """Should reject invalid symbols."""
        with pytest.raises(ValueError, match="Invalid symbol format"):
            _ = UpdateStockCommand(
                stock_id="test-stock-1", symbol="123ABC"  # Contains numbers
            )

    def test_update_stock_command_empty_symbol(self) -> None:
        """Should reject empty symbols."""
        with pytest.raises(ValueError, match="Symbol cannot be empty"):
            _ = UpdateStockCommand(stock_id="test-stock-1", symbol="")

    def test_update_stock_command_symbol_in_equality(self) -> None:
        """Should include symbol in equality comparison."""
        command1 = UpdateStockCommand(stock_id="test-stock-1", symbol="AAPL")
        command2 = UpdateStockCommand(stock_id="test-stock-1", symbol="MSFT")
        command3 = UpdateStockCommand(stock_id="test-stock-1", symbol="AAPL")

        assert command1 != command2  # Different symbols
        assert command1 == command3  # Same symbol

    def test_update_stock_command_symbol_in_hash(self) -> None:
        """Should include symbol in hash calculation."""
        command1 = UpdateStockCommand(stock_id="test-stock-1", symbol="AAPL")
        command2 = UpdateStockCommand(stock_id="test-stock-1", symbol="AAPL")

        # Same data should have same hash
        assert hash(command1) == hash(command2)

        # Can be used in sets
        command_set = {command1, command2}
        assert len(command_set) == 1

    def test_update_stock_command_symbol_property(self) -> None:
        """Should access symbol via property."""
        command = UpdateStockCommand(stock_id="test-stock-1")
        assert command.symbol is None

        command2 = UpdateStockCommand(stock_id="test-stock-1", symbol="AAPL")
        assert command2.symbol == "AAPL"
