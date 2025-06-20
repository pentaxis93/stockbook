"""
JournalContent value object for the StockBook domain.

Represents journal entry content with validation rules and immutability.
"""


class JournalContent:
    """
    Value object representing journal entry content.

    Encapsulates validation logic for journal content and ensures immutability.
    Journal content must be non-empty and cannot exceed 10,000 characters.
    """

    MAX_LENGTH = 10000
    _value: str

    def __init__(self, value: str):
        """
        Initialize JournalContent with validation.

        Args:
            value: The journal content string

        Raises:
            TypeError: If value is not a string
            ValueError: If content is empty or exceeds maximum length
        """
        if not isinstance(value, str):
            raise TypeError("Journal content must be a string")

        # Strip whitespace
        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError("Journal content cannot be empty")

        if len(normalized_value) > self.MAX_LENGTH:
            raise ValueError(
                f"Journal content cannot exceed {self.MAX_LENGTH} characters"
            )

        # Store as private attribute to prevent mutation
        object.__setattr__(self, "_value", normalized_value)

    @property
    def value(self) -> str:
        """Get the journal content value."""
        return self._value

    def get_preview(self, max_length: int = 50) -> str:
        """Get a preview of the content, truncated if necessary."""
        if len(self._value) <= max_length:
            return self._value
        return self._value[:max_length] + "..."

    def word_count(self) -> int:
        """Get the word count of the content."""
        return len(self._value.split())

    def __str__(self) -> str:
        """String representation of the journal content."""
        return self._value

    def __repr__(self) -> str:
        """Developer representation of the journal content."""
        preview = self.get_preview(30)
        return f"JournalContent({preview!r})"

    def __eq__(self, other) -> bool:
        """Check equality based on value."""
        if not isinstance(other, JournalContent):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """Hash based on value for use in collections."""
        return hash(self._value)

    def __setattr__(self, name, value):
        """Prevent mutation after initialization."""
        if hasattr(self, "_value"):
            raise AttributeError("JournalContent is immutable")
        super().__setattr__(name, value)
