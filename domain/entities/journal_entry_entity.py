"""
Journal Entry entity.

Placeholder implementation for journal entry domain entity to replace
legacy Pydantic model dependency in repository interfaces.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class JournalEntryEntity:
    """
    Journal Entry entity representing notes and observations about investments.

    TODO: Implement full domain entity with business logic, validation,
    and rich behavior. This is currently a placeholder to remove
    legacy model dependencies from repository interfaces.
    """

    # Identity
    id: Optional[int] = None

    # Core attributes
    portfolio_id: Optional[int] = None
    stock_id: Optional[int] = None
    transaction_id: Optional[int] = None
    entry_date: Optional[date] = None
    content: str = ""

    def __post_init__(self):
        """Validate journal entry data after initialization."""
        if not self.content:
            raise ValueError("Journal entry content cannot be empty")

        if self.entry_date is None:
            raise ValueError("Journal entry date cannot be None")

        if len(self.content) > 10000:
            raise ValueError("Journal entry content cannot exceed 10,000 characters")

    def __str__(self) -> str:
        """String representation."""
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"JournalEntry({self.entry_date}: {preview})"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"JournalEntryEntity(id={self.id}, date={self.entry_date})"
