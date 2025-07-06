"""
Tests for UpdateStockCommand.

Following TDD approach - these tests define the expected behavior
of the UpdateStockCommand used for stock update operations.
"""

import pytest

from src.application.commands.stock import UpdateStockCommand, UpdateStockInputs


class TestUpdateStockCommand:
    """Test suite for UpdateStockCommand."""

    def test_update_stock_command_with_valid_data(self) -> None:
        """Should create command with valid update data."""
        inputs = UpdateStockInputs(
            stock_id="test-stock-1",
            name="Apple Inc. (Updated)",
            industry_group="Technology",
            grade="A",
            notes="Updated notes",
        )
        command = UpdateStockCommand(inputs)

        assert command.stock_id == "test-stock-1"
        assert command.name == "Apple Inc. (Updated)"
        assert command.industry_group == "Technology"
        assert command.grade == "A"
        assert command.notes == "Updated notes"

    def test_update_stock_command_with_partial_data(self) -> None:
        """Should create command with only some fields to update."""
        inputs = UpdateStockInputs(
            stock_id="test-stock-1",
            grade="B",
            notes="Updated notes only",
        )
        command = UpdateStockCommand(inputs)

        assert command.stock_id == "test-stock-1"
        assert command.name is None
        assert command.industry_group is None
        assert command.grade == "B"
        assert command.notes == "Updated notes only"

    def test_update_stock_command_strips_whitespace(self) -> None:
        """Should strip whitespace from fields."""
        inputs = UpdateStockInputs(
            stock_id="test-stock-1",
            name="  Apple Inc.  ",
            industry_group="  Technology  ",
            notes="  Updated notes  ",
        )
        command = UpdateStockCommand(inputs)

        assert command.name == "Apple Inc."
        assert command.industry_group == "Technology"
        assert command.notes == "Updated notes"

    def test_update_stock_command_with_empty_string_sets_none(self) -> None:
        """Should convert empty strings to None for optional fields."""
        inputs = UpdateStockInputs(
            stock_id="test-stock-1",
            name="Apple Inc.",
            industry_group="",
            notes="",
        )
        command = UpdateStockCommand(inputs)

        assert command.name == "Apple Inc."
        assert command.industry_group is None
        assert command.notes == ""  # Notes should be empty string, not None

    def test_update_stock_command_with_invalid_stock_id_raises_error(self) -> None:
        """Should raise error for invalid stock ID."""
        with pytest.raises(ValueError, match="Stock ID must be a non-empty string"):
            inputs = UpdateStockInputs(stock_id="")
            _ = UpdateStockCommand(inputs)

        with pytest.raises(ValueError, match="Stock ID must be a non-empty string"):
            inputs = UpdateStockInputs(stock_id="   ")  # whitespace-only string
            _ = UpdateStockCommand(inputs)

    def test_update_stock_command_with_invalid_grade_raises_error(self) -> None:
        """Should raise error for invalid grade."""
        with pytest.raises(ValueError, match="Invalid grade"):
            inputs = UpdateStockInputs(stock_id="test-stock-1", grade="Z")
            _ = UpdateStockCommand(inputs)

    def test_update_stock_command_with_empty_name_allowed(self) -> None:
        """Should allow empty name as it's optional."""
        inputs = UpdateStockInputs(stock_id="test-stock-1", name="")
        command = UpdateStockCommand(inputs)
        assert command.name is None  # Empty string normalized to None

        inputs2 = UpdateStockInputs(stock_id="test-stock-1", name="   ")
        command2 = UpdateStockCommand(inputs2)
        assert command2.name is None  # Whitespace normalized to None

    def test_update_stock_command_equality(self) -> None:
        """Should compare commands for equality."""
        inputs1 = UpdateStockInputs(stock_id="test-stock-1", grade="A")
        inputs2 = UpdateStockInputs(stock_id="test-stock-1", grade="A")
        inputs3 = UpdateStockInputs(stock_id="test-stock-2", grade="A")
        command1 = UpdateStockCommand(inputs1)
        command2 = UpdateStockCommand(inputs2)
        command3 = UpdateStockCommand(inputs3)

        assert command1 == command2
        assert command1 != command3

    def test_update_stock_command_string_representation(self) -> None:
        """Should have meaningful string representation."""
        inputs = UpdateStockInputs(stock_id="test-stock-1", grade="A")
        command = UpdateStockCommand(inputs)

        str_repr = str(command)
        assert "UpdateStockCommand" in str_repr
        assert "stock_id=test-stock-1" in str_repr

    def test_update_stock_command_is_immutable(self) -> None:
        """Command should be immutable after creation."""
        inputs = UpdateStockInputs(stock_id="test-stock-1", grade="A")
        command = UpdateStockCommand(inputs)

        with pytest.raises(AttributeError):
            command.stock_id = "different-id"  # type: ignore[misc]

        with pytest.raises(AttributeError):
            command.grade = "B"  # type: ignore[misc]

    def test_update_stock_command_has_no_updates_when_all_fields_none(self) -> None:
        """Should detect when no fields are being updated."""
        inputs = UpdateStockInputs(stock_id="test-stock-1")
        command = UpdateStockCommand(inputs)

        assert not command.has_updates()

    def test_update_stock_command_has_updates_when_fields_provided(self) -> None:
        """Should detect when fields are being updated."""
        inputs = UpdateStockInputs(stock_id="test-stock-1", grade="A")
        command = UpdateStockCommand(inputs)

        assert command.has_updates()

    def test_update_stock_command_get_update_fields(self) -> None:
        """Should return only fields that are being updated."""
        inputs = UpdateStockInputs(
            stock_id="test-stock-1",
            name="Apple Inc.",
            grade="A",
        )
        command = UpdateStockCommand(inputs)

        fields = command.get_update_fields()
        assert "name" in fields
        assert "grade" in fields
        assert "industry_group" not in fields
        assert "notes" not in fields
        assert fields["name"] == "Apple Inc."
        assert fields["grade"] == "A"

    def test_update_stock_command_equality_with_non_matching_types(self) -> None:
        """Should return False when compared with non-command objects."""
        inputs = UpdateStockInputs(stock_id="test-stock-1", grade="A")
        command = UpdateStockCommand(inputs)

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
        inputs = UpdateStockInputs(stock_id="test-stock-1", sector="Technology")
        command = UpdateStockCommand(inputs)

        # Test sector property getter
        assert command.sector == "Technology"

        # Test None case
        inputs_no_sector = UpdateStockInputs(stock_id="test-stock-1")
        command_no_sector = UpdateStockCommand(inputs_no_sector)
        assert command_no_sector.sector is None

    def test_update_stock_command_normalize_sector_none_case(self) -> None:
        """Should handle None sector normalization correctly."""
        # Test the None case in _normalize_sector method
        inputs = UpdateStockInputs(stock_id="test-stock-1", sector=None)
        command = UpdateStockCommand(inputs)

        assert command.sector is None

    def test_update_stock_command_with_explicit_none_sector(self) -> None:
        """Should handle explicitly passed None sector."""
        # This tests the return None branch in _normalize_sector
        inputs = UpdateStockInputs(
            stock_id="test-stock-1",
            name="Test Company",
            sector=None,  # Explicitly None
            grade="A",
        )
        command = UpdateStockCommand(inputs)

        assert command.sector is None
        assert command.name == "Test Company"
        assert command.grade == "A"

    def test_update_stock_command_repr_representation(self) -> None:
        """Should have meaningful repr representation."""
        inputs = UpdateStockInputs(
            stock_id="test-stock-1",
            name="Apple Inc.",
            industry_group="Software",
            grade="A",
            notes="Updated notes",
        )
        command = UpdateStockCommand(inputs)

        repr_str = repr(command)
        assert "UpdateStockCommand" in repr_str
        assert "stock_id='test-stock-1'" in repr_str
        assert "name='Apple Inc.'" in repr_str
        assert "industry_group='Software'" in repr_str
        assert "grade='A'" in repr_str
        assert "notes='Updated notes'" in repr_str

    def test_update_stock_command_normalize_empty_sector_string(self) -> None:
        """Should normalize empty sector string to None."""
        inputs = UpdateStockInputs(
            stock_id="test-stock-1",
            sector="",  # Empty string
        )
        command = UpdateStockCommand(inputs)

        assert command.sector is None

    def test_update_stock_command_equality_with_sectors(self) -> None:
        """Should compare commands with sectors for equality."""
        inputs1 = UpdateStockInputs(stock_id="test-stock-1", sector="Technology")
        inputs2 = UpdateStockInputs(stock_id="test-stock-1", sector="Technology")
        inputs3 = UpdateStockInputs(stock_id="test-stock-1", sector="Healthcare")
        command1 = UpdateStockCommand(inputs1)
        command2 = UpdateStockCommand(inputs2)
        command3 = UpdateStockCommand(inputs3)

        assert command1 == command2  # Same sectors
        assert command1 != command3  # Different sectors

        # Test with None sectors - should be equal
        inputs4 = UpdateStockInputs(stock_id="test-stock-1", sector=None)
        inputs5 = UpdateStockInputs(stock_id="test-stock-1", sector=None)
        command4 = UpdateStockCommand(inputs4)
        command5 = UpdateStockCommand(inputs5)
        assert command4 == command5

    def test_update_stock_command_whitespace_only_stock_id_validation(self) -> None:
        """Should validate stock_id for whitespace-only strings."""
        with pytest.raises(ValueError, match="Stock ID must be a non-empty string"):
            inputs = UpdateStockInputs(stock_id="   ")  # Whitespace-only
            _ = UpdateStockCommand(inputs)

    def test_update_stock_command_whitespace_only_name_validation(self) -> None:
        """Should allow whitespace-only name as it's optional."""
        inputs = UpdateStockInputs(stock_id="test-stock-1", name="   ")
        command = UpdateStockCommand(inputs)
        assert command.name is None  # Whitespace normalized to None

    def test_update_stock_command_industry_group_empty_string_normalization(
        self,
    ) -> None:
        """Should normalize empty industry_group string to None."""
        inputs = UpdateStockInputs(
            stock_id="test-stock-1",
            industry_group="",  # Empty string
        )
        command = UpdateStockCommand(inputs)

        assert command.industry_group is None

    def test_update_stock_command_industry_group_whitespace_normalization(self) -> None:
        """Should normalize whitespace-only industry_group to None."""
        inputs = UpdateStockInputs(
            stock_id="test-stock-1",
            industry_group="   ",  # Whitespace-only
        )
        command = UpdateStockCommand(inputs)

        assert command.industry_group is None

    def test_update_stock_command_all_grade_values(self) -> None:
        """Should accept all valid grade values."""
        for grade in ["A", "B", "C", None]:
            inputs = UpdateStockInputs(
                stock_id="test-stock-1",
                grade=grade,
            )
            command = UpdateStockCommand(inputs)
            assert command.grade == grade

    def test_update_stock_command_get_update_fields_all_fields(self) -> None:
        """Should return all fields when all are provided."""
        inputs = UpdateStockInputs(
            stock_id="test-stock-1",
            name="Test Company",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="Test notes",
        )
        command = UpdateStockCommand(inputs)

        fields = command.get_update_fields()
        assert len(fields) == 5
        assert fields["name"] == "Test Company"
        assert fields["sector"] == "Technology"
        assert fields["industry_group"] == "Software"
        assert fields["grade"] == "A"
        assert fields["notes"] == "Test notes"

    def test_update_stock_command_get_update_fields_empty(self) -> None:
        """Should return empty dict when no fields are provided."""
        inputs = UpdateStockInputs(stock_id="test-stock-1")
        command = UpdateStockCommand(inputs)

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
            inputs = UpdateStockInputs(**kwargs)
            command = UpdateStockCommand(inputs)
            assert (
                command.has_updates()
            ), f"Failed to detect update for field {field_name}"

    def test_update_stock_command_with_explicit_none_name(self) -> None:
        """Should handle explicitly passed None name."""
        # This ensures coverage of None branch in _normalize_name
        inputs = UpdateStockInputs(stock_id="test-stock-1", name=None)
        command = UpdateStockCommand(inputs)
        assert command.name is None

    def test_update_stock_command_base_class_coverage(self) -> None:
        """Test base class coverage for UpdateStockCommand missing lines."""
        # Test that normal initialization works (covers line 378 - super().__setattr__)
        inputs = UpdateStockInputs(stock_id="test-stock-1", name="Updated Name")
        command = UpdateStockCommand(inputs)
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

        # Object has no _stock_id attribute, so __setattr__ should work
        # This directly exercises the super().__setattr__ branch
        command.test_attr = "test_value"

        # Now properly initialize the object
        inputs = UpdateStockInputs(
            stock_id="test-stock-1",
            name="Updated Company Name",
            sector="Healthcare",
            industry_group="Pharmaceuticals",
            grade="B",
            notes="Updated notes with more details",
        )
        UpdateStockCommand.__init__(command, inputs)

        # Verify all attributes were set correctly
        assert command.stock_id == "test-stock-1"
        assert command.name == "Updated Company Name"
        assert command.sector == "Healthcare"
        assert command.industry_group == "Pharmaceuticals"
        assert command.grade == "B"
        assert command.notes == "Updated notes with more details"

    def test_update_stock_command_with_symbol(self) -> None:
        """Should handle symbol updates."""
        inputs = UpdateStockInputs(stock_id="test-stock-1", symbol="AAPL")
        command = UpdateStockCommand(inputs)
        assert command.symbol == "AAPL"
        assert command.has_updates() is True
        update_fields = command.get_update_fields()
        assert "symbol" in update_fields
        assert update_fields["symbol"] == "AAPL"

    def test_update_stock_command_symbol_normalization(self) -> None:
        """Should normalize symbol to uppercase."""
        inputs = UpdateStockInputs(stock_id="test-stock-1", symbol="aapl")
        command = UpdateStockCommand(inputs)
        assert command.symbol == "AAPL"

    def test_update_stock_command_invalid_symbol(self) -> None:
        """Should reject invalid symbols."""
        with pytest.raises(ValueError, match="Invalid symbol format"):
            inputs = UpdateStockInputs(
                stock_id="test-stock-1",
                symbol="123ABC",  # Contains numbers
            )
            _ = UpdateStockCommand(inputs)

    def test_update_stock_command_empty_symbol(self) -> None:
        """Should reject empty symbols."""
        with pytest.raises(ValueError, match="Symbol cannot be empty"):
            inputs = UpdateStockInputs(stock_id="test-stock-1", symbol="")
            _ = UpdateStockCommand(inputs)

    def test_update_stock_command_symbol_in_equality(self) -> None:
        """Should include symbol in equality comparison."""
        inputs1 = UpdateStockInputs(stock_id="test-stock-1", symbol="AAPL")
        inputs2 = UpdateStockInputs(stock_id="test-stock-1", symbol="MSFT")
        inputs3 = UpdateStockInputs(stock_id="test-stock-1", symbol="AAPL")
        command1 = UpdateStockCommand(inputs1)
        command2 = UpdateStockCommand(inputs2)
        command3 = UpdateStockCommand(inputs3)

        assert command1 != command2  # Different symbols
        assert command1 == command3  # Same symbols

    def test_update_stock_command_symbol_hash(self) -> None:
        """Should include symbol in hash calculation."""
        inputs1 = UpdateStockInputs(stock_id="test-stock-1", symbol="AAPL")
        inputs2 = UpdateStockInputs(stock_id="test-stock-1", symbol="AAPL")
        command1 = UpdateStockCommand(inputs1)
        command2 = UpdateStockCommand(inputs2)

        # Same values should have same hash
        assert hash(command1) == hash(command2)

        # Can be used in sets
        command_set = {command1, command2}
        assert len(command_set) == 1

    def test_update_stock_command_symbol_property(self) -> None:
        """Should access symbol via property."""
        inputs = UpdateStockInputs(stock_id="test-stock-1")
        command = UpdateStockCommand(inputs)
        assert command.symbol is None

        inputs2 = UpdateStockInputs(stock_id="test-stock-1", symbol="AAPL")
        command2 = UpdateStockCommand(inputs2)
        assert command2.symbol == "AAPL"
