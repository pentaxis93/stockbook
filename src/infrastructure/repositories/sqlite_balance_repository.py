"""
SQLite implementation of the portfolio balance repository interface.

Provides concrete implementation using SQLite database operations
while fulfilling the domain repository contract.
"""

import sqlite3
from datetime import date
from decimal import Decimal
from typing import Any, List, Optional

from src.domain.entities.portfolio_balance_entity import PortfolioBalanceEntity
from src.domain.repositories.interfaces import IPortfolioBalanceRepository
from src.domain.value_objects import Money
from src.infrastructure.persistence.interfaces import IDatabaseConnection


class SqlitePortfolioBalanceRepository(IPortfolioBalanceRepository):
    """
    SQLite-based implementation of the portfolio balance repository.

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

    def create(self, balance: PortfolioBalanceEntity) -> str:
        """
        Create or update portfolio balance for a date.

        Args:
            balance: PortfolioBalanceEntity domain model

        Returns:
            ID of the created/updated balance record
        """
        with self.db_connection.transaction() as conn:
            # Try to insert, replace if exists
            _ = conn.execute(
                """
                INSERT OR REPLACE INTO portfolio_balance 
                (id, portfolio_id, balance_date, withdrawals, deposits, final_balance, index_change)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    balance.id,
                    balance.portfolio_id,
                    balance.balance_date.isoformat() if balance.balance_date else "",
                    float(balance.withdrawals.amount) if balance.withdrawals else 0.0,
                    float(balance.deposits.amount) if balance.deposits else 0.0,
                    (
                        float(balance.final_balance.amount)
                        if balance.final_balance
                        else 0.0
                    ),
                    balance.index_change.value if balance.index_change else None,
                ),
            )
            return balance.id

    def get_by_id(self, balance_id: str) -> Optional[PortfolioBalanceEntity]:
        """
        Retrieve portfolio balance by ID.

        Args:
            balance_id: Balance record identifier

        Returns:
            PortfolioBalance domain model or None if not found
        """
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT id, portfolio_id, balance_date, withdrawals, deposits, final_balance, index_change, created_at
                FROM portfolio_balance 
                WHERE id = ?
                """,
                (balance_id,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return self._row_to_entity(row)
        finally:
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def get_by_portfolio_and_date(
        self, portfolio_id: str, balance_date: date
    ) -> Optional[PortfolioBalanceEntity]:
        """
        Retrieve portfolio balance for a specific date.

        Args:
            portfolio_id: Portfolio identifier
            balance_date: Balance date

        Returns:
            PortfolioBalance domain model or None if not found
        """
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT id, portfolio_id, balance_date, withdrawals, deposits, final_balance, index_change, created_at
                FROM portfolio_balance 
                WHERE portfolio_id = ? AND balance_date = ?
                """,
                (portfolio_id, balance_date.isoformat()),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return self._row_to_entity(row)
        finally:
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def get_history(
        self, portfolio_id: str, limit: Optional[int] = None
    ) -> List[PortfolioBalanceEntity]:
        """
        Retrieve balance history for a portfolio.

        Args:
            portfolio_id: Portfolio identifier
            limit: Maximum number of records to return

        Returns:
            List of PortfolioBalance domain models, ordered by date (newest first)
        """
        conn = self.db_connection.get_connection()
        try:
            query = """
                SELECT id, portfolio_id, balance_date, withdrawals, deposits, final_balance, index_change, created_at
                FROM portfolio_balance 
                WHERE portfolio_id = ?
                ORDER BY balance_date DESC
            """

            params: List[Any] = [portfolio_id]
            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)

            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

            return [self._row_to_entity(row) for row in rows]
        finally:
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def get_latest_balance(self, portfolio_id: str) -> Optional[PortfolioBalanceEntity]:
        """
        Retrieve the most recent balance for a portfolio.

        Args:
            portfolio_id: Portfolio identifier

        Returns:
            Latest PortfolioBalance domain model or None if not found
        """
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT id, portfolio_id, balance_date, withdrawals, deposits, final_balance, index_change, created_at
                FROM portfolio_balance 
                WHERE portfolio_id = ?
                ORDER BY balance_date DESC
                LIMIT 1
                """,
                (portfolio_id,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return self._row_to_entity(row)
        finally:
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def _row_to_entity(self, row: sqlite3.Row) -> PortfolioBalanceEntity:
        """
        Convert database row to domain entity.

        Args:
            row: SQLite row with balance data

        Returns:
            PortfolioBalance entity populated from row data
        """
        # Parse balance date
        balance_date = None
        if row["balance_date"]:
            try:
                balance_date = date.fromisoformat(row["balance_date"])
            except ValueError:
                balance_date = None

        # Provide default date if none available
        if balance_date is None:
            balance_date = date.today()

        from src.domain.value_objects import IndexChange

        entity = PortfolioBalanceEntity(
            portfolio_id=row["portfolio_id"],
            balance_date=balance_date,
            final_balance=Money(Decimal(str(row["final_balance"]))),
            withdrawals=(
                Money(Decimal(str(row["withdrawals"])))
                if row["withdrawals"]
                else Money.zero()
            ),
            deposits=(
                Money(Decimal(str(row["deposits"])))
                if row["deposits"]
                else Money.zero()
            ),
            index_change=(
                IndexChange(row["index_change"])
                if row["index_change"] is not None
                else None
            ),
            id=row["id"],
        )
        return entity
