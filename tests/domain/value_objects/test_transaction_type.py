"""
Tests for TransactionType value object.

This module tests the TransactionType value object which encapsulates
transaction type validation and business logic for buy/sell operations.
"""

import pytest

from src.domain.value_objects.transaction_type import TransactionType


class TestTransactionTypeCreation:
    """Test TransactionType creation and validation."""

    def test_create_buy_transaction_type(self) -> None:
        """Should create valid buy transaction type."""
        transaction_type = TransactionType("buy")

        assert transaction_type.value == "buy"
        assert transaction_type.is_buy() is True
        assert transaction_type.is_sell() is False

    def test_create_sell_transaction_type(self) -> None:
        """Should create valid sell transaction type."""
        transaction_type = TransactionType("sell")

        assert transaction_type.value == "sell"
        assert transaction_type.is_buy() is False
        assert transaction_type.is_sell() is True

    def test_create_with_uppercase_normalizes_to_lowercase(self) -> None:
        """Should normalize uppercase values to lowercase."""
        buy_upper = TransactionType("BUY")
        sell_upper = TransactionType("SELL")

        assert buy_upper.value == "buy"
        assert sell_upper.value == "sell"

    def test_create_with_mixed_case_normalizes_to_lowercase(self) -> None:
        """Should normalize mixed case values to lowercase."""
        buy_mixed = TransactionType("Buy")
        sell_mixed = TransactionType("Sell")

        assert buy_mixed.value == "buy"
        assert sell_mixed.value == "sell"

    def test_create_with_whitespace_strips_whitespace(self) -> None:
        """Should strip leading and trailing whitespace."""
        buy_whitespace = TransactionType("  buy  ")
        sell_whitespace = TransactionType("\tsell\n")

        assert buy_whitespace.value == "buy"
        assert sell_whitespace.value == "sell"

    def test_create_with_empty_string_raises_error(self) -> None:
        """Should raise ValueError for empty transaction type."""
        with pytest.raises(ValueError, match="Transaction type cannot be empty"):
            _ = TransactionType("")

    def test_create_with_whitespace_only_raises_error(self) -> None:
        """Should raise ValueError for whitespace-only transaction type."""
        with pytest.raises(ValueError, match="Transaction type cannot be empty"):
            _ = TransactionType("   ")

    def test_create_with_invalid_type_raises_error(self) -> None:
        """Should raise ValueError for invalid transaction types."""
        invalid_types = ["invalid", "trade", "exchange", "transfer", "deposit"]

        for invalid_type in invalid_types:
            with pytest.raises(
                ValueError, match="Transaction type must be 'buy' or 'sell'"
            ):
                _ = TransactionType(invalid_type)

    def test_create_with_partial_match_raises_error(self) -> None:
        """Should raise ValueError for partial matches of valid types."""
        partial_matches = ["bu", "sel", "buying", "selling", "buys", "sells"]

        for partial_match in partial_matches:
            with pytest.raises(
                ValueError, match="Transaction type must be 'buy' or 'sell'"
            ):
                _ = TransactionType(partial_match)


class TestTransactionTypeBusinessLogic:
    """Test TransactionType business logic methods."""

    def test_is_buy_returns_true_for_buy_type(self) -> None:
        """Should return True for buy transaction type."""
        buy_type = TransactionType("buy")

        assert buy_type.is_buy() is True

    def test_is_buy_returns_false_for_sell_type(self) -> None:
        """Should return False for sell transaction type."""
        sell_type = TransactionType("sell")

        assert sell_type.is_buy() is False

    def test_is_sell_returns_true_for_sell_type(self) -> None:
        """Should return True for sell transaction type."""
        sell_type = TransactionType("sell")

        assert sell_type.is_sell() is True

    def test_is_sell_returns_false_for_buy_type(self) -> None:
        """Should return False for buy transaction type."""
        buy_type = TransactionType("buy")

        assert buy_type.is_sell() is False


class TestTransactionTypeEquality:
    """Test TransactionType equality and hashing."""

    def test_equal_transaction_types_are_equal(self) -> None:
        """Should be equal if transaction types have same value."""
        buy1 = TransactionType("buy")
        buy2 = TransactionType("BUY")  # Different case but same normalized value
        sell1 = TransactionType("sell")
        sell2 = TransactionType("SELL")

        assert buy1 == buy2
        assert sell1 == sell2

    def test_different_transaction_types_are_not_equal(self) -> None:
        """Should not be equal if transaction types have different values."""
        buy_type = TransactionType("buy")
        sell_type = TransactionType("sell")

        assert buy_type != sell_type

    def test_transaction_type_not_equal_to_other_types(self) -> None:
        """Should not be equal to non-TransactionType objects."""
        buy_type = TransactionType("buy")

        assert buy_type != "buy"
        assert buy_type != 1
        assert buy_type != None
        assert buy_type != {"value": "buy"}

    def test_transaction_type_immutability(self) -> None:
        """Should be immutable after creation."""
        transaction_type = TransactionType("buy")

        # Test that attempting to modify raises AttributeError
        with pytest.raises(AttributeError, match="TransactionType is immutable"):
            transaction_type.value = "sell"  # type: ignore[misc]

        with pytest.raises(AttributeError, match="TransactionType is immutable"):
            transaction_type._value = "sell"  # type: ignore[misc]

    def test_transaction_type_base_class_coverage(self) -> None:
        """Test base class coverage for TransactionType missing lines."""
        # Test that normal initialization works (covers line 91 - super().__setattr__)
        transaction_type = TransactionType("buy")
        assert transaction_type.value == "buy"

        # Test __str__ method (covers line 71)
        assert str(transaction_type) == "buy"

        # Test hash method (covers line 85)
        assert hash(transaction_type) == hash("buy")

    def test_transaction_type_setattr_during_initialization(self) -> None:
        """Test that __setattr__ allows setting attributes during initialization."""
        # Create a partially initialized object
        transaction_type = object.__new__(TransactionType)

        # This exercises the super().__setattr__ branch (line 91)
        setattr(transaction_type, "test_attr", "test_value")

        # Now properly initialize the object
        TransactionType.__init__(transaction_type, "buy")
        assert transaction_type.value == "buy"
