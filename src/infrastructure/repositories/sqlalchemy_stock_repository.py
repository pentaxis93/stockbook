"""
SQLAlchemy Core implementation of the Stock repository.

This module provides a concrete implementation of IStockRepository using
SQLAlchemy Core, maintaining clean architecture separation by avoiding ORM.
"""

# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false, reportArgumentType=false

from datetime import datetime, UTC
from typing import Any

from sqlalchemy import delete as sql_delete
from sqlalchemy import (
    exc,
    func,
    insert,
    select,
)
from sqlalchemy import update as sql_update

from src.domain.entities.stock import Stock
from src.domain.repositories.interfaces import IStockRepository
from src.domain.value_objects import (
    CompanyName,
    Grade,
    IndustryGroup,
    Notes,
    Sector,
    StockSymbol,
)
from src.infrastructure.persistence.interfaces import IDatabaseConnection
from src.infrastructure.persistence.tables.stock_table import stock_table


class SqlAlchemyStockRepository(IStockRepository):
    """
    SQLAlchemy Core implementation of the stock repository.

    This repository uses SQLAlchemy Core (not ORM) to maintain clean
    architecture separation while providing database persistence for
    Stock domain entities.
    """

    def __init__(self, connection: IDatabaseConnection) -> None:
        """
        Initialize the repository with a database connection.

        Args:
            connection: Database connection supporting SQLAlchemy Core operations
        """
        self._connection = connection

    def create(self, stock: Stock) -> str:
        """
        Create a new stock record in the database.

        Args:
            stock: Stock domain entity to persist

        Returns:
            str: ID of the created stock

        Raises:
            ValueError: If a stock with the same symbol already exists
            exc.DatabaseError: For other database errors
        """
        # Convert entity to row data
        row_data = self._entity_to_row(stock)

        # Create insert statement
        stmt = insert(stock_table).values(**row_data)

        try:
            # Execute the insert
            self._connection.execute(stmt)
            return stock.id

        except exc.IntegrityError as e:
            # Check if it's a unique constraint violation on symbol
            if "symbol" in str(e):
                raise ValueError(
                    f"Stock with symbol {stock.symbol.value} already exists"
                ) from e
            raise

    def get_by_symbol(self, symbol: StockSymbol) -> Stock | None:
        """
        Retrieve stock by symbol.

        Args:
            symbol: Stock symbol value object

        Returns:
            Stock domain entity or None if not found
        """
        # Create select statement
        stmt = select(*stock_table.c).where(stock_table.c.symbol == symbol.value)

        # Execute query
        result = self._connection.execute(stmt)
        row = result.fetchone()

        if row is None:
            return None

        # Convert row to domain entity
        # Handle both dict (from mocks) and Row objects (from SQLAlchemy)
        row_dict = row._asdict() if hasattr(row, "_asdict") else row
        return self._row_to_entity(row_dict)

    def _entity_to_row(self, stock: Stock) -> dict[str, Any]:
        """
        Convert Stock entity to database row dictionary.

        Args:
            stock: Stock domain entity

        Returns:
            Dictionary with database column values
        """
        now = datetime.now(UTC)

        return {
            "id": stock.id,
            "symbol": stock.symbol.value,
            "company_name": stock.company_name.value if stock.company_name else None,
            "sector": stock.sector.value if stock.sector else None,
            "industry_group": (
                stock.industry_group.value if stock.industry_group else None
            ),
            "grade": stock.grade.value if stock.grade else None,
            "notes": stock.notes.value if stock.notes else "",
            "created_at": now,
            "updated_at": now,
        }

    def _row_to_entity(self, row: dict[str, Any]) -> Stock:
        """
        Convert database row to Stock entity.

        Args:
            row: Database row as dictionary

        Returns:
            Stock domain entity
        """
        builder = (
            Stock.Builder().with_id(row["id"]).with_symbol(StockSymbol(row["symbol"]))
        )

        if row["company_name"]:
            builder = builder.with_company_name(CompanyName(row["company_name"]))
        if row["sector"]:
            builder = builder.with_sector(Sector(row["sector"]))
        if row["industry_group"]:
            builder = builder.with_industry_group(IndustryGroup(row["industry_group"]))
        if row["grade"]:
            builder = builder.with_grade(Grade(row["grade"]))
        if row["notes"]:
            builder = builder.with_notes(Notes(row["notes"]))
        else:
            builder = builder.with_notes(Notes(""))

        return builder.build()

    # Stub implementations for other interface methods (to be implemented later)

    def get_by_id(self, stock_id: str) -> Stock | None:
        """
        Retrieve stock by ID.

        Args:
            stock_id: Unique identifier of the stock

        Returns:
            Stock domain entity or None if not found
        """
        # Create select statement
        stmt = select(*stock_table.c).where(stock_table.c.id == stock_id)

        # Execute query
        result = self._connection.execute(stmt)
        row = result.fetchone()

        if row is None:
            return None

        # Convert row to domain entity
        # Handle both dict (from mocks) and Row objects (from SQLAlchemy)
        row_dict = row._asdict() if hasattr(row, "_asdict") else row
        return self._row_to_entity(row_dict)

    def get_all(self) -> list[Stock]:
        """
        Retrieve all stocks from the database.

        Returns:
            List of Stock domain entities
        """
        # Create select statement for all stocks
        stmt = select(*stock_table.c)

        # Execute query
        result = self._connection.execute(stmt)
        rows = result.fetchall()

        # Convert rows to domain entities
        return [
            self._row_to_entity(row._asdict() if hasattr(row, "_asdict") else row)
            for row in rows
        ]

    def update(self, stock_id: str, stock: Stock) -> bool:
        """
        Update an existing stock record.

        Args:
            stock_id: ID of the stock to update
            stock: Stock domain entity with updated values

        Returns:
            True if the stock was updated, False if not found

        Raises:
            ValueError: If updating would violate unique constraints
            exc.DatabaseError: For other database errors
        """
        # Convert entity to row data (excluding ID and created_at)
        row_data = self._entity_to_row(stock)
        # Remove fields that shouldn't be updated
        row_data.pop("id", None)
        row_data.pop("created_at", None)

        # Update the updated_at timestamp
        row_data["updated_at"] = datetime.now(UTC)

        # Create update statement
        stmt = (
            sql_update(stock_table)
            .where(stock_table.c.id == stock_id)
            .values(**row_data)
        )

        try:
            # Execute the update
            result = self._connection.execute(stmt)

            # Check if any rows were affected
            return bool(result.rowcount > 0)

        except exc.IntegrityError as e:
            # Check if it's a unique constraint violation on symbol
            if "symbol" in str(e):
                raise ValueError(
                    f"Stock with symbol {stock.symbol.value} already exists"
                ) from e
            raise

    def delete(self, stock_id: str) -> bool:
        """
        Delete a stock record from the database.

        Args:
            stock_id: ID of the stock to delete

        Returns:
            True if the stock was deleted, False if not found

        Raises:
            exc.IntegrityError: If deletion would violate foreign key constraints
            exc.DatabaseError: For other database errors
        """
        # Create delete statement
        stmt = sql_delete(stock_table).where(stock_table.c.id == stock_id)

        # Execute the delete
        result = self._connection.execute(stmt)

        # Check if any rows were affected
        return bool(result.rowcount > 0)

    def exists_by_symbol(self, symbol: StockSymbol) -> bool:
        """
        Check if a stock with the given symbol exists.

        Args:
            symbol: Stock symbol to check

        Returns:
            True if stock exists, False otherwise

        Raises:
            exc.DatabaseError: For database errors
        """
        # Create optimized count query
        stmt = (
            select(func.count())  # pylint: disable=not-callable
            .select_from(stock_table)
            .where(stock_table.c.symbol == symbol.value)
        )

        # Execute query and get scalar result
        result = self._connection.execute(stmt)
        count = result.scalar()

        return bool(count > 0)

    def search_stocks(
        self,
        symbol_filter: str | None = None,
        name_filter: str | None = None,
        industry_filter: str | None = None,
    ) -> list[Stock]:
        """
        Search for stocks based on optional filters.

        Args:
            symbol_filter: Pattern to match against stock symbols (case-insensitive)
            name_filter: Pattern to match against company names (case-insensitive)
            industry_filter: Exact industry group to filter by

        Returns:
            List of Stock entities matching the filters

        Raises:
            exc.DatabaseError: For database errors
        """
        # Start with base select statement
        stmt = select(*stock_table.c)

        # Apply filters dynamically
        if symbol_filter:
            # Case-insensitive pattern matching for symbol
            stmt = stmt.where(stock_table.c.symbol.ilike(f"%{symbol_filter}%"))

        if name_filter:
            # Case-insensitive pattern matching for company name
            stmt = stmt.where(stock_table.c.company_name.ilike(f"%{name_filter}%"))

        if industry_filter:
            # Exact match for industry group
            stmt = stmt.where(stock_table.c.industry_group == industry_filter)

        # Execute query
        result = self._connection.execute(stmt)
        rows = result.fetchall()

        # Convert rows to domain entities
        return [
            self._row_to_entity(row._asdict() if hasattr(row, "_asdict") else row)
            for row in rows
        ]
