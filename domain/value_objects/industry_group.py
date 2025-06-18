"""
IndustryGroup value object for the StockBook domain.

Represents an industry group classification with validation rules and immutability.
"""


class IndustryGroup:
    """
    Value object representing an industry group.

    Encapsulates validation logic for industry groups and ensures immutability.
    """

    MAX_LENGTH = 100

    def __init__(self, value: str):
        """
        Initialize IndustryGroup with validation.

        Args:
            value: The industry group string

        Raises:
            ValueError: If industry group exceeds maximum length
        """
        # Strip whitespace
        normalized_value = value.strip()

        # Validate length
        if len(normalized_value) > self.MAX_LENGTH:
            raise ValueError(
                f"Industry group cannot exceed {self.MAX_LENGTH} characters"
            )

        # Store as private attribute to prevent mutation
        object.__setattr__(self, "_value", normalized_value)

    @property
    def value(self) -> str:
        """Get the industry group value."""
        return self._value

    def __str__(self) -> str:
        """String representation of the industry group."""
        return self._value

    def __repr__(self) -> str:
        """Developer representation of the industry group."""
        return f"IndustryGroup({self._value!r})"

    def __eq__(self, other) -> bool:
        """Check equality based on value."""
        if not isinstance(other, IndustryGroup):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """Hash based on value for use in collections."""
        return hash(self._value)

    def __setattr__(self, name, value):
        """Prevent mutation after initialization."""
        if hasattr(self, "_value"):
            raise AttributeError("IndustryGroup is immutable")
        super().__setattr__(name, value)
