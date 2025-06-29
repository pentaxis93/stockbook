"""
SQLite implementation of the transaction repository interface.

Provides concrete implementation using SQLite database operations
while fulfilling the domain repository contract.
"""

import sqlite3
from contextlib import suppress
from datetime import date
from decimal import Decimal
from typing import Any, List, Optional

from src.domain.entities.transaction_entity import TransactionEntity
from src.domain.repositories.interfaces import ITransactionRepository
from src.domain.value_objects import Money, Notes, Quantity, TransactionType
from src.infrastructure.persistence.interfaces import IDatabaseConnection


class SqliteTransactionRepository(ITransactionRepository):
    """
    SQLite-based implementation of the transaction repository.

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

    def create(self, transaction: TransactionEntity) -> str:
        """
        Create a new transaction record in the database.

        Args:
            transaction: Transaction entity to persist

        Returns:
            Database ID of the created transaction

        Raises:
            ValueError: If transaction data is invalid
            DatabaseError: If creation fails
        """
        with self.db_connection.transaction() as conn:
            _ = conn.execute(
                """
                    INSERT INTO stock_transaction (id, portfolio_id, stock_id, type, quantity, price, transaction_date, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                (
                    transaction.id,
                    transaction.portfolio_id,
                    transaction.stock_id,
                    transaction.transaction_type.value,  # Extract value from TransactionType
                    int(transaction.quantity.value),
                    float(transaction.price.amount),
                    transaction.transaction_date.isoformat(),
                    transaction.notes.value,  # Extract value from Notes
                ),
            )
            return transaction.id

    def get_by_id(self, transaction_id: str) -> Optional[TransactionEntity]:
        """
        Retrieve transaction by database ID.

        Args:
            transaction_id: Database ID to search for

        Returns:
            Transaction entity if found, None otherwise
        """
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT id, portfolio_id, stock_id, type, quantity, price, transaction_date, notes, created_at
                FROM stock_transaction 
                WHERE id = ?
                """,
                (transaction_id,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return self._row_to_entity(row)
        finally:
            # Only close if not in a transactional context
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def get_by_portfolio(
        self, portfolio_id: str, limit: Optional[int] = None
    ) -> List[TransactionEntity]:
        """
        Retrieve transactions for a specific portfolio.

        Args:
            portfolio_id: Portfolio identifier
            limit: Maximum number of transactions to return

        Returns:
            List of Transaction domain models, ordered by date (newest first)
        """
        conn = self.db_connection.get_connection()
        try:
            query = """
                SELECT id, portfolio_id, stock_id, type, quantity, price, transaction_date, notes, created_at
                FROM stock_transaction 
                WHERE portfolio_id = ?
                ORDER BY transaction_date DESC, created_at DESC
            """

            params: List[Any] = [portfolio_id]
            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)

            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

            return [self._row_to_entity(row) for row in rows]
        finally:
            # Only close if not in a transactional context
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def get_by_stock(
        self, stock_id: str, portfolio_id: Optional[str] = None
    ) -> List[TransactionEntity]:
        """
        Retrieve transactions for a specific stock.

        Args:
            stock_id: Stock identifier
            portfolio_id: Optional portfolio filter

        Returns:
            List of Transaction domain models
        """
        conn = self.db_connection.get_connection()
        try:
            params: List[Any]
            if portfolio_id is not None:
                query = """
                    SELECT id, portfolio_id, stock_id, type, quantity, price, transaction_date, notes, created_at
                    FROM stock_transaction 
                    WHERE stock_id = ? AND portfolio_id = ?
                    ORDER BY transaction_date DESC, created_at DESC
                """
                params = [stock_id, portfolio_id]
            else:
                query = """
                    SELECT id, portfolio_id, stock_id, type, quantity, price, transaction_date, notes, created_at
                    FROM stock_transaction 
                    WHERE stock_id = ?
                    ORDER BY transaction_date DESC, created_at DESC
                """
                params = [stock_id]

            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

            return [self._row_to_entity(row) for row in rows]
        finally:
            # Only close if not in a transactional context
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def get_by_date_range(
        self, start_date: date, end_date: date, portfolio_id: Optional[str] = None
    ) -> List[TransactionEntity]:
        """
        Retrieve transactions within a date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            portfolio_id: Optional portfolio filter

        Returns:
            List of Transaction domain models
        """
        conn = self.db_connection.get_connection()
        try:
            params: List[Any]
            if portfolio_id is not None:
                query = """
                    SELECT id, portfolio_id, stock_id, type, quantity, price, transaction_date, notes, created_at
                    FROM stock_transaction 
                    WHERE transaction_date >= ? AND transaction_date <= ? AND portfolio_id = ?
                    ORDER BY transaction_date DESC, created_at DESC
                """
                params = [
                    start_date.isoformat(),
                    end_date.isoformat(),
                    portfolio_id,
                ]
            else:
                query = """
                    SELECT id, portfolio_id, stock_id, type, quantity, price, transaction_date, notes, created_at
                    FROM stock_transaction 
                    WHERE transaction_date >= ? AND transaction_date <= ?
                    ORDER BY transaction_date DESC, created_at DESC
                """
                params = [start_date.isoformat(), end_date.isoformat()]

            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

            return [self._row_to_entity(row) for row in rows]
        finally:
            # Only close if not in a transactional context
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def update(self, transaction_id: str, transaction: TransactionEntity) -> bool:
        """
        Update an existing transaction record.

        Args:
            transaction_id: Database ID of transaction to update
            transaction: Transaction entity with updated data

        Returns:
            True if transaction was updated, False if not found
        """
        with self.db_connection.transaction() as conn:
            cursor = conn.execute(
                """
                UPDATE stock_transaction 
                SET portfolio_id = ?, stock_id = ?, type = ?, quantity = ?, price = ?, 
                    transaction_date = ?, notes = ?
                WHERE id = ?
                """,
                (
                    transaction.portfolio_id,
                    transaction.stock_id,
                    transaction.transaction_type.value,  # Extract value from TransactionType
                    int(transaction.quantity.value),
                    float(transaction.price.amount),
                    transaction.transaction_date.isoformat(),
                    transaction.notes.value,  # Extract value from Notes
                    transaction_id,
                ),
            )
            return cursor.rowcount > 0

    def delete(self, transaction_id: str) -> bool:
        """
        Delete transaction by ID.

        Args:
            transaction_id: Transaction identifier

        Returns:
            True if deletion successful, False otherwise
        """
        with self.db_connection.transaction() as conn:
            cursor = conn.execute(
                "DELETE FROM stock_transaction WHERE id = ?", (transaction_id,)
            )
            return cursor.rowcount > 0

    def _row_to_entity(self, row: sqlite3.Row) -> TransactionEntity:
        """
        Convert database row to domain entity.

        Args:
            row: SQLite row with transaction data

        Returns:
            Transaction entity populated from row data
        """
        # Parse transaction date - must be valid for TransactionEntity
        transaction_date = date.today()  # Default fallback
        if row["transaction_date"]:
            with suppress(ValueError):
                transaction_date = date.fromisoformat(row["transaction_date"])

        return TransactionEntity(
            id=row["id"],  # Use id parameter
            portfolio_id=row["portfolio_id"],
            stock_id=row["stock_id"],
            transaction_type=TransactionType(row["type"]),  # Wrap in TransactionType
            quantity=Quantity(row["quantity"]),
            price=Money(Decimal(str(row["price"]))),  # TODO: Store currency in DB
            transaction_date=transaction_date,
            notes=Notes(row["notes"] or ""),  # Wrap in Notes value object
        )
