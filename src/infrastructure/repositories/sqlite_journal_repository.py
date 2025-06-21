"""
SQLite implementation of the journal entry repository interface.

Provides concrete implementation using SQLite database operations
while fulfilling the domain repository contract.
"""

import sqlite3
from datetime import date
from typing import List, Optional

from src.domain.entities.journal_entry_entity import JournalEntryEntity
from src.domain.repositories.interfaces import IJournalRepository
from src.infrastructure.persistence.interfaces import IDatabaseConnection


class SqliteJournalRepository(IJournalRepository):
    """
    SQLite-based implementation of the journal entry repository.

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

    def create(self, entry: JournalEntryEntity) -> str:
        """
        Create a new journal entry.

        Args:
            entry: JournalEntryEntity domain model

        Returns:
            ID of the created entry
        """
        with self.db_connection.transaction() as conn:
            conn.execute(
                """
                INSERT INTO journal_entry (id, entry_date, content, stock_id, portfolio_id, transaction_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.id,
                    entry.entry_date.isoformat() if entry.entry_date else "",
                    entry.content.value,
                    entry.stock_id,
                    entry.portfolio_id,
                    entry.transaction_id,
                ),
            )
            return entry.id

    def get_by_id(self, entry_id: str) -> Optional[JournalEntryEntity]:
        """
        Retrieve journal entry by ID.

        Args:
            entry_id: Entry identifier

        Returns:
            JournalEntry domain model or None if not found
        """
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT id, entry_date, content, stock_id, portfolio_id, transaction_id, created_at, updated_at
                FROM journal_entry 
                WHERE id = ?
                """,
                (entry_id,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return self._row_to_entity(row)
        finally:
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def get_recent(self, limit: Optional[int] = None) -> List[JournalEntryEntity]:
        """
        Retrieve recent journal entries.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of JournalEntry domain models, ordered by date (newest first)
        """
        conn = self.db_connection.get_connection()
        try:
            query = """
                SELECT id, entry_date, content, stock_id, portfolio_id, transaction_id, created_at, updated_at
                FROM journal_entry 
                ORDER BY entry_date DESC, created_at DESC
            """

            params: list = []
            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)

            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

            return [self._row_to_entity(row) for row in rows]
        finally:
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def get_by_portfolio(
        self, portfolio_id: str, limit: Optional[int] = None
    ) -> List[JournalEntryEntity]:
        """
        Retrieve journal entries for a specific portfolio.

        Args:
            portfolio_id: Portfolio identifier
            limit: Maximum number of entries to return

        Returns:
            List of JournalEntry domain models
        """
        conn = self.db_connection.get_connection()
        try:
            query = """
                SELECT id, entry_date, content, stock_id, portfolio_id, transaction_id, created_at, updated_at
                FROM journal_entry 
                WHERE portfolio_id = ?
                ORDER BY entry_date DESC, created_at DESC
            """

            params: list = [portfolio_id]
            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)

            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

            return [self._row_to_entity(row) for row in rows]
        finally:
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def get_by_stock(
        self, stock_id: str, limit: Optional[int] = None
    ) -> List[JournalEntryEntity]:
        """
        Retrieve journal entries for a specific stock.

        Args:
            stock_id: Stock identifier
            limit: Maximum number of entries to return

        Returns:
            List of JournalEntry domain models
        """
        conn = self.db_connection.get_connection()
        try:
            query = """
                SELECT id, entry_date, content, stock_id, portfolio_id, transaction_id, created_at, updated_at
                FROM journal_entry 
                WHERE stock_id = ?
                ORDER BY entry_date DESC, created_at DESC
            """

            params: list = [stock_id]
            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)

            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

            return [self._row_to_entity(row) for row in rows]
        finally:
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def get_by_transaction(self, transaction_id: str) -> List[JournalEntryEntity]:
        """
        Retrieve journal entries for a specific transaction.

        Args:
            transaction_id: Transaction identifier

        Returns:
            List of JournalEntry domain models
        """
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT id, entry_date, content, stock_id, portfolio_id, transaction_id, created_at, updated_at
                FROM journal_entry 
                WHERE transaction_id = ?
                ORDER BY entry_date DESC, created_at DESC
                """,
                (transaction_id,),
            )
            rows = cursor.fetchall()

            return [self._row_to_entity(row) for row in rows]
        finally:
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def get_by_date_range(
        self, start_date: date, end_date: date
    ) -> List[JournalEntryEntity]:
        """
        Retrieve journal entries within a date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            List of JournalEntry domain models
        """
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.execute(
                """
                SELECT id, entry_date, content, stock_id, portfolio_id, transaction_id, created_at, updated_at
                FROM journal_entry 
                WHERE entry_date >= ? AND entry_date <= ?
                ORDER BY entry_date DESC, created_at DESC
                """,
                (start_date.isoformat(), end_date.isoformat()),
            )
            rows = cursor.fetchall()

            return [self._row_to_entity(row) for row in rows]
        finally:
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def update(self, entry_id: str, entry: JournalEntryEntity) -> bool:
        """
        Update existing journal entry.

        Args:
            entry_id: Entry identifier
            entry: Updated entry domain model

        Returns:
            True if update successful, False otherwise
        """
        with self.db_connection.transaction() as conn:
            cursor = conn.execute(
                """
                UPDATE journal_entry 
                SET entry_date = ?, content = ?, stock_id = ?, portfolio_id = ?, transaction_id = ?
                WHERE id = ?
                """,
                (
                    entry.entry_date.isoformat() if entry.entry_date else "",
                    entry.content.value,
                    entry.stock_id,
                    entry.portfolio_id,
                    entry.transaction_id,
                    entry_id,
                ),
            )
            return cursor.rowcount > 0

    def delete(self, entry_id: str) -> bool:
        """
        Delete journal entry by ID.

        Args:
            entry_id: Entry identifier

        Returns:
            True if deletion successful, False otherwise
        """
        with self.db_connection.transaction() as conn:
            cursor = conn.execute("DELETE FROM journal_entry WHERE id = ?", (entry_id,))
            return cursor.rowcount > 0

    def _row_to_entity(self, row: sqlite3.Row) -> JournalEntryEntity:
        """
        Convert database row to domain entity.

        Args:
            row: SQLite row with journal entry data

        Returns:
            JournalEntry entity populated from row data
        """
        # Parse entry date
        entry_date = None
        if row["entry_date"]:
            try:
                entry_date = date.fromisoformat(row["entry_date"])
            except ValueError:
                entry_date = None

        # Provide default date if none available
        if entry_date is None:
            entry_date = date.today()

        from src.domain.value_objects import JournalContent

        entity = JournalEntryEntity(
            entry_date=entry_date,
            content=JournalContent(row["content"]),
            portfolio_id=row["portfolio_id"],
            stock_id=row["stock_id"],
            transaction_id=row["transaction_id"],
            id=row["id"],
        )
        return entity
