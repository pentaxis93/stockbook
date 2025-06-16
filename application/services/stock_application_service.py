"""
Stock application service.

Orchestrates stock-related use cases and coordinates between
domain entities and repositories.
"""

from typing import List, Optional
from application.commands.stock_commands import CreateStockCommand
from application.dto.stock_dto import StockDto
from domain.entities.stock_entity import StockEntity
from domain.value_objects.stock_symbol import StockSymbol
from domain.repositories.interfaces import IUnitOfWork


class StockApplicationService:
    """
    Application service for stock operations.
    
    Provides high-level use case operations for stock management,
    coordinating between domain entities and repositories.
    """
    
    def __init__(self, unit_of_work: IUnitOfWork):
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
                    raise ValueError(f"Stock with symbol {command.symbol} already exists")
                
                # Create domain entity
                stock_entity = StockEntity(
                    symbol=symbol_vo,
                    name=command.name,
                    industry_group=command.industry_group,
                    grade=command.grade,
                    notes=command.notes
                )
                
                # Persist entity
                stock_id = self._unit_of_work.stocks.create(stock_entity)
                stock_entity.set_id(stock_id)
                
                # Commit transaction
                self._unit_of_work.commit()
                
                return StockDto.from_entity(stock_entity)
                
        except Exception as e:
            self._unit_of_work.rollback()
            raise
    
    def get_stock_by_symbol(self, symbol: str) -> Optional[StockDto]:
        """
        Retrieve stock by symbol.
        
        Args:
            symbol: Stock symbol to search for
            
        Returns:
            Stock DTO if found, None otherwise
        """
        symbol_vo = StockSymbol(symbol)
        stock_entity = self._unit_of_work.stocks.get_by_symbol(symbol_vo)
        
        if stock_entity is None:
            return None
        
        return StockDto.from_entity(stock_entity)
    
    def get_all_stocks(self) -> List[StockDto]:
        """
        Retrieve all stocks.
        
        Returns:
            List of stock DTOs
        """
        stock_entities = self._unit_of_work.stocks.get_all()
        return [StockDto.from_entity(entity) for entity in stock_entities]
    
    def update_stock_grade(self, symbol: str, new_grade: Optional[str]) -> StockDto:
        """
        Update stock grade.
        
        Args:
            symbol: Stock symbol to update
            new_grade: New grade value
            
        Returns:
            Updated stock DTO
            
        Raises:
            ValueError: If stock not found
        """
        try:
            with self._unit_of_work:
                symbol_vo = StockSymbol(symbol)
                stock_entity = self._unit_of_work.stocks.get_by_symbol(symbol_vo)
                
                if stock_entity is None:
                    raise ValueError(f"Stock with symbol {symbol} not found")
                
                if stock_entity.id is None:
                    raise ValueError("Stock entity missing ID - cannot update")
                
                # Update domain entity
                stock_entity.update_grade(new_grade)
                
                # Persist changes
                self._unit_of_work.stocks.update(stock_entity.id, stock_entity)
                
                # Commit transaction
                self._unit_of_work.commit()
                
                return StockDto.from_entity(stock_entity)
                
        except Exception as e:
            self._unit_of_work.rollback()
            raise
    
    def stock_exists(self, symbol: str) -> bool:
        """
        Check if stock exists by symbol.
        
        Args:
            symbol: Stock symbol to check
            
        Returns:
            True if stock exists, False otherwise
        """
        symbol_vo = StockSymbol(symbol)
        return self._unit_of_work.stocks.exists_by_symbol(symbol_vo)