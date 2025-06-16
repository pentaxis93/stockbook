"""
Quantity value object for representing share quantities.

Provides validation and type safety for share quantities
used in trading operations.
"""

from typing import Union


class Quantity:
    """
    Immutable value object representing share quantities.
    
    Enforces business rules for share quantities including:
    - Must be positive integers only
    - Cannot exceed reasonable maximum limits
    - Supports arithmetic operations with validation
    """
    
    # Maximum allowed quantity (1 million shares)
    MAX_QUANTITY = 1_000_000
    
    def __init__(self, value: Union[int, str]):
        """
        Initialize Quantity with validation.
        
        Args:
            value: Share quantity (integer or string representation)
            
        Raises:
            ValueError: If quantity is invalid
        """
        # Convert string to int if needed
        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                raise ValueError("Quantity must be an integer")
        
        # Validate type
        if not isinstance(value, int):
            raise ValueError("Quantity must be an integer")
        
        # Validate positive
        if value <= 0:
            raise ValueError("Quantity must be positive")
        
        # Validate maximum
        if value > self.MAX_QUANTITY:
            raise ValueError(f"Quantity cannot exceed {self.MAX_QUANTITY:,}")
        
        # Use object.__setattr__ to bypass immutability during initialization
        object.__setattr__(self, '_value', value)
    
    @property
    def value(self) -> int:
        """Get the quantity value."""
        return self._value
    
    def __setattr__(self, name, value):
        """Prevent modification after initialization (immutability)."""
        if hasattr(self, '_value'):  # Object is already initialized
            raise AttributeError(f"Cannot modify immutable Quantity object")
        super().__setattr__(name, value)
    
    def __eq__(self, other) -> bool:
        """Check equality with another Quantity object."""
        if not isinstance(other, Quantity):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        """Make Quantity hashable for use in sets/dicts."""
        return hash(self.value)
    
    def __add__(self, other: 'Quantity') -> 'Quantity':
        """Add two Quantity objects."""
        if not isinstance(other, Quantity):
            raise TypeError("Can only add Quantity to Quantity")
        
        result_value = self.value + other.value
        return Quantity(result_value)  # Will validate maximum in constructor
    
    def __sub__(self, other: 'Quantity') -> 'Quantity':
        """Subtract two Quantity objects."""
        if not isinstance(other, Quantity):
            raise TypeError("Can only subtract Quantity from Quantity")
        
        result_value = self.value - other.value
        return Quantity(result_value)  # Will validate positive in constructor
    
    def __mul__(self, other: int) -> 'Quantity':
        """Multiply Quantity by a positive integer."""
        if not isinstance(other, int):
            raise ValueError("Can only multiply Quantity by positive integers")
        
        if other <= 0:
            raise ValueError("Can only multiply Quantity by positive integers")
        
        result_value = self.value * other
        return Quantity(result_value)  # Will validate maximum in constructor
    
    def __rmul__(self, other: int) -> 'Quantity':
        """Right multiplication (int * Quantity)."""
        return self.__mul__(other)
    
    def __truediv__(self, other: int) -> 'Quantity':
        """Divide Quantity by a positive integer."""
        if not isinstance(other, int):
            raise ValueError("Can only divide Quantity by positive integers")
        
        if other <= 0:
            raise ValueError("Can only divide Quantity by positive integers")
        
        # Check if division results in whole number
        if self.value % other != 0:
            raise ValueError("Division must result in a whole number")
        
        result_value = self.value // other
        return Quantity(result_value)  # Will validate positive in constructor
    
    def __lt__(self, other: 'Quantity') -> bool:
        """Less than comparison."""
        if not isinstance(other, Quantity):
            raise TypeError("Cannot compare Quantity with non-Quantity")
        return self.value < other.value
    
    def __le__(self, other: 'Quantity') -> bool:
        """Less than or equal comparison."""
        if not isinstance(other, Quantity):
            raise TypeError("Cannot compare Quantity with non-Quantity")
        return self.value <= other.value
    
    def __gt__(self, other: 'Quantity') -> bool:
        """Greater than comparison."""
        if not isinstance(other, Quantity):
            raise TypeError("Cannot compare Quantity with non-Quantity")
        return self.value > other.value
    
    def __ge__(self, other: 'Quantity') -> bool:
        """Greater than or equal comparison."""
        if not isinstance(other, Quantity):
            raise TypeError("Cannot compare Quantity with non-Quantity")
        return self.value >= other.value
    
    def __str__(self) -> str:
        """String representation for display."""
        if self.value == 1:
            return f"{self.value} share"
        else:
            return f"{self.value} shares"
    
    def __repr__(self) -> str:
        """Developer representation."""
        return f"Quantity({self.value})"
    
    @classmethod
    def is_valid(cls, value: Union[int, str]) -> bool:
        """
        Check if value is valid for Quantity without creating instance.
        
        Args:
            value: Value to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            cls(value)
            return True
        except (ValueError, TypeError):
            return False
    
    @classmethod
    def from_string(cls, value: str) -> 'Quantity':
        """
        Factory method for explicit string conversion.
        
        Args:
            value: String representation of quantity
            
        Returns:
            Quantity instance
        """
        return cls(value)