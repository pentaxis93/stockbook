"""
Stock application service.

Orchestrates stock-related use cases and coordinates between
domain entities and repositories.
"""

from src.application.commands.stock import (
    CreateStockCommand,
    UpdateStockCommand,
)
from src.application.dto.stock_dto import StockDto
from src.domain.entities.stock import Stock
from src.domain.repositories.interfaces import IStockBookUnitOfWork
from src.domain.value_objects import CompanyName, Grade, IndustryGroup, Notes
from src.domain.value_objects.sector import Sector
from src.domain.value_objects.stock_symbol import StockSymbol


class StockApplicationService:
    """
    Application service for stock operations.

    Provides high-level use case operations for stock management,
    coordinating between domain entities and repositories.
    """

    def __init__(self, unit_of_work: IStockBookUnitOfWork):
        """
        Initialize service with unit of work.

        Args:
            unit_of_work: Unit of work for transaction management
        """
        self._unit_of_work = unit_of_work

    def create_stock(self, command: CreateStockCommand) -> StockDto:
        """
        Create a new stock.

        Args:
            command: Command containing stock creation data

        Returns:
            DTO representing the created stock

        Raises:
            ValueError: If stock with symbol already exists
        """
        try:
            with self._unit_of_work:
                # Check if stock already exists
                symbol_vo = StockSymbol(command.symbol)
                existing_stock = self._unit_of_work.stocks.get_by_symbol(symbol_vo)

                if existing_stock is not None:
                    raise ValueError(
                        f"Stock with symbol {command.symbol} already exists"
                    )

                # Create domain entity
                builder = Stock.Builder().with_symbol(symbol_vo)

                if command.name:
                    builder = builder.with_company_name(CompanyName(command.name))
                if command.sector:
                    builder = builder.with_sector(Sector(command.sector))
                if command.industry_group:
                    builder = builder.with_industry_group(
                        IndustryGroup(command.industry_group)
                    )
                if command.grade:
                    builder = builder.with_grade(Grade(command.grade))
                if command.notes:
                    builder = builder.with_notes(Notes(command.notes))

                stock_entity = builder.build()

                # Persist entity
                _ = self._unit_of_work.stocks.create(stock_entity)

                # Commit transaction
                self._unit_of_work.commit()

                return StockDto.from_entity(stock_entity)

        except Exception:
            self._unit_of_work.rollback()
            raise

    def get_stock_by_symbol(self, symbol: str) -> StockDto | None:
        """
        Retrieve stock by symbol.

        Args:
            symbol: Stock symbol to search for

        Returns:
            Stock DTO if found, None otherwise
        """
        with self._unit_of_work:
            symbol_vo = StockSymbol(symbol)
            stock_entity = self._unit_of_work.stocks.get_by_symbol(symbol_vo)

            if stock_entity is None:
                return None

            return StockDto.from_entity(stock_entity)

    def get_stock_by_id(self, stock_id: str) -> StockDto | None:
        """
        Retrieve stock by ID.

        Args:
            stock_id: Stock ID to search for

        Returns:
            Stock DTO if found, None otherwise
        """
        with self._unit_of_work:
            stock_entity = self._unit_of_work.stocks.get_by_id(stock_id)

            if stock_entity is None:
                return None

            return StockDto.from_entity(stock_entity)

    def get_all_stocks(self) -> list[StockDto]:
        """
        Retrieve all stocks.

        Returns:
            List of stock DTOs
        """
        with self._unit_of_work:
            stock_entities = self._unit_of_work.stocks.get_all()
            return [StockDto.from_entity(entity) for entity in stock_entities]

    def stock_exists(self, symbol: str) -> bool:
        """
        Check if stock exists by symbol.

        Args:
            symbol: Stock symbol to check

        Returns:
            True if stock exists, False otherwise
        """
        with self._unit_of_work:
            symbol_vo = StockSymbol(symbol)
            return self._unit_of_work.stocks.exists_by_symbol(symbol_vo)

    def search_stocks(
        self,
        symbol_filter: str | None = None,
        name_filter: str | None = None,
        industry_filter: str | None = None,
    ) -> list[StockDto]:
        """
        Search stocks with multiple filter criteria.

        Args:
            symbol_filter: Filter by symbols containing this string (case-insensitive)
            name_filter: Filter by names containing this string (case-insensitive)
            industry_filter: Filter by industry group containing this string (case-insensitive)

        Returns:
            List of stock DTOs matching the criteria
        """
        with self._unit_of_work:
            stock_entities = self._unit_of_work.stocks.search_stocks(
                symbol_filter=symbol_filter,
                name_filter=name_filter,
                industry_filter=industry_filter,
            )
            return [StockDto.from_entity(entity) for entity in stock_entities]

    def update_stock(self, command: UpdateStockCommand) -> StockDto:
        """
        Update an existing stock.

        Args:
            command: Command containing stock update data

        Returns:
            DTO representing the updated stock

        Raises:
            ValueError: If stock not found or no fields to update
        """
        try:
            with self._unit_of_work:
                # Validate command and retrieve stock entity
                stock_entity = self._validate_update_command_and_get_stock(command)

                # Apply updates and save
                self._apply_updates_and_save(command, stock_entity)

                # Commit transaction
                self._unit_of_work.commit()

                return StockDto.from_entity(stock_entity)

        except Exception:
            self._unit_of_work.rollback()
            raise

    def _validate_update_command_and_get_stock(
        self, command: UpdateStockCommand
    ) -> Stock:
        """Validate update command and retrieve stock entity."""
        # Check if stock exists
        stock_entity = self._unit_of_work.stocks.get_by_id(command.stock_id)

        if stock_entity is None:
            raise ValueError(f"Stock with ID {command.stock_id} not found")

        # Validate that there are fields to update
        if not command.has_updates():
            raise ValueError("No fields to update")

        # Check for duplicate symbol if symbol is being changed
        if command.symbol and command.symbol != stock_entity.symbol.value:
            symbol_vo = StockSymbol(command.symbol)
            existing_stock = self._unit_of_work.stocks.get_by_symbol(symbol_vo)
            if existing_stock is not None and existing_stock.id != command.stock_id:
                raise ValueError(f"Stock with symbol {command.symbol} already exists")

        return stock_entity

    def _apply_updates_and_save(
        self, command: UpdateStockCommand, stock_entity: Stock
    ) -> None:
        """Apply updates to stock entity and save to repository."""
        # Get the fields to update and apply them to the entity
        update_fields = command.get_update_fields()
        stock_entity.update_fields(**update_fields)

        # Persist changes
        update_success = self._unit_of_work.stocks.update(stock_entity.id, stock_entity)

        if not update_success:
            raise ValueError("Failed to update stock")
