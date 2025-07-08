"""Position repository interface.

Defines the contract for position data persistence operations.
"""

from abc import ABC, abstractmethod

from src.domain.entities import Position


class IPositionRepository(ABC):
    """Abstract interface for position data operations."""

    @abstractmethod
    def create(self, position: Position) -> str:
        """Create a new position.

        Args:
            position: Position domain model

        Returns:
            ID of the created position

        Raises:
            ValidationError: If position data is invalid
            BusinessLogicError: If position violates business rules
            DatabaseError: If creation fails
        """

    @abstractmethod
    def update(self, position_id: str, position: Position) -> bool:
        """Update existing position.

        Args:
            position_id: Position identifier
            position: Updated position domain model

        Returns:
            True if update successful, False otherwise

        Raises:
            ValidationError: If position data is invalid
            BusinessLogicError: If update violates business rules
            DatabaseError: If update fails
        """

    @abstractmethod
    def get_by_id(self, position_id: str) -> Position | None:
        """Retrieve position by ID.

        Args:
            position_id: Position identifier

        Returns:
            Position domain model or None if not found
        """

    @abstractmethod
    def get_by_portfolio_and_stock(
        self,
        portfolio_id: str,
        stock_id: str,
    ) -> Position | None:
        """Retrieve position by portfolio and stock combination.

        Args:
            portfolio_id: Portfolio identifier
            stock_id: Stock identifier

        Returns:
            Position domain model or None if not found
        """

    @abstractmethod
    def get_by_portfolio(self, portfolio_id: str) -> list[Position]:
        """Retrieve all positions for a specific portfolio.

        Args:
            portfolio_id: Portfolio identifier

        Returns:
            List of Position domain models for the portfolio
        """

    @abstractmethod
    def delete(self, position_id: str) -> bool:
        """Delete position by ID.

        Args:
            position_id: Position identifier

        Returns:
            True if deletion successful, False otherwise

        Raises:
            DatabaseError: If deletion fails
        """

    @abstractmethod
    def delete_by_portfolio_and_stock(
        self,
        portfolio_id: str,
        stock_id: str,
    ) -> bool:
        """Delete position by portfolio and stock combination.

        Args:
            portfolio_id: Portfolio identifier
            stock_id: Stock identifier

        Returns:
            True if deletion successful, False otherwise

        Raises:
            DatabaseError: If deletion fails
        """
