"""JournalContent value object for the StockBook domain.

Represents journal entry content with validation rules and immutability.
"""

from .notes import BaseTextValueObject


class JournalContent(BaseTextValueObject):
    """Value object representing journal entry content.

    Encapsulates validation logic for journal content and ensures immutability.
    Journal content must be non-empty and cannot exceed 10,000 characters.
    """

    MAX_LENGTH = 10000

    def __init__(self, value: str) -> None:
        """Initialize JournalContent with validation.

        Args:
            value: The journal content string

        Raises:
            TypeError: If value is not a string
            ValueError: If content is empty or exceeds maximum length
        """
        try:
            super().__init__(value, max_length=self.MAX_LENGTH, allow_empty=False)
        except ValueError as e:
            if "cannot be empty" in str(e):
                msg = "Journal content cannot be empty"
                raise ValueError(msg) from e
            if "cannot exceed" in str(e):
                msg = f"Journal content cannot exceed {self.MAX_LENGTH} characters"
                raise ValueError(msg) from e
            raise

    def get_preview(self, max_length: int = 50) -> str:
        """Get a preview of the content, truncated if necessary."""
        if len(self._value) <= max_length:
            return self._value
        return self._value[:max_length] + "..."

    def word_count(self) -> int:
        """Get the word count of the content."""
        return len(self._value.split())

    def __repr__(self) -> str:
        """Developer representation of the journal content."""
        preview = self.get_preview(30)
        return f"JournalContent({preview!r})"
