"""Stock application service interface."""

from abc import ABC, abstractmethod

from src.application.commands.stock import CreateStockCommand, UpdateStockCommand
from src.application.dto.stock_dto import StockDto


class IStockApplicationService(ABC):
    """Interface for stock application service."""

    @abstractmethod
    def get_all_stocks(self) -> list[StockDto]:
        """Retrieve all stocks.

        Returns:
            List of stock DTOs
        """
        ...

    @abstractmethod
    def get_stock_by_id(self, stock_id: str) -> StockDto | None:
        """Retrieve stock by ID.

        Args:
            stock_id: Stock ID to search for

        Returns:
            Stock DTO if found, None otherwise
        """
        ...

    @abstractmethod
    def search_stocks(
        self,
        symbol_filter: str | None = None,
        name_filter: str | None = None,
        industry_filter: str | None = None,
    ) -> list[StockDto]:
        """Search stocks with multiple filter criteria.

        Args:
            symbol_filter: Filter by symbols containing this string (case-insensitive)
            name_filter: Filter by names containing this string (case-insensitive)
            industry_filter: Filter by industry group containing this string
                (case-insensitive)

        Returns:
            List of stock DTOs matching the criteria
        """
        ...

    @abstractmethod
    def create_stock(self, command: CreateStockCommand) -> StockDto:
        """Create a new stock.

        Args:
            command: Command containing stock creation data

        Returns:
            Created stock DTO

        Raises:
            StockAlreadyExistsError: If stock with same symbol already exists
            ValidationError: If command data is invalid
        """
        ...

    @abstractmethod
    def update_stock(self, command: UpdateStockCommand) -> StockDto:
        """Update an existing stock.

        Args:
            command: Command containing stock update data

        Returns:
            Updated stock DTO

        Raises:
            StockNotFoundError: If stock with given ID doesn't exist
            ValidationError: If command data is invalid
        """
        ...
