"""
SQLite implementation of the portfolio repository interface.

Provides concrete implementation using SQLite database operations
while fulfilling the domain repository contract.
"""

import sqlite3
from datetime import datetime
from typing import List, Optional

from src.domain.entities.portfolio_entity import PortfolioEntity
from src.domain.repositories.interfaces import IPortfolioRepository
from src.domain.value_objects import Notes, PortfolioName
from src.infrastructure.persistence.interfaces import IDatabaseConnection


class SqlitePortfolioRepository(IPortfolioRepository):
    """
    SQLite-based implementation of the portfolio repository.

    Maps between domain entities and database records while maintaining
    the repository pattern and clean architecture boundaries.
    """

    def __init__(self, db_connection: IDatabaseConnection):
        """
        Initialize repository with database connection.

        Args:
            db_connection: Database connection manager
        """
        self.db_connection = db_connection

    def create(self, portfolio: PortfolioEntity) -> str:
        """
        Create a new portfolio record in the database.

        Args:
            portfolio: Portfolio entity to persist

        Returns:
            Database ID of the created portfolio

        Raises:
            ValueError: If portfolio data is invalid
        """
        with self.db_connection.transaction() as conn:
            _ = conn.execute(
                """
                    INSERT INTO portfolio (id, name, description, max_positions, max_risk_per_trade, is_active)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                (
                    portfolio.id,
                    portfolio.name.value,
                    portfolio.description.value if portfolio.description else None,
                    10,  # Default max positions
                    2.0,  # Default 2% max risk
                    portfolio.is_active,
                ),
            )
            return portfolio.id

    def get_by_id(self, portfolio_id: str) -> Optional[PortfolioEntity]:
        """
        Retrieve portfolio by database ID.

        Args:
            portfolio_id: Database ID to search for

        Returns:
            Portfolio entity if found, None otherwise
        """
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT id, name, description, max_positions, max_risk_per_trade, is_active, 
                       created_at, updated_at
                FROM portfolio 
                WHERE id = ?
                """,
                (portfolio_id,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return self._row_to_entity(row)
        finally:
            # Only close if not in a transactional context
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def get_all_active(self) -> List[PortfolioEntity]:
        """
        Retrieve all active portfolios.

        Returns:
            List of active Portfolio domain models
        """
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT id, name, description, max_positions, max_risk_per_trade, is_active, 
                       created_at, updated_at
                FROM portfolio 
                WHERE is_active = 1
                ORDER BY name
                """
            )
            rows = cursor.fetchall()

            return [self._row_to_entity(row) for row in rows]
        finally:
            # Only close if not in a transactional context
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def get_all(self) -> List[PortfolioEntity]:
        """
        Retrieve all portfolios (active and inactive).

        Returns:
            List of all Portfolio domain models
        """
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT id, name, description, max_positions, max_risk_per_trade, is_active, 
                       created_at, updated_at
                FROM portfolio 
                ORDER BY name
                """
            )
            rows = cursor.fetchall()

            return [self._row_to_entity(row) for row in rows]
        finally:
            # Only close if not in a transactional context
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def update(self, portfolio_id: str, portfolio: PortfolioEntity) -> bool:
        """
        Update an existing portfolio record.

        Args:
            portfolio_id: Database ID of portfolio to update
            portfolio: Portfolio entity with updated data

        Returns:
            True if portfolio was updated, False if not found
        """
        with self.db_connection.transaction() as conn:
            cursor = conn.execute(
                """
                UPDATE portfolio 
                SET name = ?, description = ?, max_positions = ?, max_risk_per_trade = ?, is_active = ?
                WHERE id = ?
                """,
                (
                    portfolio.name.value,
                    portfolio.description.value if portfolio.description else None,
                    10,  # Default max positions
                    2.0,  # Default 2% max risk
                    portfolio.is_active,
                    portfolio_id,
                ),
            )
            return cursor.rowcount > 0

    def deactivate(self, portfolio_id: str) -> bool:
        """
        Deactivate portfolio (soft delete).

        Args:
            portfolio_id: Portfolio identifier

        Returns:
            True if deactivation successful, False otherwise
        """
        with self.db_connection.transaction() as conn:
            cursor = conn.execute(
                """
                UPDATE portfolio 
                SET is_active = 0
                WHERE id = ?
                """,
                (portfolio_id,),
            )
            return cursor.rowcount > 0

    def _row_to_entity(self, row: sqlite3.Row) -> PortfolioEntity:
        """
        Convert database row to domain entity.

        Args:
            row: SQLite row with portfolio data

        Returns:
            Portfolio entity populated from row data
        """
        created_date = None
        if row["created_at"]:
            try:
                # Parse SQLite timestamp to date
                created_datetime = datetime.fromisoformat(
                    row["created_at"].replace("Z", "+00:00")
                )
                created_date = created_datetime.date()
            except (ValueError, AttributeError):
                created_date = None

        return PortfolioEntity(
            id=row["id"],
            name=PortfolioName(row["name"]),
            description=Notes(row["description"] or ""),
            created_date=created_date,
            is_active=bool(row["is_active"]),
        )
