"""
Journal Entry entity.

Rich domain entity implementing clean architecture with value objects.
Follows Domain-Driven Design principles with business logic encapsulation.
"""

from datetime import date

from src.domain.entities.entity import Entity
from src.domain.value_objects import JournalContent


class JournalEntry(Entity):
    """
    Journal Entry entity representing notes and observations about investments.

    Rich domain entity with value objects and business logic.
    Follows clean architecture and Domain-Driven Design principles.
    """

    def __init__(
        # Rationale: JournalEntry captures investment notes and observations.
        # Parameters represent the entry essentials (date, content) and flexible
        # references to related entities (portfolio/stock/transaction). This design
        # allows journal entries to be associated with various investment contexts.
        self,
        entry_date: date,
        content: JournalContent,
        portfolio_id: str | None = None,
        stock_id: str | None = None,
        transaction_id: str | None = None,
        id: str | None = None,
    ):
        """Initialize journal entry with required value objects and validation."""
        # Validate optional foreign key IDs
        if portfolio_id is not None and not portfolio_id:
            raise ValueError("Portfolio ID must be a non-empty string")
        if stock_id is not None and not stock_id:
            raise ValueError("Stock ID must be a non-empty string")
        if transaction_id is not None and not transaction_id:
            raise ValueError("Transaction ID must be a non-empty string")

        # Store validated attributes
        super().__init__(id=id)
        self._entry_date = entry_date
        self._content = content
        self._portfolio_id = portfolio_id
        self._stock_id = stock_id
        self._transaction_id = transaction_id

    # Core attributes
    @property
    def entry_date(self) -> date:
        """Get entry date."""
        return self._entry_date

    @property
    def content(self) -> JournalContent:
        """Get entry content."""
        return self._content

    @property
    def portfolio_id(self) -> str | None:
        """Get portfolio ID."""
        return self._portfolio_id

    @property
    def stock_id(self) -> str | None:
        """Get stock ID."""
        return self._stock_id

    @property
    def transaction_id(self) -> str | None:
        """Get transaction ID."""
        return self._transaction_id

    # Business methods
    def is_related_to_portfolio(self) -> bool:
        """Check if entry is related to a portfolio."""
        return self._portfolio_id is not None

    def is_related_to_stock(self) -> bool:
        """Check if entry is related to a stock."""
        return self._stock_id is not None

    def is_related_to_transaction(self) -> bool:
        """Check if entry is related to a transaction."""
        return self._transaction_id is not None

    def get_content_preview(self, max_length: int = 50) -> str:
        """Get a preview of the content."""
        return self._content.get_preview(max_length)

    def update_content(self, content: JournalContent | str) -> None:
        """Update entry content."""
        if isinstance(content, str):
            self._content = JournalContent(content)
        else:
            self._content = content

    # Representation

    def __str__(self) -> str:
        """String representation."""
        preview = self._content.get_preview(50)
        return f"JournalEntry({self._entry_date}: {preview})"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"JournalEntry(date={self._entry_date})"
