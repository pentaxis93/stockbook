"""Journal repository interface.

Defines the contract for journal entry data persistence operations.
"""

from abc import ABC, abstractmethod
from datetime import date

from src.domain.entities import JournalEntry


class IJournalRepository(ABC):
    """Abstract interface for journal entry data operations."""

    @abstractmethod
    def create(self, entry: JournalEntry) -> str:
        """Create a new journal entry.

        Args:
            entry: JournalEntry domain model

        Returns:
            ID of the created entry

        Raises:
            ValidationError: If entry data is invalid
            DatabaseError: If creation fails
        """

    @abstractmethod
    def get_by_id(self, entry_id: str) -> JournalEntry | None:
        """Retrieve journal entry by ID.

        Args:
            entry_id: Entry identifier

        Returns:
            JournalEntry domain model or None if not found
        """

    @abstractmethod
    def get_recent(self, limit: int | None = None) -> list[JournalEntry]:
        """Retrieve recent journal entries.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of JournalEntry domain models, ordered by date (newest first)
        """

    @abstractmethod
    def get_by_portfolio(
        self,
        portfolio_id: str,
        limit: int | None = None,
    ) -> list[JournalEntry]:
        """Retrieve journal entries for a specific portfolio.

        Args:
            portfolio_id: Portfolio identifier
            limit: Maximum number of entries to return

        Returns:
            List of JournalEntry domain models
        """

    @abstractmethod
    def get_by_stock(
        self,
        stock_id: str,
        limit: int | None = None,
    ) -> list[JournalEntry]:
        """Retrieve journal entries for a specific stock.

        Args:
            stock_id: Stock identifier
            limit: Maximum number of entries to return

        Returns:
            List of JournalEntry domain models
        """

    @abstractmethod
    def get_by_transaction(self, transaction_id: str) -> list[JournalEntry]:
        """Retrieve journal entries for a specific transaction.

        Args:
            transaction_id: Transaction identifier

        Returns:
            List of JournalEntry domain models
        """

    @abstractmethod
    def get_by_date_range(self, start_date: date, end_date: date) -> list[JournalEntry]:
        """Retrieve journal entries within a date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            List of JournalEntry domain models
        """

    @abstractmethod
    def update(self, entry_id: str, entry: JournalEntry) -> bool:
        """Update existing journal entry.

        Args:
            entry_id: Entry identifier
            entry: Updated entry domain model

        Returns:
            True if update successful, False otherwise

        Raises:
            ValidationError: If entry data is invalid
            DatabaseError: If update fails
        """

    @abstractmethod
    def delete(self, entry_id: str) -> bool:
        """Delete journal entry by ID.

        Args:
            entry_id: Entry identifier

        Returns:
            True if deletion successful, False otherwise

        Raises:
            DatabaseError: If deletion fails
        """
