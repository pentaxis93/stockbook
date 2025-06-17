"""
SQLite implementation of the stock repository interface.

Provides concrete implementation using SQLite database operations
while fulfilling the domain repository contract.
"""

import sqlite3
from typing import List, Optional

from domain.entities.stock_entity import StockEntity
from domain.repositories.interfaces import IStockRepository
from domain.value_objects.stock_symbol import StockSymbol
from infrastructure.persistence.database_connection import DatabaseConnection


class SqliteStockRepository(IStockRepository):
    """
    SQLite-based implementation of the stock repository.

    Maps between domain entities and database records while maintaining
    the repository pattern and clean architecture boundaries.
    """

    def __init__(self, db_connection: DatabaseConnection):
        """
        Initialize repository with database connection.

        Args:
            db_connection: Database connection manager
        """
        self.db_connection = db_connection

    def create(self, stock: StockEntity) -> int:
        """
        Create a new stock record in the database.

        Args:
            stock: Stock entity to persist

        Returns:
            Database ID of the created stock

        Raises:
            ValueError: If stock symbol already exists
        """
        try:
            with self.db_connection.transaction() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO stock (symbol, name, industry_group, grade, notes)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        stock.symbol.value,
                        stock.name,
                        stock.industry_group,
                        stock.grade,
                        stock.notes,
                    ),
                )
                return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: stock.symbol" in str(e):
                raise ValueError(
                    f"Stock with symbol {stock.symbol.value} already exists"
                )
            raise

    def get_by_id(self, stock_id: int) -> Optional[StockEntity]:
        """
        Retrieve stock by database ID.

        Args:
            stock_id: Database ID to search for

        Returns:
            Stock entity if found, None otherwise
        """
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.execute(
                "SELECT id, symbol, name, industry_group, grade, notes FROM stock WHERE id = ?",
                (stock_id,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return self._row_to_entity(row)
        finally:
            # Only close if not in a transactional context
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def get_by_symbol(self, symbol: StockSymbol) -> Optional[StockEntity]:
        """
        Retrieve stock by symbol.

        Args:
            symbol: Stock symbol to search for

        Returns:
            Stock entity if found, None otherwise
        """
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.execute(
                "SELECT id, symbol, name, industry_group, grade, notes FROM stock WHERE symbol = ?",
                (symbol.value,),
            )
            row = cursor.fetchone()

            if row is None:
                return None

            return self._row_to_entity(row)
        finally:
            # Only close if not in a transactional context
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def get_all(self) -> List[StockEntity]:
        """
        Retrieve all stocks from the database.

        Returns:
            List of all stock entities
        """
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.execute(
                "SELECT id, symbol, name, industry_group, grade, notes FROM stock ORDER BY symbol"
            )
            rows = cursor.fetchall()

            return [self._row_to_entity(row) for row in rows]
        finally:
            # Only close if not in a transactional context
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def update(self, stock_id: int, stock: StockEntity) -> bool:
        """
        Update an existing stock record.

        Args:
            stock_id: Database ID of stock to update
            stock: Stock entity with updated data

        Returns:
            True if stock was updated, False if not found
        """
        with self.db_connection.transaction() as conn:
            cursor = conn.execute(
                """
                UPDATE stock 
                SET name = ?, industry_group = ?, grade = ?, notes = ?
                WHERE id = ?
                """,
                (stock.name, stock.industry_group, stock.grade, stock.notes, stock_id),
            )
            return cursor.rowcount > 0

    def delete(self, stock_id: int) -> bool:
        """
        Delete a stock by ID.

        Args:
            stock_id: Database ID of stock to delete

        Returns:
            True if stock was deleted, False if not found
        """
        with self.db_connection.transaction() as conn:
            cursor = conn.execute("DELETE FROM stock WHERE id = ?", (stock_id,))
            return cursor.rowcount > 0

    def exists_by_symbol(self, symbol: StockSymbol) -> bool:
        """
        Check if a stock exists by symbol.

        Args:
            symbol: Stock symbol to check

        Returns:
            True if stock exists, False otherwise
        """
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.execute(
                "SELECT 1 FROM stock WHERE symbol = ? LIMIT 1", (symbol.value,)
            )
            return cursor.fetchone() is not None
        finally:
            # Only close if not in a transactional context
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def get_by_grade(self, grade: str) -> List[StockEntity]:
        """
        Retrieve all stocks with specific grade.

        Args:
            grade: Grade to filter by

        Returns:
            List of stock entities with the specified grade
        """
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.execute(
                "SELECT id, symbol, name, industry_group, grade, notes FROM stock WHERE grade = ? ORDER BY symbol",
                (grade,),
            )
            rows = cursor.fetchall()

            return [self._row_to_entity(row) for row in rows]
        finally:
            # Only close if not in a transactional context
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def get_by_industry_group(self, industry_group: str) -> List[StockEntity]:
        """
        Retrieve all stocks in specific industry group.

        Args:
            industry_group: Industry group to filter by

        Returns:
            List of stock entities in the specified industry group
        """
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.execute(
                "SELECT id, symbol, name, industry_group, grade, notes FROM stock WHERE industry_group = ? ORDER BY symbol",
                (industry_group,),
            )
            rows = cursor.fetchall()

            return [self._row_to_entity(row) for row in rows]
        finally:
            # Only close if not in a transactional context
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def search_stocks(
        self,
        symbol_filter: Optional[str] = None,
        name_filter: Optional[str] = None,
        industry_filter: Optional[str] = None,
        grade_filter: Optional[str] = None,
    ) -> List[StockEntity]:
        """
        Search stocks with multiple filter criteria.

        Args:
            symbol_filter: Filter by symbols containing this string (case-insensitive)
            name_filter: Filter by names containing this string (case-insensitive)
            industry_filter: Filter by industry group containing this string (case-insensitive)
            grade_filter: Filter by exact grade match (A, B, or C)

        Returns:
            List of StockEntity domain models matching the criteria
        """
        conn = self.db_connection.get_connection()
        try:
            # Build dynamic query based on provided filters
            where_clauses = []
            parameters = []

            if symbol_filter:
                where_clauses.append("UPPER(symbol) LIKE UPPER(?)")
                parameters.append(f"%{symbol_filter}%")

            if name_filter:
                where_clauses.append("UPPER(name) LIKE UPPER(?)")
                parameters.append(f"%{name_filter}%")

            if industry_filter:
                where_clauses.append("UPPER(industry_group) LIKE UPPER(?)")
                parameters.append(f"%{industry_filter}%")

            if grade_filter:
                where_clauses.append("grade = ?")
                parameters.append(grade_filter)

            # Build the complete query
            base_query = (
                "SELECT id, symbol, name, industry_group, grade, notes FROM stock"
            )

            if where_clauses:
                query = (
                    f"{base_query} WHERE {' AND '.join(where_clauses)} ORDER BY symbol"
                )
            else:
                query = f"{base_query} ORDER BY symbol"

            cursor = conn.execute(query, parameters)
            rows = cursor.fetchall()

            return [self._row_to_entity(row) for row in rows]
        finally:
            # Only close if not in a transactional context
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def _row_to_entity(self, row: sqlite3.Row) -> StockEntity:
        """
        Convert database row to domain entity.

        Args:
            row: SQLite row with stock data

        Returns:
            Stock entity populated from row data
        """
        return StockEntity(
            stock_id=row["id"],
            symbol=StockSymbol(row["symbol"]),
            name=row["name"],
            industry_group=row["industry_group"],
            grade=row["grade"],
            notes=row["notes"] or "",
        )
