"""Transaction repository interface.

Defines the contract for transaction data persistence operations.
"""

from abc import ABC, abstractmethod
from datetime import date

from src.domain.entities import Transaction


class ITransactionRepository(ABC):
    """Abstract interface for transaction data operations."""

    @abstractmethod
    def create(self, transaction: Transaction) -> str:
        """Create a new transaction.

        Args:
            transaction: Transaction domain model

        Returns:
            ID of the created transaction

        Raises:
            ValidationError: If transaction data is invalid
            BusinessLogicError: If transaction violates business rules
            DatabaseError: If creation fails
        """
        pass

    @abstractmethod
    def get_by_id(self, transaction_id: str) -> Transaction | None:
        """Retrieve transaction by ID.

        Args:
            transaction_id: Transaction identifier

        Returns:
            Transaction domain model or None if not found
        """
        pass

    @abstractmethod
    def get_by_portfolio(
        self, portfolio_id: str, limit: int | None = None
    ) -> list[Transaction]:
        """Retrieve transactions for a specific portfolio.

        Args:
            portfolio_id: Portfolio identifier
            limit: Maximum number of transactions to return

        Returns:
            List of Transaction domain models, ordered by date (newest first)
        """
        pass

    @abstractmethod
    def get_by_stock(
        self, stock_id: str, portfolio_id: str | None = None
    ) -> list[Transaction]:
        """Retrieve transactions for a specific stock.

        Args:
            stock_id: Stock identifier
            portfolio_id: Optional portfolio filter

        Returns:
            List of Transaction domain models
        """
        pass

    @abstractmethod
    def get_by_date_range(
        self, start_date: date, end_date: date, portfolio_id: str | None = None
    ) -> list[Transaction]:
        """Retrieve transactions within a date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            portfolio_id: Optional portfolio filter

        Returns:
            List of Transaction domain models
        """
        pass

    @abstractmethod
    def update(self, transaction_id: str, transaction: Transaction) -> bool:
        """Update existing transaction.

        Args:
            transaction_id: Transaction identifier
            transaction: Updated transaction domain model

        Returns:
            True if update successful, False otherwise

        Raises:
            ValidationError: If transaction data is invalid
            BusinessLogicError: If update violates business rules
            DatabaseError: If update fails
        """
        pass

    @abstractmethod
    def delete(self, transaction_id: str) -> bool:
        """Delete transaction by ID.

        Args:
            transaction_id: Transaction identifier

        Returns:
            True if deletion successful, False otherwise

        Raises:
            DatabaseError: If deletion fails
        """
        pass
