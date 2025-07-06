"""Portfolio balance repository interface.

Defines the contract for portfolio balance data persistence operations.
"""

from abc import ABC, abstractmethod
from datetime import date

from src.domain.entities import PortfolioBalance


class IPortfolioBalanceRepository(ABC):
    """Abstract interface for portfolio balance data operations."""

    @abstractmethod
    def create(self, balance: PortfolioBalance) -> str:
        """Create or update portfolio balance for a date.

        Args:
            balance: PortfolioBalance domain model

        Returns:
            ID of the created/updated balance record

        Raises:
            ValidationError: If balance data is invalid
            DatabaseError: If operation fails
        """
        pass

    @abstractmethod
    def get_by_id(self, balance_id: str) -> PortfolioBalance | None:
        """Retrieve portfolio balance by ID.

        Args:
            balance_id: Balance record identifier

        Returns:
            PortfolioBalance domain model or None if not found
        """
        pass

    @abstractmethod
    def get_by_portfolio_and_date(
        self, portfolio_id: str, balance_date: date
    ) -> PortfolioBalance | None:
        """Retrieve portfolio balance for a specific date.

        Args:
            portfolio_id: Portfolio identifier
            balance_date: Balance date

        Returns:
            PortfolioBalance domain model or None if not found
        """
        pass

    @abstractmethod
    def get_history(
        self, portfolio_id: str, limit: int | None = None
    ) -> list[PortfolioBalance]:
        """Retrieve balance history for a portfolio.

        Args:
            portfolio_id: Portfolio identifier
            limit: Maximum number of records to return

        Returns:
            List of PortfolioBalance domain models, ordered by date (newest first)
        """
        pass

    @abstractmethod
    def get_latest_balance(self, portfolio_id: str) -> PortfolioBalance | None:
        """Retrieve the most recent balance for a portfolio.

        Args:
            portfolio_id: Portfolio identifier

        Returns:
            Latest PortfolioBalance domain model or None if not found
        """
        pass
