"""
Notes value object for the StockBook domain.

Represents notes/comments with validation rules and immutability.
"""


class Notes:
    """
    Value object representing notes/comments.

    Encapsulates validation logic for notes and ensures immutability.
    """

    MAX_LENGTH = 1000
    _value: str

    def __init__(self, value: str):
        """
        Initialize Notes with validation.

        Args:
            value: The notes string

        Raises:
            ValueError: If notes exceed maximum length
        """
        # Strip whitespace
        normalized_value = value.strip()

        # Validate length
        if len(normalized_value) > self.MAX_LENGTH:
            raise ValueError(f"Notes cannot exceed {self.MAX_LENGTH} characters")

        # Store as private attribute to prevent mutation
        object.__setattr__(self, "_value", normalized_value)

    @property
    def value(self) -> str:
        """Get the notes value."""
        return self._value

    def has_content(self) -> bool:
        """
        Check if notes have content.

        Returns:
            True if notes have non-empty content, False otherwise
        """
        return bool(self._value)

    def __str__(self) -> str:
        """String representation of the notes."""
        return self._value

    def __repr__(self) -> str:
        """Developer representation of the notes."""
        return f"Notes({self._value!r})"

    def __eq__(self, other) -> bool:
        """Check equality based on value."""
        if not isinstance(other, Notes):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """Hash based on value for use in collections."""
        return hash(self._value)

    def __setattr__(self, name, value):
        """Prevent mutation after initialization."""
        if hasattr(self, "_value"):
            raise AttributeError("Notes is immutable")
        super().__setattr__(name, value)
