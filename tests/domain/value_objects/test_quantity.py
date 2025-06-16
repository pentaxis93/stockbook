"""
Tests for Quantity value object.

Following TDD approach - these tests define the expected behavior
before implementation.
"""

import pytest
from domain.value_objects.quantity import Quantity


class TestQuantity:
    """Test suite for Quantity value object."""
    
    def test_create_quantity_with_valid_positive_integer(self):
        """Should create Quantity with valid positive integer."""
        quantity = Quantity(100)
        assert quantity.value == 100
    
    def test_create_quantity_with_zero_raises_error(self):
        """Should raise error for zero quantity."""
        with pytest.raises(ValueError, match="Quantity must be positive"):
            Quantity(0)
    
    def test_create_quantity_with_negative_value_raises_error(self):
        """Should raise error for negative quantities."""
        with pytest.raises(ValueError, match="Quantity must be positive"):
            Quantity(-10)
    
    def test_create_quantity_with_float_raises_error(self):
        """Should raise error for non-integer values."""
        with pytest.raises(ValueError, match="Quantity must be an integer"):
            Quantity(100.5)
    
    def test_create_quantity_with_string_integer(self):
        """Should accept string representation of integers."""
        quantity = Quantity("100")
        assert quantity.value == 100
    
    def test_create_quantity_with_invalid_string_raises_error(self):
        """Should raise error for non-numeric strings."""
        with pytest.raises(ValueError, match="Quantity must be an integer"):
            Quantity("abc")
        
        with pytest.raises(ValueError, match="Quantity must be an integer"):
            Quantity("100.5")
    
    def test_create_quantity_with_very_large_value_raises_error(self):
        """Should raise error for unreasonably large quantities."""
        with pytest.raises(ValueError, match="Quantity cannot exceed 1,000,000"):
            Quantity(1_000_001)
    
    def test_create_quantity_accepts_maximum_value(self):
        """Should accept maximum allowed quantity."""
        quantity = Quantity(1_000_000)
        assert quantity.value == 1_000_000
    
    def test_quantity_equality(self):
        """Should compare Quantity objects for equality."""
        quantity1 = Quantity(100)
        quantity2 = Quantity(100)
        quantity3 = Quantity(200)
        
        assert quantity1 == quantity2
        assert quantity1 != quantity3
    
    def test_quantity_equality_with_non_quantity(self):
        """Should not be equal to non-Quantity objects."""
        quantity = Quantity(100)
        assert quantity != 100
        assert quantity != "100"
        assert quantity != None
    
    def test_quantity_hash(self):
        """Should be hashable for use in sets/dicts."""
        quantity1 = Quantity(100)
        quantity2 = Quantity(100)
        quantity3 = Quantity(200)
        
        # Same quantities should have same hash
        assert hash(quantity1) == hash(quantity2)
        
        # Can be used in set
        quantity_set = {quantity1, quantity2, quantity3}
        assert len(quantity_set) == 2  # 100 appears only once
    
    def test_quantity_addition(self):
        """Should add Quantity objects."""
        quantity1 = Quantity(100)
        quantity2 = Quantity(50)
        result = quantity1 + quantity2
        
        assert result.value == 150
        assert isinstance(result, Quantity)
    
    def test_quantity_addition_exceeding_maximum_raises_error(self):
        """Should raise error if addition exceeds maximum."""
        quantity1 = Quantity(800_000)
        quantity2 = Quantity(300_000)
        
        with pytest.raises(ValueError, match="Quantity cannot exceed 1,000,000"):
            quantity1 + quantity2
    
    def test_quantity_subtraction(self):
        """Should subtract Quantity objects."""
        quantity1 = Quantity(100)
        quantity2 = Quantity(30)
        result = quantity1 - quantity2
        
        assert result.value == 70
        assert isinstance(result, Quantity)
    
    def test_quantity_subtraction_resulting_in_zero_or_negative_raises_error(self):
        """Should raise error if subtraction results in zero or negative."""
        quantity1 = Quantity(100)
        quantity2 = Quantity(100)
        quantity3 = Quantity(150)
        
        with pytest.raises(ValueError, match="Quantity must be positive"):
            quantity1 - quantity2  # Would be zero
        
        with pytest.raises(ValueError, match="Quantity must be positive"):
            quantity1 - quantity3  # Would be negative
    
    def test_quantity_multiplication_by_integer(self):
        """Should multiply Quantity by integer."""
        quantity = Quantity(100)
        result = quantity * 2
        
        assert result.value == 200
        assert isinstance(result, Quantity)
    
    def test_quantity_multiplication_by_float_raises_error(self):
        """Should raise error when multiplying by float."""
        quantity = Quantity(100)
        
        with pytest.raises(ValueError, match="Can only multiply Quantity by positive integers"):
            quantity * 2.5
    
    def test_quantity_multiplication_by_negative_raises_error(self):
        """Should raise error when multiplying by negative."""
        quantity = Quantity(100)
        
        with pytest.raises(ValueError, match="Can only multiply Quantity by positive integers"):
            quantity * -2
    
    def test_quantity_multiplication_by_zero_raises_error(self):
        """Should raise error when multiplying by zero."""
        quantity = Quantity(100)
        
        with pytest.raises(ValueError, match="Can only multiply Quantity by positive integers"):
            quantity * 0
    
    def test_quantity_right_multiplication(self):
        """Should support right multiplication (int * Quantity)."""
        quantity = Quantity(100)
        result = 3 * quantity
        
        assert result.value == 300
        assert isinstance(result, Quantity)
    
    def test_quantity_division_by_integer(self):
        """Should divide Quantity by integer."""
        quantity = Quantity(100)
        result = quantity / 2
        
        assert result.value == 50
        assert isinstance(result, Quantity)
    
    def test_quantity_division_with_remainder_raises_error(self):
        """Should raise error if division doesn't result in whole number."""
        quantity = Quantity(100)
        
        with pytest.raises(ValueError, match="Division must result in a whole number"):
            quantity / 3
    
    def test_quantity_division_by_float_raises_error(self):
        """Should raise error when dividing by float."""
        quantity = Quantity(100)
        
        with pytest.raises(ValueError, match="Can only divide Quantity by positive integers"):
            quantity / 2.5
    
    def test_quantity_division_by_zero_raises_error(self):
        """Should raise error when dividing by zero."""
        quantity = Quantity(100)
        
        with pytest.raises(ValueError, match="Can only divide Quantity by positive integers"):
            quantity / 0
    
    def test_quantity_comparison_operators(self):
        """Should support comparison operators."""
        quantity1 = Quantity(100)
        quantity2 = Quantity(150)
        quantity3 = Quantity(100)
        
        assert quantity1 < quantity2
        assert quantity2 > quantity1
        assert quantity1 <= quantity3
        assert quantity1 >= quantity3
    
    def test_quantity_comparison_with_non_quantity_raises_error(self):
        """Should raise error when comparing with non-Quantity objects."""
        quantity = Quantity(100)
        
        with pytest.raises(TypeError):
            quantity < 150
        
        with pytest.raises(TypeError):
            quantity > "100"
    
    def test_quantity_string_representation(self):
        """Should have proper string representation."""
        quantity = Quantity(100)
        assert str(quantity) == "100 shares"
        
        quantity_single = Quantity(1)
        assert str(quantity_single) == "1 share"
    
    def test_quantity_repr(self):
        """Should have proper repr representation."""
        quantity = Quantity(100)
        assert repr(quantity) == "Quantity(100)"
    
    def test_quantity_is_immutable(self):
        """Quantity should be immutable."""
        quantity = Quantity(100)
        
        # Attempting to modify should raise AttributeError
        with pytest.raises(AttributeError):
            quantity.value = 200
    
    def test_quantity_from_string_factory_method(self):
        """Should provide factory method for string conversion."""
        quantity = Quantity.from_string("100")
        assert quantity.value == 100
        assert isinstance(quantity, Quantity)
    
    def test_quantity_is_valid_class_method(self):
        """Should provide class method to validate quantities without creating instance."""
        assert Quantity.is_valid(100) == True
        assert Quantity.is_valid("100") == True
        assert Quantity.is_valid(0) == False
        assert Quantity.is_valid(-10) == False
        assert Quantity.is_valid(100.5) == False
        assert Quantity.is_valid("abc") == False
        assert Quantity.is_valid(1_000_001) == False