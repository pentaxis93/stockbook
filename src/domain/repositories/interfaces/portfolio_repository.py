"""
Portfolio repository interface.

Defines the contract for portfolio data persistence operations.
"""

from abc import ABC, abstractmethod

from src.domain.entities import Portfolio


class IPortfolioRepository(ABC):
    """Abstract interface for portfolio data operations."""

    @abstractmethod
    def create(self, portfolio: Portfolio) -> str:
        """
        Create a new portfolio.

        Args:
            portfolio: Portfolio domain model

        Returns:
            ID of the created portfolio

        Raises:
            ValidationError: If portfolio data is invalid
            DatabaseError: If creation fails
        """
        pass

    @abstractmethod
    def get_by_id(self, portfolio_id: str) -> Portfolio | None:
        """
        Retrieve portfolio by ID.

        Args:
            portfolio_id: Portfolio identifier

        Returns:
            Portfolio domain model or None if not found
        """
        pass

    @abstractmethod
    def get_all_active(self) -> list[Portfolio]:
        """
        Retrieve all active portfolios.

        Returns:
            List of active Portfolio domain models
        """
        pass

    @abstractmethod
    def get_all(self) -> list[Portfolio]:
        """
        Retrieve all portfolios (active and inactive).

        Returns:
            List of all Portfolio domain models
        """
        pass

    @abstractmethod
    def update(self, portfolio_id: str, portfolio: Portfolio) -> bool:
        """
        Update existing portfolio.

        Args:
            portfolio_id: Portfolio identifier
            portfolio: Updated portfolio domain model

        Returns:
            True if update successful, False otherwise

        Raises:
            ValidationError: If portfolio data is invalid
            DatabaseError: If update fails
        """
        pass

    @abstractmethod
    def deactivate(self, portfolio_id: str) -> bool:
        """
        Deactivate portfolio (soft delete).

        Args:
            portfolio_id: Portfolio identifier

        Returns:
            True if deactivation successful, False otherwise
        """
        pass
