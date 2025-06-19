"""
SQLite implementation of the target repository interface.

Provides concrete implementation using SQLite database operations
while fulfilling the domain repository contract.
"""

import sqlite3
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from domain.entities.target_entity import TargetEntity
from domain.repositories.interfaces import ITargetRepository
from infrastructure.persistence.interfaces import IDatabaseConnection
from shared_kernel.value_objects import Money


class SqliteTargetRepository(ITargetRepository):
    """
    SQLite-based implementation of the target repository.

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

    def create(self, target: TargetEntity) -> int:
        """
        Create a new target record in the database.

        Args:
            target: Target entity to persist

        Returns:
            Database ID of the created target

        Raises:
            ValueError: If target data is invalid
            DatabaseError: If creation fails
        """
        with self.db_connection.transaction() as conn:
            cursor = conn.execute(
                """
                INSERT INTO target (stock_id, portfolio_id, pivot_price, failure_price, notes, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    target.stock_id,
                    target.portfolio_id,
                    float(target.pivot_price.amount) if target.pivot_price else 0.0,
                    float(target.failure_price.amount) if target.failure_price else 0.0,
                    target.notes.value or "",
                    target.status.value,
                ),
            )
            return cursor.lastrowid or 0

    def get_by_id(self, target_id: int) -> Optional[TargetEntity]:
        """
        Retrieve target by database ID.

        Args:
            target_id: Database ID to search for

        Returns:
            Target entity if found, None otherwise
        """
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT id, stock_id, portfolio_id, pivot_price, failure_price, notes, status, created_at, updated_at
                FROM target 
                WHERE id = ?
                """,
                (target_id,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return self._row_to_entity(row)
        finally:
            # Only close if not in a transactional context
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def get_active_by_portfolio(self, portfolio_id: int) -> List[TargetEntity]:
        """
        Retrieve active targets for a portfolio.

        Args:
            portfolio_id: Portfolio identifier

        Returns:
            List of active Target domain models
        """
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT id, stock_id, portfolio_id, pivot_price, failure_price, notes, status, created_at, updated_at
                FROM target 
                WHERE portfolio_id = ? AND status = 'active'
                ORDER BY created_at DESC
                """,
                (portfolio_id,),
            )
            rows = cursor.fetchall()

            return [self._row_to_entity(row) for row in rows]
        finally:
            # Only close if not in a transactional context
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def get_active_by_stock(self, stock_id: int) -> List[TargetEntity]:
        """
        Retrieve active targets for a stock.

        Args:
            stock_id: Stock identifier

        Returns:
            List of active Target domain models
        """
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT id, stock_id, portfolio_id, pivot_price, failure_price, notes, status, created_at, updated_at
                FROM target 
                WHERE stock_id = ? AND status = 'active'
                ORDER BY created_at DESC
                """,
                (stock_id,),
            )
            rows = cursor.fetchall()

            return [self._row_to_entity(row) for row in rows]
        finally:
            # Only close if not in a transactional context
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def get_all_active(self) -> List[TargetEntity]:
        """
        Retrieve all active targets.

        Returns:
            List of active Target domain models
        """
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT id, stock_id, portfolio_id, pivot_price, failure_price, notes, status, created_at, updated_at
                FROM target 
                WHERE status = 'active'
                ORDER BY created_at DESC
                """
            )
            rows = cursor.fetchall()

            return [self._row_to_entity(row) for row in rows]
        finally:
            # Only close if not in a transactional context
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def update(self, target_id: int, target: TargetEntity) -> bool:
        """
        Update an existing target record.

        Args:
            target_id: Database ID of target to update
            target: Target entity with updated data

        Returns:
            True if target was updated, False if not found
        """
        with self.db_connection.transaction() as conn:
            cursor = conn.execute(
                """
                UPDATE target 
                SET stock_id = ?, portfolio_id = ?, pivot_price = ?, failure_price = ?, 
                    notes = ?, status = ?
                WHERE id = ?
                """,
                (
                    target.stock_id,
                    target.portfolio_id,
                    float(target.pivot_price.amount) if target.pivot_price else 0.0,
                    float(target.failure_price.amount) if target.failure_price else 0.0,
                    target.notes.value or "",
                    target.status.value,
                    target_id,
                ),
            )
            return cursor.rowcount > 0

    def update_status(self, target_id: int, status: str) -> bool:
        """
        Update target status.

        Args:
            target_id: Target identifier
            status: New status ('active', 'hit', 'failed', 'cancelled')

        Returns:
            True if update successful, False otherwise
        """
        with self.db_connection.transaction() as conn:
            cursor = conn.execute(
                """
                UPDATE target 
                SET status = ?
                WHERE id = ?
                """,
                (status, target_id),
            )
            return cursor.rowcount > 0

    def _row_to_entity(self, row: sqlite3.Row) -> TargetEntity:
        """
        Convert database row to domain entity.

        Args:
            row: SQLite row with target data

        Returns:
            Target entity populated from row data
        """
        # Parse created date
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

        # Provide default date if none available
        if created_date is None:
            created_date = date.today()

        from domain.value_objects import Notes, TargetStatus

        entity = TargetEntity(
            portfolio_id=row["portfolio_id"],
            stock_id=row["stock_id"],
            pivot_price=Money(
                Decimal(str(row["pivot_price"])), "USD"
            ),  # TODO: Store currency in DB
            failure_price=Money(
                Decimal(str(row["failure_price"])), "USD"
            ),  # TODO: Store currency in DB
            status=TargetStatus(row["status"]),
            created_date=created_date,
            notes=Notes(row["notes"] or ""),
            target_id=row["id"],
        )
        return entity
