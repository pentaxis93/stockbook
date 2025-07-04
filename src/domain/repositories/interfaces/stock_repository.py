"""
Stock repository interface.

Defines the contract for stock data persistence operations.
"""

from abc import ABC, abstractmethod

from src.domain.entities import Stock
from src.domain.value_objects.stock_symbol import StockSymbol


class IStockRepository(ABC):
    """Abstract interface for stock data operations."""

    @abstractmethod
    def create(self, stock: Stock) -> str:
        """
        Create a new stock record.

        Args:
            stock: Stock domain model

        Returns:
            ID of the created stock

        Raises:
            ValidationError: If stock data is invalid
            DatabaseError: If creation fails
        """
        pass

    @abstractmethod
    def get_by_id(self, stock_id: str) -> Stock | None:
        """
        Retrieve stock by ID.

        Args:
            stock_id: Stock identifier

        Returns:
            Stock domain model or None if not found
        """
        pass

    @abstractmethod
    def get_by_symbol(self, symbol: StockSymbol) -> Stock | None:
        """
        Retrieve stock by symbol.

        Args:
            symbol: Stock symbol value object

        Returns:
            Stock domain model or None if not found
        """
        pass

    @abstractmethod
    def get_all(self) -> list[Stock]:
        """
        Retrieve all stocks.

        Returns:
            List of Stock domain models
        """
        pass

    @abstractmethod
    def update(self, stock_id: str, stock: Stock) -> bool:
        """
        Update existing stock.

        Args:
            stock_id: Stock identifier
            stock: Updated Stock domain model

        Returns:
            True if update successful, False otherwise

        Raises:
            ValidationError: If stock data is invalid
            DatabaseError: If update fails
        """
        pass

    @abstractmethod
    def delete(self, stock_id: str) -> bool:
        """
        Delete stock by ID.

        Args:
            stock_id: Stock identifier

        Returns:
            True if deletion successful, False otherwise

        Raises:
            BusinessLogicError: If stock has dependent records
            DatabaseError: If deletion fails
        """
        pass

    @abstractmethod
    def exists_by_symbol(self, symbol: StockSymbol) -> bool:
        """
        Check if stock exists by symbol.

        Args:
            symbol: Stock symbol value object to check

        Returns:
            True if stock exists, False otherwise
        """
        pass

    @abstractmethod
    def search_stocks(
        self,
        symbol_filter: str | None = None,
        name_filter: str | None = None,
        industry_filter: str | None = None,
    ) -> list[Stock]:
        """
        Search stocks with multiple filter criteria.

        Args:
            symbol_filter: Filter by symbols containing this string (case-insensitive)
            name_filter: Filter by names containing this string (case-insensitive)
            industry_filter: Filter by industry group containing this string (case-insensitive)

        Returns:
            List of Stock domain models matching the criteria
        """
        pass
