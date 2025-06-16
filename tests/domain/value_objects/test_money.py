"""
Tests for Money value object.

Following TDD approach - these tests define the expected behavior
before implementation.
"""

import pytest
from decimal import Decimal
from domain.value_objects.money import Money


class TestMoney:
    """Test suite for Money value object."""
    
    def test_create_money_with_valid_amount(self):
        """Should create Money with valid decimal amount."""
        money = Money(Decimal("100.50"), "USD")
        assert money.amount == Decimal("100.50")
        assert money.currency == "USD"
    
    def test_create_money_with_string_amount(self):
        """Should create Money from string amount."""
        money = Money("100.50", "USD")
        assert money.amount == Decimal("100.50")
        assert money.currency == "USD"
    
    def test_create_money_with_float_amount(self):
        """Should create Money from float amount."""
        money = Money(100.50, "USD")
        assert money.amount == Decimal("100.50")
        assert money.currency == "USD"
    
    def test_create_money_with_zero_amount(self):
        """Should allow zero amount."""
        money = Money(Decimal("0.00"), "USD")
        assert money.amount == Decimal("0.00")
    
    def test_create_money_with_negative_amount_raises_error(self):
        """Should raise error for negative amounts in trading context."""
        with pytest.raises(ValueError, match="Amount cannot be negative"):
            Money(Decimal("-10.00"), "USD")
    
    def test_create_money_with_invalid_currency_raises_error(self):
        """Should raise error for invalid currency codes."""
        with pytest.raises(ValueError, match="Currency must be a valid 3-letter code"):
            Money(Decimal("100.00"), "INVALID")
    
    def test_create_money_with_empty_currency_raises_error(self):
        """Should raise error for empty currency."""
        with pytest.raises(ValueError, match="Currency must be a valid 3-letter code"):
            Money(Decimal("100.00"), "")
    
    def test_money_equality(self):
        """Should compare Money objects for equality."""
        money1 = Money(Decimal("100.50"), "USD")
        money2 = Money(Decimal("100.50"), "USD")
        money3 = Money(Decimal("100.51"), "USD")
        money4 = Money(Decimal("100.50"), "CAD")
        
        assert money1 == money2
        assert money1 != money3  # Different amount
        assert money1 != money4  # Different currency
    
    def test_money_addition(self):
        """Should add Money objects with same currency."""
        money1 = Money(Decimal("100.50"), "USD")
        money2 = Money(Decimal("50.25"), "USD")
        result = money1 + money2
        
        assert result.amount == Decimal("150.75")
        assert result.currency == "USD"
    
    def test_money_addition_different_currency_raises_error(self):
        """Should raise error when adding different currencies."""
        money1 = Money(Decimal("100.50"), "USD")
        money2 = Money(Decimal("50.25"), "CAD")
        
        with pytest.raises(ValueError, match="Cannot perform operations on different currencies"):
            money1 + money2
    
    def test_money_subtraction(self):
        """Should subtract Money objects with same currency."""
        money1 = Money(Decimal("100.50"), "USD")
        money2 = Money(Decimal("50.25"), "USD")
        result = money1 - money2
        
        assert result.amount == Decimal("50.25")
        assert result.currency == "USD"
    
    def test_money_subtraction_negative_result_raises_error(self):
        """Should raise error if subtraction results in negative amount."""
        money1 = Money(Decimal("50.00"), "USD")
        money2 = Money(Decimal("100.00"), "USD")
        
        with pytest.raises(ValueError, match="Result cannot be negative"):
            money1 - money2
    
    def test_money_multiplication_by_scalar(self):
        """Should multiply Money by scalar values."""
        money = Money(Decimal("100.50"), "USD")
        result = money * Decimal("2.5")
        
        assert result.amount == Decimal("251.25")
        assert result.currency == "USD"
    
    def test_money_multiplication_by_integer(self):
        """Should multiply Money by integer."""
        money = Money(Decimal("100.50"), "USD")
        result = money * 2
        
        assert result.amount == Decimal("201.00")
        assert result.currency == "USD"
    
    def test_money_division_by_scalar(self):
        """Should divide Money by scalar values."""
        money = Money(Decimal("100.50"), "USD")
        result = money / Decimal("2")
        
        assert result.amount == Decimal("50.25")
        assert result.currency == "USD"
    
    def test_money_division_by_zero_raises_error(self):
        """Should raise error when dividing by zero."""
        money = Money(Decimal("100.50"), "USD")
        
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            money / Decimal("0")
    
    def test_money_comparison_operators(self):
        """Should support comparison operators."""
        money1 = Money(Decimal("100.50"), "USD")
        money2 = Money(Decimal("150.75"), "USD")
        money3 = Money(Decimal("100.50"), "USD")
        
        assert money1 < money2
        assert money2 > money1
        assert money1 <= money3
        assert money1 >= money3
    
    def test_money_comparison_different_currency_raises_error(self):
        """Should raise error when comparing different currencies."""
        money1 = Money(Decimal("100.50"), "USD")
        money2 = Money(Decimal("100.50"), "CAD")
        
        with pytest.raises(ValueError, match="Cannot compare different currencies"):
            money1 < money2
    
    def test_money_string_representation(self):
        """Should have proper string representation."""
        money = Money(Decimal("100.50"), "USD")
        assert str(money) == "100.50 USD"
    
    def test_money_repr(self):
        """Should have proper repr representation."""
        money = Money(Decimal("100.50"), "USD")
        assert repr(money) == "Money(100.50, 'USD')"
    
    def test_money_is_immutable(self):
        """Money should be immutable."""
        money = Money(Decimal("100.50"), "USD")
        
        # Attempting to modify should raise AttributeError
        with pytest.raises(AttributeError):
            money.amount = Decimal("200.00")
        
        with pytest.raises(AttributeError):
            money.currency = "CAD"
    
    def test_money_precision_handling(self):
        """Should handle decimal precision correctly."""
        money = Money(Decimal("100.123456"), "USD")
        # Should round to 2 decimal places for currency
        assert money.amount == Decimal("100.12")
    
    def test_money_zero_factory_method(self):
        """Should provide zero factory method."""
        zero_usd = Money.zero("USD")
        assert zero_usd.amount == Decimal("0.00")
        assert zero_usd.currency == "USD"
    
    def test_money_from_cents_factory_method(self):
        """Should create Money from cents/smallest currency unit."""
        money = Money.from_cents(10050, "USD")  # 100.50 USD
        assert money.amount == Decimal("100.50")
        assert money.currency == "USD"
    
    def test_money_to_cents_method(self):
        """Should convert Money to cents/smallest currency unit."""
        money = Money(Decimal("100.50"), "USD")
        assert money.to_cents() == 10050