"""
Comprehensive test suite for Money value object in domain layer.

Tests the Money value object as a foundational domain component.
This follows TDD approach by defining all expected behavior before implementation.
"""

from decimal import Decimal

import pytest

from src.domain.value_objects.money import Money


class TestMoneyCreation:
    """Test Money value object creation and validation."""

    def test_create_money_with_decimal_amount(self):
        """Should create Money with decimal amount."""
        money = Money(Decimal("100.50"))
        assert money.amount == Decimal("100.50")

    def test_create_money_with_integer_amount(self):
        """Should create Money with integer amount converted to decimal."""
        money = Money(100)
        assert money.amount == Decimal("100.00")

    def test_create_money_with_float_amount(self):
        """Should create Money with float amount converted to decimal."""
        money = Money(99.99)
        assert money.amount == Decimal("99.99")

    def test_create_money_with_string_amount(self):
        """Should create Money with string amount converted to decimal."""
        money = Money("75.25")
        assert money.amount == Decimal("75.25")

    def test_create_money_with_zero_amount(self):
        """Should allow zero amount."""
        money = Money(0)
        assert money.amount == Decimal("0.00")

    def test_create_money_with_negative_amount(self):
        """Should allow negative amounts for debts/adjustments."""
        money = Money(-50.75)
        assert money.amount == Decimal("-50.75")

    def test_reject_invalid_amount_type(self):
        """Should reject non-numeric amount types."""
        with pytest.raises(TypeError):
            Money("invalid")

    def test_precision_handling(self):
        """Should handle high-precision decimal amounts by rounding to currency precision."""
        money = Money(Decimal("100.123456789"))
        assert money.amount == Decimal("100.12")  # Rounded to 2 decimal places


# Rounded to 2 decimal places


class TestMoneyArithmetic:
    """Test Money arithmetic operations."""

    def test_add_money(self):
        """Should add money amounts."""
        money1 = Money(100)
        money2 = Money(50)
        result = money1 + money2
        assert result.amount == Decimal("150")

    def test_subtract_money(self):
        """Should subtract money amounts."""
        money1 = Money(100)
        money2 = Money(30)
        result = money1 - money2
        assert result.amount == Decimal("70")

    def test_multiply_by_scalar(self):
        """Should multiply money by numeric scalar."""
        money = Money(100)
        result = money * 2.5
        assert result.amount == Decimal("250.00")

    def test_multiply_by_decimal(self):
        """Should multiply money by decimal scalar."""
        money = Money(100)
        result = money * Decimal("1.5")
        assert result.amount == Decimal("150.00")

    def test_divide_by_scalar(self):
        """Should divide money by numeric scalar."""
        money = Money(100)
        result = money / 4
        assert result.amount == Decimal("25.00")

    def test_divide_by_zero_raises_error(self):
        """Should raise error when dividing by zero."""
        money = Money(100)
        with pytest.raises(ZeroDivisionError):
            money / 0

    def test_negate_money(self):
        """Should negate money amount."""
        money = Money(100)
        result = -money
        assert result.amount == Decimal("-100.00")

    def test_absolute_value(self):
        """Should return absolute value of money."""
        money = Money(-100)
        result = abs(money)
        assert result.amount == Decimal("100.00")


class TestMoneyComparison:
    """Test Money comparison operations."""

    def test_equality_same_amount(self):
        """Should be equal with same amount."""
        money1 = Money(100)
        money2 = Money(100)
        assert money1 == money2

    def test_inequality_different_amount(self):
        """Should not be equal with different amounts."""
        money1 = Money(100)
        money2 = Money(50)
        assert money1 != money2

    def test_less_than(self):
        """Should compare less than."""
        money1 = Money(50)
        money2 = Money(100)
        assert money1 < money2
        assert not money2 < money1

    def test_greater_than(self):
        """Should compare greater than."""
        money1 = Money(100)
        money2 = Money(50)
        assert money1 > money2
        assert not money2 > money1

    def test_less_than_or_equal(self):
        """Should compare less than or equal."""
        money1 = Money(50)
        money2 = Money(100)
        money3 = Money(50)
        assert money1 <= money2
        assert money1 <= money3
        assert not money2 <= money1

    def test_greater_than_or_equal(self):
        """Should compare greater than or equal."""
        money1 = Money(100)
        money2 = Money(50)
        money3 = Money(100)
        assert money1 >= money2
        assert money1 >= money3
        assert not money2 >= money1


class TestMoneyUtilities:
    """Test Money utility methods."""

    def test_is_zero(self):
        """Should identify zero amounts."""
        zero_money = Money(0)
        non_zero_money = Money(100)
        assert zero_money.is_zero()
        assert not non_zero_money.is_zero()

    def test_is_positive(self):
        """Should identify positive amounts."""
        positive_money = Money(100)
        zero_money = Money(0)
        negative_money = Money(-50)
        assert positive_money.is_positive()
        assert not zero_money.is_positive()
        assert not negative_money.is_positive()

    def test_is_negative(self):
        """Should identify negative amounts."""
        negative_money = Money(-50)
        zero_money = Money(0)
        positive_money = Money(100)
        assert negative_money.is_negative()
        assert not zero_money.is_negative()
        assert not positive_money.is_negative()

    def test_to_string_representation(self):
        """Should provide readable string representation."""
        money = Money(100.50)
        assert str(money) == "$100.50"

    def test_to_repr_representation(self):
        """Should provide developer representation."""
        money = Money(100.50)
        assert repr(money) == "Money(100.50)"

    def test_hash_for_sets_and_dicts(self):
        """Should be hashable for use in sets and as dict keys."""
        money1 = Money(100)
        money2 = Money(100)
        money3 = Money(50)

        money_set = {money1, money2, money3}
        assert len(money_set) == 2  # money1 and money2 are equal

        money_dict = {money1: "first", money2: "second"}
        assert len(money_dict) == 1  # money1 and money2 have same hash


# money1 and money2 have same hash


class TestMoneyClassMethods:
    """Test Money class methods and factory methods."""

    def test_zero_factory_method(self):
        """Should create zero money."""
        zero_money = Money.zero()
        assert zero_money.amount == Decimal("0")
        assert zero_money.is_zero()

    def test_from_cents_factory_method(self):
        """Should create money from cents/smallest currency unit."""
        money = Money.from_cents(12550)  # 125.50 USD
        assert money.amount == Decimal("125.50")

    def test_to_cents_method(self):
        """Should convert money to cents."""
        money = Money(125.50)
        assert money.to_cents() == 12550


class TestMoneyEdgeCases:
    """Test Money edge cases and error conditions."""

    def test_very_large_amounts(self):
        """Should handle very large amounts."""
        large_amount = Decimal("999999999999999.99")
        money = Money(large_amount)
        assert money.amount == large_amount

    def test_very_small_amounts(self):
        """Should handle very small amounts by rounding to currency precision."""
        small_amount = Decimal("0.00000001")
        money = Money(small_amount)
        assert money.amount == Decimal("0.00")  # Rounded to 2 decimal places

    def test_immutability(self):
        """Should be immutable value object."""
        money = Money(100)

        # Should not be able to modify amount
        with pytest.raises(AttributeError):
            money.amount = Decimal("200")

    def test_thread_safety(self):
        """Should be thread-safe as immutable value object."""
        # Since Money is immutable, it's inherently thread-safe
        # This test documents the expectation
        money = Money(100)

        # Multiple operations should not affect the original
        result1 = money + Money(50)
        result2 = money * 2
        result3 = -money

        # Original should be unchanged
        assert money.amount == Decimal("100.00")

        # Results should be independent
        assert result1.amount == Decimal("150.00")
        assert result2.amount == Decimal("200.00")
        assert result3.amount == Decimal("-100.00")
