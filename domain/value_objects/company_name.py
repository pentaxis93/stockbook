"""
CompanyName value object for the StockBook domain.

Represents a company name with validation rules and immutability.
"""


class CompanyName:
    """
    Value object representing a company name.

    Encapsulates validation logic for company names and ensures immutability.
    """

    MAX_LENGTH = 200
    _value: str

    def __init__(self, value: str):
        """
        Initialize CompanyName with validation.

        Args:
            value: The company name string

        Raises:
            ValueError: If name exceeds maximum length
        """
        # Strip whitespace
        normalized_value = value.strip()

        # Validate length
        if len(normalized_value) > self.MAX_LENGTH:
            raise ValueError(f"Company name cannot exceed {self.MAX_LENGTH} characters")

        # Store as private attribute to prevent mutation
        object.__setattr__(self, "_value", normalized_value)

    @property
    def value(self) -> str:
        """Get the company name value."""
        return self._value

    def __str__(self) -> str:
        """String representation of the company name."""
        return self._value

    def __repr__(self) -> str:
        """Developer representation of the company name."""
        return f"CompanyName({self._value!r})"

    def __eq__(self, other) -> bool:
        """Check equality based on value."""
        if not isinstance(other, CompanyName):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """Hash based on value for use in collections."""
        return hash(self._value)

    def __setattr__(self, name, value):
        """Prevent mutation after initialization."""
        if hasattr(self, "_value"):
            raise AttributeError("CompanyName is immutable")
        super().__setattr__(name, value)
