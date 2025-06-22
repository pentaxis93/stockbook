"""
SQLite implementation of the stock repository interface.

Provides concrete implementation using SQLite database operations
while fulfilling the domain repository contract.
"""

import sqlite3
from typing import List, Optional, Tuple

from src.domain.entities.stock_entity import StockEntity
from src.domain.repositories.interfaces import IStockRepository
from src.domain.value_objects import CompanyName, Grade, IndustryGroup, Notes
from src.domain.value_objects.sector import Sector
from src.domain.value_objects.stock_symbol import StockSymbol
from src.infrastructure.persistence.interfaces import IDatabaseConnection


class SqliteStockRepository(IStockRepository):
    """
    SQLite-based implementation of the stock repository.

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

    def create(self, stock: StockEntity) -> str:
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
                _ = conn.execute(
                    """
                        INSERT INTO stock (id, symbol, name, sector, industry_group, grade, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                    (
                        stock.id,
                        stock.symbol.value,
                        stock.company_name.value,
                        stock.sector.value if stock.sector else None,
                        stock.industry_group.value if stock.industry_group else None,
                        stock.grade.value if stock.grade else None,
                        stock.notes.value,
                    ),
                )
                return stock.id
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: stock.symbol" in str(e):
                raise ValueError(
                    f"Stock with symbol {stock.symbol.value} already exists"
                ) from e
            raise

    def get_by_id(self, stock_id: str) -> Optional[StockEntity]:
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
                "SELECT id, symbol, name, sector, industry_group, grade, notes FROM stock WHERE id = ?",
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
                "SELECT id, symbol, name, sector, industry_group, grade, notes FROM stock WHERE symbol = ?",
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
                "SELECT id, symbol, name, sector, industry_group, grade, notes FROM stock ORDER BY symbol"
            )
            rows = cursor.fetchall()

            return [self._row_to_entity(row) for row in rows]
        finally:
            # Only close if not in a transactional context
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def update(self, stock_id: str, stock: StockEntity) -> bool:
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
                SET name = ?, sector = ?, industry_group = ?, grade = ?, notes = ?
                WHERE id = ?
                """,
                (
                    stock.company_name.value,
                    stock.sector.value if stock.sector else None,
                    stock.industry_group.value if stock.industry_group else None,
                    stock.grade.value if stock.grade else None,
                    stock.notes.value,
                    stock_id,
                ),
            )
            return cursor.rowcount > 0

    def delete(self, stock_id: str) -> bool:
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
                "SELECT id, symbol, name, sector, industry_group, grade, notes FROM stock WHERE grade = ? ORDER BY symbol",
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
                "SELECT id, symbol, name, sector, industry_group, grade, notes FROM stock WHERE industry_group = ? ORDER BY symbol",
                (industry_group,),
            )
            rows = cursor.fetchall()

            return [self._row_to_entity(row) for row in rows]
        finally:
            # Only close if not in a transactional context
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def get_by_sector(self, sector: str) -> List[StockEntity]:
        """
        Get all stocks in a specific sector.

        Args:
            sector: Sector to filter by

        Returns:
            List of stock entities in the sector
        """
        conn = self.db_connection.get_connection()
        try:
            cursor = conn.execute(
                "SELECT id, symbol, name, sector, industry_group, grade, notes FROM stock WHERE sector = ? ORDER BY symbol",
                (sector,),
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
        sector_filter: Optional[str] = None,
        industry_filter: Optional[str] = None,
        grade_filter: Optional[str] = None,
    ) -> List[StockEntity]:
        """
        Search stocks with multiple filter criteria.

        Args:
            symbol_filter: Filter by symbols containing this string (case-insensitive)
            name_filter: Filter by names containing this string (case-insensitive)
            sector_filter: Filter by sector containing this string (case-insensitive)
            industry_filter: Filter by industry group containing this string (case-insensitive)
            grade_filter: Filter by exact grade match (A, B, or C)

        Returns:
            List of StockEntity domain models matching the criteria
        """
        conn = self.db_connection.get_connection()
        try:
            where_clauses, parameters = self._build_search_filters(
                symbol_filter, name_filter, sector_filter, industry_filter, grade_filter
            )

            query = self._build_search_query(where_clauses)
            cursor = conn.execute(query, parameters)
            rows = cursor.fetchall()

            return [self._row_to_entity(row) for row in rows]
        finally:
            # Only close if not in a transactional context
            if not getattr(self.db_connection, "is_transactional", False):
                conn.close()

    def _build_search_filters(
        self,
        symbol_filter: Optional[str],
        name_filter: Optional[str],
        sector_filter: Optional[str],
        industry_filter: Optional[str],
        grade_filter: Optional[str],
    ) -> Tuple[List[str], List[str]]:
        """Build WHERE clauses and parameters for search filters."""
        where_clauses: List[str] = []
        parameters: List[str] = []

        # Add all filter types using helper method
        self._add_like_filter(where_clauses, parameters, "UPPER(symbol)", symbol_filter)
        self._add_like_filter(where_clauses, parameters, "UPPER(name)", name_filter)
        self._add_like_filter(where_clauses, parameters, "UPPER(sector)", sector_filter)
        self._add_like_filter(
            where_clauses, parameters, "UPPER(industry_group)", industry_filter
        )
        self._add_exact_filter(where_clauses, parameters, "grade", grade_filter)

        return where_clauses, parameters

    def _add_like_filter(
        self,
        where_clauses: List[str],
        parameters: List[str],
        column: str,
        filter_value: Optional[str],
    ) -> None:
        """Add a LIKE filter to the where clauses if filter value is provided."""
        if filter_value:
            where_clauses.append(f"{column} LIKE UPPER(?)")
            parameters.append(f"%{filter_value}%")

    def _add_exact_filter(
        self,
        where_clauses: List[str],
        parameters: List[str],
        column: str,
        filter_value: Optional[str],
    ) -> None:
        """Add an exact match filter to the where clauses if filter value is provided."""
        if filter_value:
            where_clauses.append(f"{column} = ?")
            parameters.append(filter_value)

    def _build_search_query(self, where_clauses: List[str]) -> str:
        """Build the complete SQL query for stock search."""
        base_query = (
            "SELECT id, symbol, name, sector, industry_group, grade, notes FROM stock"
        )

        if where_clauses:
            return f"{base_query} WHERE {' AND '.join(where_clauses)} ORDER BY symbol"
        return f"{base_query} ORDER BY symbol"

    def _row_to_entity(self, row: sqlite3.Row) -> StockEntity:
        """
        Convert database row to domain entity.

        Args:
            row: SQLite row with stock data

        Returns:
            Stock entity populated from row data
        """
        return StockEntity(
            id=row["id"],
            symbol=StockSymbol(row["symbol"]),
            company_name=CompanyName(row["name"] or ""),
            sector=Sector(row["sector"]) if row["sector"] else None,
            industry_group=(
                IndustryGroup(row["industry_group"]) if row["industry_group"] else None
            ),
            grade=Grade(row["grade"]) if row["grade"] else None,
            notes=Notes(row["notes"] or ""),
        )
