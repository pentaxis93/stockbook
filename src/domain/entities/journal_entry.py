"""Journal Entry entity.

Rich domain entity implementing clean architecture with value objects.
Follows Domain-Driven Design principles with business logic encapsulation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from src.domain.entities.entity import Entity
from src.domain.value_objects import JournalContent


if TYPE_CHECKING:
    from datetime import date


class JournalEntry(Entity):
    """Journal Entry entity representing notes and observations about investments.

    Rich domain entity with value objects and business logic.
    Follows clean architecture and Domain-Driven Design principles.
    """

    class Builder:
        """Builder for JournalEntry to manage multiple parameters elegantly."""

        def __init__(self) -> None:
            """Initialize builder with default values."""
            self.entry_date: date | None = None
            self.content: JournalContent | None = None
            self.portfolio_id: str | None = None
            self.stock_id: str | None = None
            self.transaction_id: str | None = None
            self.entity_id: str | None = None

        def with_entry_date(self, entry_date: date) -> Self:
            """Set the entry date."""
            self.entry_date = entry_date
            return self

        def with_content(self, content: JournalContent) -> Self:
            """Set the content."""
            self.content = content
            return self

        def with_portfolio_id(self, portfolio_id: str | None) -> Self:
            """Set the portfolio ID."""
            self.portfolio_id = portfolio_id
            return self

        def with_stock_id(self, stock_id: str | None) -> Self:
            """Set the stock ID."""
            self.stock_id = stock_id
            return self

        def with_transaction_id(self, transaction_id: str | None) -> Self:
            """Set the transaction ID."""
            self.transaction_id = transaction_id
            return self

        def with_id(self, entity_id: str | None) -> Self:
            """Set the entity ID."""
            self.entity_id = entity_id
            return self

        def build(self) -> JournalEntry:
            """Build and return the JournalEntry instance."""
            return JournalEntry(_builder_instance=self)

    def __init__(self, *, _builder_instance: JournalEntry.Builder | None = None):
        """Initialize journal entry through builder pattern."""
        if _builder_instance is None:
            raise ValueError("JournalEntry must be created through Builder")

        # Extract values from builder
        entry_date = _builder_instance.entry_date
        content = _builder_instance.content
        portfolio_id = _builder_instance.portfolio_id
        stock_id = _builder_instance.stock_id
        transaction_id = _builder_instance.transaction_id
        entity_id = _builder_instance.entity_id

        # Validate required fields
        if entry_date is None:
            raise ValueError("Entry date is required")
        if content is None:
            raise ValueError("Content is required")

        # Validate optional foreign key IDs
        if portfolio_id is not None and not portfolio_id:
            raise ValueError("Portfolio ID must be a non-empty string")
        if stock_id is not None and not stock_id:
            raise ValueError("Stock ID must be a non-empty string")
        if transaction_id is not None and not transaction_id:
            raise ValueError("Transaction ID must be a non-empty string")

        # Initialize parent
        super().__init__(id=entity_id)

        # Store validated attributes
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
