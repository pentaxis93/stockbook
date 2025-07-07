"""Target repository interface.

Defines the contract for target data persistence operations.
"""

from abc import ABC, abstractmethod

from src.domain.entities import Target


class ITargetRepository(ABC):
    """Abstract interface for target data operations."""

    @abstractmethod
    def create(self, target: Target) -> str:
        """Create a new target.

        Args:
            target: Target domain model

        Returns:
            ID of the created target

        Raises:
            ValidationError: If target data is invalid
            DatabaseError: If creation fails
        """

    @abstractmethod
    def get_by_id(self, target_id: str) -> Target | None:
        """Retrieve target by ID.

        Args:
            target_id: Target identifier

        Returns:
            Target domain model or None if not found
        """

    @abstractmethod
    def get_active_by_portfolio(self, portfolio_id: str) -> list[Target]:
        """Retrieve active targets for a portfolio.

        Args:
            portfolio_id: Portfolio identifier

        Returns:
            List of active Target domain models
        """

    @abstractmethod
    def get_active_by_stock(self, stock_id: str) -> list[Target]:
        """Retrieve active targets for a stock.

        Args:
            stock_id: Stock identifier

        Returns:
            List of active Target domain models
        """

    @abstractmethod
    def get_all_active(self) -> list[Target]:
        """Retrieve all active targets.

        Returns:
            List of active Target domain models
        """

    @abstractmethod
    def update(self, target_id: str, target: Target) -> bool:
        """Update existing target.

        Args:
            target_id: Target identifier
            target: Updated target domain model

        Returns:
            True if update successful, False otherwise

        Raises:
            ValidationError: If target data is invalid
            DatabaseError: If update fails
        """

    @abstractmethod
    def update_status(self, target_id: str, status: str) -> bool:
        """Update target status.

        Args:
            target_id: Target identifier
            status: New status ('active', 'hit', 'failed', 'cancelled')

        Returns:
            True if update successful, False otherwise
        """
