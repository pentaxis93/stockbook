"""
Comprehensive test suite for Quantity value object in domain layer.

Tests the Quantity value object as a foundational domain component.
This follows TDD approach by defining all expected behavior before implementation.
"""

from decimal import Decimal

import pytest

from src.domain.value_objects.quantity import Quantity


class TestQuantityCreation:
    """Test Quantity value object creation and validation."""

    def test_create_quantity_with_decimal_value(self):
        """Should create Quantity with decimal value."""
        qty = Quantity(Decimal("100.5"))
        assert qty.value == Decimal("100.5")

    def test_create_quantity_with_integer_value(self):
        """Should create Quantity with integer value converted to decimal."""
        qty = Quantity(100)
        assert qty.value == Decimal("100")

    def test_create_quantity_with_float_value(self):
        """Should create Quantity with float value converted to decimal."""
        qty = Quantity(99.75)
        assert qty.value == Decimal("99.75")

    def test_create_quantity_with_string_value(self):
        """Should create Quantity with string value converted to decimal."""
        qty = Quantity("75.25")
        assert qty.value == Decimal("75.25")

    def test_create_quantity_with_zero_value(self):
        """Should allow zero quantity."""
        qty = Quantity(0)
        assert qty.value == Decimal("0")

    def test_reject_negative_quantity(self):
        """Should reject negative quantities in business contexts."""
        with pytest.raises(ValueError, match="Quantity cannot be negative"):
            Quantity(-10)

    def test_negative_quantities_not_allowed(self):
        """Should not allow negative quantities in simplified implementation."""
        with pytest.raises(ValueError, match="Quantity cannot be negative"):
            Quantity(-10)

    def test_reject_invalid_value_type(self):
        """Should reject non-numeric value types."""
        with pytest.raises(TypeError):
            Quantity("invalid")

    def test_precision_handling(self):
        """Should handle high-precision decimal values."""
        qty = Quantity(Decimal("100.123456789"))
        assert qty.value == Decimal("100.123456789")


class TestQuantityArithmetic:
    """Test Quantity arithmetic operations."""

    def test_add_quantities(self):
        """Should add quantities together."""
        qty1 = Quantity(100)
        qty2 = Quantity(50)
        result = qty1 + qty2
        assert result.value == Decimal("150")

    def test_subtract_quantities(self):
        """Should subtract quantities."""
        qty1 = Quantity(100)
        qty2 = Quantity(30)
        result = qty1 - qty2
        assert result.value == Decimal("70")

    def test_subtract_resulting_in_negative_raises_error(self):
        """Should raise error when subtraction results in negative (default behavior)."""
        qty1 = Quantity(30)
        qty2 = Quantity(100)
        with pytest.raises(ValueError, match="Resulting quantity cannot be negative"):
            qty1 - qty2

    def test_subtract_normal_behavior(self):
        """Should perform normal subtraction when result is positive."""
        qty1 = Quantity(100)
        qty2 = Quantity(30)
        result = qty1 - qty2
        assert result.value == Decimal("70")

    def test_multiply_by_scalar(self):
        """Should multiply quantity by numeric scalar."""
        qty = Quantity(100)
        result = qty * 2.5
        assert result.value == Decimal("250")

    def test_multiply_by_decimal(self):
        """Should multiply quantity by decimal scalar."""
        qty = Quantity(100)
        result = qty * Decimal("1.5")
        assert result.value == Decimal("150")

    def test_divide_by_scalar(self):
        """Should divide quantity by numeric scalar."""
        qty = Quantity(100)
        result = qty / 4
        assert result.value == Decimal("25")

    def test_divide_by_zero_raises_error(self):
        """Should raise error when dividing by zero."""
        qty = Quantity(100)
        with pytest.raises(ZeroDivisionError):
            qty / 0


class TestQuantityComparison:
    """Test Quantity comparison operations."""

    def test_equality_same_value(self):
        """Should be equal with same value."""
        qty1 = Quantity(100)
        qty2 = Quantity(100)
        assert qty1 == qty2

    def test_inequality_different_value(self):
        """Should not be equal with different values."""
        qty1 = Quantity(100)
        qty2 = Quantity(50)
        assert qty1 != qty2

    def test_less_than_comparison(self):
        """Should compare less than correctly."""
        qty1 = Quantity(50)
        qty2 = Quantity(100)
        assert qty1 < qty2
        assert not qty2 < qty1

    def test_greater_than_comparison(self):
        """Should compare greater than correctly."""
        qty1 = Quantity(100)
        qty2 = Quantity(50)
        assert qty1 > qty2
        assert not qty2 > qty1

    def test_less_than_or_equal(self):
        """Should compare less than or equal."""
        qty1 = Quantity(50)
        qty2 = Quantity(100)
        qty3 = Quantity(50)
        assert qty1 <= qty2
        assert qty1 <= qty3
        assert not qty2 <= qty1

    def test_greater_than_or_equal(self):
        """Should compare greater than or equal."""
        qty1 = Quantity(100)
        qty2 = Quantity(50)
        qty3 = Quantity(100)
        assert qty1 >= qty2
        assert qty1 >= qty3
        assert not qty2 >= qty1


class TestQuantityUtilities:
    """Test Quantity utility methods."""

    def test_is_zero(self):
        """Should identify zero quantities."""
        zero_qty = Quantity(0)
        non_zero_qty = Quantity(100)
        assert zero_qty.is_zero()
        assert not non_zero_qty.is_zero()

    def test_is_positive(self):
        """Should identify positive quantities."""
        positive_qty = Quantity(100)
        zero_qty = Quantity(0)
        assert positive_qty.is_positive()
        assert not zero_qty.is_positive()

    def test_is_whole_number(self):
        """Should identify whole number quantities."""
        whole_qty = Quantity(100)
        fractional_qty = Quantity(100.5)
        assert whole_qty.is_whole()
        assert not fractional_qty.is_whole()

    def test_to_string_representation(self):
        """Should provide readable string representation."""
        qty = Quantity(100.50)
        assert str(qty) == "100.5"

    def test_to_repr_representation(self):
        """Should provide developer representation."""
        qty = Quantity(100.50)
        assert repr(qty) == "Quantity(100.5)"

    def test_hash_for_sets_and_dicts(self):
        """Should be hashable for use in sets and as dict keys."""
        qty1 = Quantity(100)
        qty2 = Quantity(100)
        qty3 = Quantity(50)

        qty_set = {qty1, qty2, qty3}
        assert len(qty_set) == 2  # qty1 and qty2 are equal

        qty_dict = {qty1: "first", qty2: "second"}
        assert len(qty_dict) == 1  # qty1 and qty2 have same hash


class TestQuantityClassMethods:
    """Test Quantity class methods and factory methods."""

    def test_zero_factory_method(self):
        """Should create zero quantity."""
        zero_qty = Quantity.zero()
        assert zero_qty.value == Decimal("0")
        assert zero_qty.is_zero()


class TestQuantityEdgeCases:
    """Test Quantity edge cases and error conditions."""

    def test_very_large_quantities(self):
        """Should handle very large quantities."""
        large_qty = Quantity(Decimal("999999999999999"))
        assert large_qty.value == Decimal("999999999999999")

    def test_very_small_quantities(self):
        """Should handle very small quantities."""
        small_qty = Quantity(Decimal("0.00000001"))
        assert small_qty.value == Decimal("0.00000001")

    def test_immutability(self):
        """Should be immutable value object."""
        qty = Quantity(100)

        # Should not be able to modify value
        with pytest.raises(AttributeError):
            qty.value = Decimal("200")

    def test_precision_preservation(self):
        """Should preserve decimal precision through operations."""
        qty1 = Quantity(Decimal("10.123"))
        qty2 = Quantity(Decimal("5.456"))

        result = qty1 + qty2
        # Should preserve precision
        assert result.value == Decimal("15.579")

    def test_thread_safety(self):
        """Should be thread-safe as immutable value object."""
        # Since Quantity is immutable, it's inherently thread-safe
        qty = Quantity(100)

        # Multiple operations should not affect the original
        result1 = qty + Quantity(50)
        result2 = qty * 2
        result3 = qty / 2

        # Original should be unchanged
        assert qty.value == Decimal("100")

        # Results should be independent
        assert result1.value == Decimal("150")
        assert result2.value == Decimal("200")
        assert result3.value == Decimal("50")

    def test_type_coercion_safety(self):
        """Should safely handle type coercion in operations."""
        qty = Quantity(100)

        # Should work with different numeric types
        result_int = qty + 50
        result_float = qty + 25.5
        result_decimal = qty + Decimal("10.25")

        assert result_int.value == Decimal("150")
        assert result_float.value == Decimal("125.5")
        assert result_decimal.value == Decimal("110.25")
