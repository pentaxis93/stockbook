"""
Quantity value object for the shared kernel.

Provides a robust, immutable quantity representation that handles numeric
operations and business rules consistently across all domains.
"""

import decimal
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
from typing import List, Union


class Quantity:
    """
    Immutable value object representing quantities.
    
    Handles arithmetic operations, comparisons, and business rules for quantities
    in a way that's safe and consistent across all bounded contexts.
    """
    
    def __init__(self, value: Union[int, float, str, Decimal], allow_negative: bool = False):
        """
        Initialize Quantity with a numeric value.
        
        Args:
            value: Numeric value (converted to Decimal for precision)
            allow_negative: Whether to allow negative quantities
            
        Raises:
            TypeError: If value cannot be converted to Decimal
            ValueError: If value is negative and not allowed
        """
        try:
            self._value = Decimal(str(value))
        except (ValueError, TypeError, decimal.InvalidOperation) as e:
            raise TypeError(f"Value must be numeric, got {type(value).__name__}") from e
        
        self._allow_negative = allow_negative
        
        if not allow_negative and self._value < 0:
            raise ValueError("Quantity cannot be negative")
    
    @property
    def value(self) -> Decimal:
        """Get the quantity value."""
        return self._value
    
    def __str__(self) -> str:
        """String representation for display."""
        return str(self._value)
    
    def __repr__(self) -> str:
        """Developer representation."""
        return f"Quantity({self._value})"
    
    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, Quantity):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        """Hash for use in sets and as dict keys."""
        return hash(self._value)
    
    def __lt__(self, other) -> bool:
        """Less than comparison."""
        if not isinstance(other, Quantity):
            raise TypeError("Cannot compare Quantity with non-Quantity")
        return self._value < other._value
    
    def __le__(self, other) -> bool:
        """Less than or equal comparison."""
        if not isinstance(other, Quantity):
            raise TypeError("Cannot compare Quantity with non-Quantity")
        return self._value <= other._value
    
    def __gt__(self, other) -> bool:
        """Greater than comparison."""
        if not isinstance(other, Quantity):
            raise TypeError("Cannot compare Quantity with non-Quantity")
        return self._value > other._value
    
    def __ge__(self, other) -> bool:
        """Greater than or equal comparison."""
        if not isinstance(other, Quantity):
            raise TypeError("Cannot compare Quantity with non-Quantity")
        return self._value >= other._value
    
    def __add__(self, other) -> 'Quantity':
        """Add two Quantity instances or Quantity and scalar."""
        if isinstance(other, Quantity):
            result_value = self._value + other._value
        elif isinstance(other, (int, float, Decimal)):
            result_value = self._value + Decimal(str(other))
        else:
            raise TypeError("Can only add Quantity or numeric types to Quantity")
        
        return Quantity(result_value, allow_negative=self._allow_negative)
    
    def __radd__(self, other) -> 'Quantity':
        """Right addition (scalar + Quantity)."""
        return self.__add__(other)
    
    def __sub__(self, other) -> 'Quantity':
        """Subtract Quantity or scalar from this Quantity."""
        if isinstance(other, Quantity):
            result_value = self._value - other._value
        elif isinstance(other, (int, float, Decimal)):
            result_value = self._value - Decimal(str(other))
        else:
            raise TypeError("Can only subtract Quantity or numeric types from Quantity")
        
        if not self._allow_negative and result_value < 0:
            raise ValueError("Resulting quantity cannot be negative")
        
        return Quantity(result_value, allow_negative=self._allow_negative)
    
    def __mul__(self, scalar) -> 'Quantity':
        """Multiply Quantity by a scalar."""
        if isinstance(scalar, (int, float, Decimal)):
            result_value = self._value * Decimal(str(scalar))
            return Quantity(result_value, allow_negative=self._allow_negative)
        raise TypeError("Can only multiply Quantity by numeric types")
    
    def __rmul__(self, scalar) -> 'Quantity':
        """Right multiplication (scalar * Quantity)."""
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar) -> 'Quantity':
        """Divide Quantity by a scalar."""
        if isinstance(scalar, (int, float, Decimal)):
            if scalar == 0:
                raise ZeroDivisionError("Cannot divide by zero")
            result_value = self._value / Decimal(str(scalar))
            return Quantity(result_value, allow_negative=self._allow_negative)
        raise TypeError("Can only divide Quantity by numeric types")
    
    def __floordiv__(self, scalar) -> 'Quantity':
        """Floor division of Quantity by scalar."""
        if isinstance(scalar, (int, float, Decimal)):
            if scalar == 0:
                raise ZeroDivisionError("Cannot divide by zero")
            result_value = self._value // Decimal(str(scalar))
            return Quantity(result_value, allow_negative=self._allow_negative)
        raise TypeError("Can only floor divide Quantity by numeric types")
    
    def __mod__(self, scalar) -> 'Quantity':
        """Modulo operation for Quantity."""
        if isinstance(scalar, (int, float, Decimal)):
            if scalar == 0:
                raise ZeroDivisionError("Cannot divide by zero")
            result_value = self._value % Decimal(str(scalar))
            return Quantity(result_value, allow_negative=self._allow_negative)
        raise TypeError("Can only use modulo with numeric types")
    
    def __pow__(self, exponent) -> 'Quantity':
        """Power operation for Quantity."""
        if isinstance(exponent, (int, float, Decimal)):
            result_value = self._value ** Decimal(str(exponent))
            return Quantity(result_value, allow_negative=self._allow_negative)
        raise TypeError("Can only raise Quantity to numeric power")
    
    def __neg__(self) -> 'Quantity':
        """Negate Quantity."""
        if not self._allow_negative:
            raise ValueError("Negation would result in negative quantity")
        return Quantity(-self._value, allow_negative=True)
    
    def __abs__(self) -> 'Quantity':
        """Absolute value of Quantity."""
        return Quantity(abs(self._value), allow_negative=self._allow_negative)
    
    def is_zero(self) -> bool:
        """Check if quantity is zero."""
        return self._value == Decimal('0')
    
    def is_positive(self) -> bool:
        """Check if quantity is positive."""
        return self._value > Decimal('0')
    
    def is_negative(self) -> bool:
        """Check if quantity is negative."""
        return self._value < Decimal('0')
    
    def is_whole(self) -> bool:
        """Check if quantity is a whole number."""
        return self._value % 1 == 0
    
    def round(self, decimal_places: int = 0) -> 'Quantity':
        """Round quantity to specified decimal places."""
        if decimal_places < 0:
            raise ValueError("Decimal places must be non-negative")
        
        if decimal_places == 0:
            rounded_value = self._value.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        else:
            scale = Decimal('0.1') ** decimal_places
            rounded_value = self._value.quantize(scale, rounding=ROUND_HALF_UP)
        
        return Quantity(rounded_value, allow_negative=self._allow_negative)
    
    def ceiling(self) -> 'Quantity':
        """Round up to next whole number."""
        import math
        result_value = Decimal(math.ceil(float(self._value)))
        return Quantity(result_value, allow_negative=self._allow_negative)
    
    def floor(self) -> 'Quantity':
        """Round down to previous whole number."""
        import math
        result_value = Decimal(math.floor(float(self._value)))
        return Quantity(result_value, allow_negative=self._allow_negative)
    
    def split(self, parts: int) -> List['Quantity']:
        """
        Split quantity into equal parts.
        
        Handles rounding to ensure sum equals original quantity.
        """
        if parts <= 0:
            raise ValueError("Number of parts must be positive")
        
        if parts == 1:
            return [self]
        
        # Calculate base amount per part
        base_amount = self._value / Decimal(parts)
        rounded_base = base_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        # Create parts
        quantities = []
        total_allocated = Decimal('0')
        
        for i in range(parts - 1):
            quantities.append(Quantity(rounded_base, allow_negative=self._allow_negative))
            total_allocated += rounded_base
        
        # Last part gets the remainder
        remainder = self._value - total_allocated
        quantities.append(Quantity(remainder, allow_negative=self._allow_negative))
        
        return quantities
    
    def percentage_of(self, total: 'Quantity') -> Decimal:
        """Calculate what percentage this quantity is of the total."""
        if not isinstance(total, Quantity):
            raise TypeError("Total must be a Quantity")
        
        if total.is_zero():
            return Decimal('0')
        
        return (self._value / total._value) * Decimal('100')
    
    def distribute_by_ratio(self, ratios: List[Union[int, float, Decimal]]) -> List['Quantity']:
        """Distribute quantity proportionally by given ratios."""
        if not ratios:
            return []
        
        # Convert to decimals and calculate total
        decimal_ratios = [Decimal(str(ratio)) for ratio in ratios]
        total_ratio = sum(decimal_ratios)
        
        if total_ratio == 0:
            return [Quantity.zero() for _ in ratios]
        
        # Calculate proportional amounts
        quantities = []
        remaining = self._value
        
        for i, ratio in enumerate(decimal_ratios[:-1]):  # All but last
            portion = (self._value * ratio / total_ratio).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            quantities.append(Quantity(portion, allow_negative=self._allow_negative))
            remaining -= portion
        
        # Last portion gets the remainder
        quantities.append(Quantity(remaining, allow_negative=self._allow_negative))
        
        return quantities
    
    def convert_units(self, conversion_factor: Decimal) -> 'Quantity':
        """Convert to different units using conversion factor."""
        converted_value = self._value * conversion_factor
        return Quantity(converted_value, allow_negative=self._allow_negative)
    
    def is_within_range(self, min_value: Union[int, float, Decimal], 
                       max_value: Union[int, float, Decimal]) -> bool:
        """Check if quantity is within specified range."""
        min_decimal = Decimal(str(min_value))
        max_decimal = Decimal(str(max_value))
        return min_decimal <= self._value <= max_decimal
    
    @classmethod
    def zero(cls) -> 'Quantity':
        """Create zero quantity."""
        return cls(Decimal('0'))
    
    @classmethod
    def one(cls) -> 'Quantity':
        """Create unit quantity."""
        return cls(Decimal('1'))
    
    @classmethod
    def from_string(cls, quantity_str: str, allow_negative: bool = False) -> 'Quantity':
        """Parse quantity from string."""
        try:
            value = Decimal(quantity_str.strip())
            return cls(value, allow_negative=allow_negative)
        except ValueError as e:
            raise ValueError(f"Cannot parse quantity from '{quantity_str}'") from e
    
    @classmethod
    def from_fraction(cls, numerator: int, denominator: int, 
                     allow_negative: bool = False) -> 'Quantity':
        """Create quantity from fraction."""
        if denominator == 0:
            raise ZeroDivisionError("Denominator cannot be zero")
        
        fraction = Fraction(numerator, denominator)
        value = Decimal(fraction.numerator) / Decimal(fraction.denominator)
        return cls(value, allow_negative=allow_negative)
    
    @classmethod
    def sum(cls, quantities: List['Quantity'], allow_negative: bool = False) -> 'Quantity':
        """Sum a list of quantities."""
        if not quantities:
            return cls.zero()
        
        total_value = sum(qty.value for qty in quantities)
        return cls(total_value, allow_negative=allow_negative)
    
    @classmethod
    def max(cls, quantities: List['Quantity']) -> 'Quantity':
        """Find maximum quantity from list."""
        if not quantities:
            raise ValueError("Cannot find max of empty list")
        
        max_qty = quantities[0]
        for qty in quantities[1:]:
            if qty > max_qty:
                max_qty = qty
        return max_qty
    
    @classmethod
    def min(cls, quantities: List['Quantity']) -> 'Quantity':
        """Find minimum quantity from list."""
        if not quantities:
            raise ValueError("Cannot find min of empty list")
        
        min_qty = quantities[0]
        for qty in quantities[1:]:
            if qty < min_qty:
                min_qty = qty
        return min_qty