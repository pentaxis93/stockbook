"""
Comprehensive test suite for Money value object in shared kernel.

Tests the Money value object as a reusable component across all bounded contexts.
This follows TDD approach by defining all expected behavior before implementation.
"""

import pytest
from decimal import Decimal
from shared_kernel.value_objects.money import Money


class TestMoneyCreation:
    """Test Money value object creation and validation."""
    
    def test_create_money_with_decimal_amount(self):
        """Should create Money with decimal amount."""
        money = Money(Decimal("100.50"), "USD")
        assert money.amount == Decimal("100.50")
        assert money.currency == "USD"
    
    def test_create_money_with_integer_amount(self):
        """Should create Money with integer amount converted to decimal."""
        money = Money(100, "EUR")
        assert money.amount == Decimal("100")
        assert money.currency == "EUR"
    
    def test_create_money_with_float_amount(self):
        """Should create Money with float amount converted to decimal."""
        money = Money(99.99, "GBP")
        assert money.amount == Decimal("99.99")
        assert money.currency == "GBP"
    
    def test_create_money_with_string_amount(self):
        """Should create Money with string amount converted to decimal."""
        money = Money("75.25", "CAD")
        assert money.amount == Decimal("75.25")
        assert money.currency == "CAD"
    
    def test_create_money_with_zero_amount(self):
        """Should allow zero amount."""
        money = Money(0, "USD")
        assert money.amount == Decimal("0")
        assert money.currency == "USD"
    
    def test_create_money_with_negative_amount(self):
        """Should allow negative amounts for debts/adjustments."""
        money = Money(-50.75, "USD")
        assert money.amount == Decimal("-50.75")
        assert money.currency == "USD"
    
    def test_reject_invalid_amount_type(self):
        """Should reject non-numeric amount types."""
        with pytest.raises(TypeError):
            Money("invalid", "USD")
    
    def test_reject_empty_currency(self):
        """Should reject empty currency code."""
        with pytest.raises(ValueError):
            Money(100, "")
    
    def test_reject_none_currency(self):
        """Should reject None currency."""
        with pytest.raises(TypeError):
            Money(100, None)
    
    def test_currency_code_normalization(self):
        """Should normalize currency codes to uppercase."""
        money = Money(100, "usd")
        assert money.currency == "USD"
    
    def test_precision_handling(self):
        """Should handle high-precision decimal amounts."""
        money = Money(Decimal("100.123456789"), "USD")
        assert money.amount == Decimal("100.123456789")


class TestMoneyArithmetic:
    """Test Money arithmetic operations."""
    
    def test_add_same_currency(self):
        """Should add money with same currency."""
        money1 = Money(100, "USD")
        money2 = Money(50, "USD")
        result = money1 + money2
        assert result.amount == Decimal("150")
        assert result.currency == "USD"
    
    def test_add_different_currencies_raises_error(self):
        """Should raise error when adding different currencies."""
        money1 = Money(100, "USD")
        money2 = Money(50, "EUR")
        with pytest.raises(ValueError, match="Cannot add money with different currencies"):
            money1 + money2
    
    def test_subtract_same_currency(self):
        """Should subtract money with same currency."""
        money1 = Money(100, "USD")
        money2 = Money(30, "USD")
        result = money1 - money2
        assert result.amount == Decimal("70")
        assert result.currency == "USD"
    
    def test_subtract_different_currencies_raises_error(self):
        """Should raise error when subtracting different currencies."""
        money1 = Money(100, "USD")
        money2 = Money(30, "EUR")
        with pytest.raises(ValueError, match="Cannot subtract money with different currencies"):
            money1 - money2
    
    def test_multiply_by_scalar(self):
        """Should multiply money by numeric scalar."""
        money = Money(100, "USD")
        result = money * 2.5
        assert result.amount == Decimal("250")
        assert result.currency == "USD"
    
    def test_multiply_by_decimal(self):
        """Should multiply money by decimal scalar."""
        money = Money(100, "USD")
        result = money * Decimal("1.5")
        assert result.amount == Decimal("150")
        assert result.currency == "USD"
    
    def test_divide_by_scalar(self):
        """Should divide money by numeric scalar."""
        money = Money(100, "USD")
        result = money / 4
        assert result.amount == Decimal("25")
        assert result.currency == "USD"
    
    def test_divide_by_zero_raises_error(self):
        """Should raise error when dividing by zero."""
        money = Money(100, "USD")
        with pytest.raises(ZeroDivisionError):
            money / 0
    
    def test_negate_money(self):
        """Should negate money amount."""
        money = Money(100, "USD")
        result = -money
        assert result.amount == Decimal("-100")
        assert result.currency == "USD"
    
    def test_absolute_value(self):
        """Should return absolute value of money."""
        money = Money(-100, "USD")
        result = abs(money)
        assert result.amount == Decimal("100")
        assert result.currency == "USD"


class TestMoneyComparison:
    """Test Money comparison operations."""
    
    def test_equality_same_amount_and_currency(self):
        """Should be equal with same amount and currency."""
        money1 = Money(100, "USD")
        money2 = Money(100, "USD")
        assert money1 == money2
    
    def test_inequality_different_amount(self):
        """Should not be equal with different amounts."""
        money1 = Money(100, "USD")
        money2 = Money(50, "USD")
        assert money1 != money2
    
    def test_inequality_different_currency(self):
        """Should not be equal with different currencies."""
        money1 = Money(100, "USD")
        money2 = Money(100, "EUR")
        assert money1 != money2
    
    def test_less_than_same_currency(self):
        """Should compare less than with same currency."""
        money1 = Money(50, "USD")
        money2 = Money(100, "USD")
        assert money1 < money2
        assert not money2 < money1
    
    def test_less_than_different_currencies_raises_error(self):
        """Should raise error when comparing different currencies."""
        money1 = Money(50, "USD")
        money2 = Money(100, "EUR")
        with pytest.raises(ValueError, match="Cannot compare money with different currencies"):
            money1 < money2
    
    def test_greater_than_same_currency(self):
        """Should compare greater than with same currency."""
        money1 = Money(100, "USD")
        money2 = Money(50, "USD")
        assert money1 > money2
        assert not money2 > money1
    
    def test_less_than_or_equal(self):
        """Should compare less than or equal."""
        money1 = Money(50, "USD")
        money2 = Money(100, "USD")
        money3 = Money(50, "USD")
        assert money1 <= money2
        assert money1 <= money3
        assert not money2 <= money1
    
    def test_greater_than_or_equal(self):
        """Should compare greater than or equal."""
        money1 = Money(100, "USD")
        money2 = Money(50, "USD")
        money3 = Money(100, "USD")
        assert money1 >= money2
        assert money1 >= money3
        assert not money2 >= money1


class TestMoneyUtilities:
    """Test Money utility methods."""
    
    def test_is_zero(self):
        """Should identify zero amounts."""
        zero_money = Money(0, "USD")
        non_zero_money = Money(100, "USD")
        assert zero_money.is_zero()
        assert not non_zero_money.is_zero()
    
    def test_is_positive(self):
        """Should identify positive amounts."""
        positive_money = Money(100, "USD")
        zero_money = Money(0, "USD")
        negative_money = Money(-50, "USD")
        assert positive_money.is_positive()
        assert not zero_money.is_positive()
        assert not negative_money.is_positive()
    
    def test_is_negative(self):
        """Should identify negative amounts."""
        negative_money = Money(-50, "USD")
        zero_money = Money(0, "USD")
        positive_money = Money(100, "USD")
        assert negative_money.is_negative()
        assert not zero_money.is_negative()
        assert not positive_money.is_negative()
    
    def test_to_string_representation(self):
        """Should provide readable string representation."""
        money = Money(100.50, "USD")
        assert str(money) == "100.50 USD"
    
    def test_to_repr_representation(self):
        """Should provide developer representation."""
        money = Money(100.50, "USD")
        assert repr(money) == "Money(100.50, 'USD')"
    
    def test_hash_for_sets_and_dicts(self):
        """Should be hashable for use in sets and as dict keys."""
        money1 = Money(100, "USD")
        money2 = Money(100, "USD")
        money3 = Money(50, "USD")
        
        money_set = {money1, money2, money3}
        assert len(money_set) == 2  # money1 and money2 are equal
        
        money_dict = {money1: "first", money2: "second"}
        assert len(money_dict) == 1  # money1 and money2 have same hash


class TestMoneyClassMethods:
    """Test Money class methods and factory methods."""
    
    def test_zero_factory_method(self):
        """Should create zero money with specified currency."""
        zero_usd = Money.zero("USD")
        assert zero_usd.amount == Decimal("0")
        assert zero_usd.currency == "USD"
        assert zero_usd.is_zero()
    
    def test_from_cents_factory_method(self):
        """Should create money from cents/smallest currency unit."""
        money = Money.from_cents(12550, "USD")  # 125.50 USD
        assert money.amount == Decimal("125.50")
        assert money.currency == "USD"
    
    def test_from_string_factory_method(self):
        """Should parse money from formatted string."""
        money = Money.from_string("$125.50")
        assert money.amount == Decimal("125.50")
        assert money.currency == "USD"
        
        money_eur = Money.from_string("€99.99")
        assert money_eur.amount == Decimal("99.99")
        assert money_eur.currency == "EUR"
    
    def test_sum_money_list(self):
        """Should sum a list of money with same currency."""
        money_list = [
            Money(100, "USD"),
            Money(50, "USD"),
            Money(25, "USD")
        ]
        total = Money.sum(money_list)
        assert total.amount == Decimal("175")
        assert total.currency == "USD"
    
    def test_sum_empty_list_with_currency(self):
        """Should return zero money for empty list with specified currency."""
        total = Money.sum([], currency="USD")
        assert total.amount == Decimal("0")
        assert total.currency == "USD"
    
    def test_sum_mixed_currencies_raises_error(self):
        """Should raise error when summing mixed currencies."""
        money_list = [
            Money(100, "USD"),
            Money(50, "EUR")
        ]
        with pytest.raises(ValueError, match="All money amounts must have the same currency"):
            Money.sum(money_list)


class TestMoneyEdgeCases:
    """Test Money edge cases and error conditions."""
    
    def test_very_large_amounts(self):
        """Should handle very large amounts."""
        large_amount = Decimal("999999999999999.99")
        money = Money(large_amount, "USD")
        assert money.amount == large_amount
    
    def test_very_small_amounts(self):
        """Should handle very small amounts."""
        small_amount = Decimal("0.00000001")
        money = Money(small_amount, "USD")
        assert money.amount == small_amount
    
    def test_currency_code_validation(self):
        """Should validate currency codes."""
        # Valid 3-letter codes
        Money(100, "USD")
        Money(100, "EUR")
        Money(100, "GBP")
        
        # Invalid codes should raise ValueError
        with pytest.raises(ValueError, match="Currency code must be 3 letters"):
            Money(100, "US")
        
        with pytest.raises(ValueError, match="Currency code must be 3 letters"):
            Money(100, "DOLLAR")
    
    def test_immutability(self):
        """Should be immutable value object."""
        money = Money(100, "USD")
        
        # Should not be able to modify amount or currency
        with pytest.raises(AttributeError):
            money.amount = Decimal("200")
        
        with pytest.raises(AttributeError):
            money.currency = "EUR"
    
    def test_thread_safety(self):
        """Should be thread-safe as immutable value object."""
        # Since Money is immutable, it's inherently thread-safe
        # This test documents the expectation
        money = Money(100, "USD")
        
        # Multiple operations should not affect the original
        result1 = money + Money(50, "USD")
        result2 = money * 2
        result3 = -money
        
        # Original should be unchanged
        assert money.amount == Decimal("100")
        assert money.currency == "USD"
        
        # Results should be independent
        assert result1.amount == Decimal("150")
        assert result2.amount == Decimal("200")
        assert result3.amount == Decimal("-100")


class TestMoneyBusinessRules:
    """Test Money business rules and domain constraints."""
    
    def test_precision_constraints(self):
        """Should enforce precision constraints for currency."""
        # Most currencies have 2 decimal places
        money = Money(Decimal("100.123"), "USD")
        rounded = money.round_to_currency_precision()
        assert rounded.amount == Decimal("100.12")
    
    def test_conversion_support(self):
        """Should support currency conversion with external rates."""
        usd_money = Money(100, "USD")
        
        # Conversion should create new Money instance
        eur_money = usd_money.convert_to("EUR", exchange_rate=Decimal("0.85"))
        assert eur_money.amount == Decimal("85.00")
        assert eur_money.currency == "EUR"
        
        # Original should be unchanged
        assert usd_money.amount == Decimal("100")
        assert usd_money.currency == "USD"
    
    def test_allocation_for_splitting(self):
        """Should support allocating money into portions."""
        money = Money(100, "USD")
        
        # Split into 3 equal parts
        portions = money.allocate([1, 1, 1])
        assert len(portions) == 3
        assert all(portion.currency == "USD" for portion in portions)
        
        # Sum should equal original (handling rounding)
        total = Money.sum(portions)
        assert total == money
    
    def test_percentage_calculations(self):
        """Should support percentage-based calculations."""
        money = Money(100, "USD")
        
        # Calculate 15% tax
        tax = money.percentage(15)
        assert tax.amount == Decimal("15.00")
        assert tax.currency == "USD"
        
        # Calculate total with tax
        total_with_tax = money + tax
        assert total_with_tax.amount == Decimal("115.00")