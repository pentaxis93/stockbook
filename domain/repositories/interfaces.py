"""
Repository interface definitions for StockBook application.

This module defines abstract base classes for all repository operations,
following the Repository pattern and Interface Segregation Principle.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date
from decimal import Decimal

from models import Stock, Portfolio, Transaction, Target, PortfolioBalance, JournalEntry


class IStockRepository(ABC):
    """Abstract interface for stock data operations."""
    
    @abstractmethod
    def create(self, stock: Stock) -> int:
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
    def get_by_id(self, stock_id: int) -> Optional[Stock]:
        """
        Retrieve stock by ID.
        
        Args:
            stock_id: Stock identifier
            
        Returns:
            Stock domain model or None if not found
        """
        pass
    
    @abstractmethod
    def get_by_symbol(self, symbol: str) -> Optional[Stock]:
        """
        Retrieve stock by symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            Stock domain model or None if not found
        """
        pass
    
    @abstractmethod
    def get_all(self) -> List[Stock]:
        """
        Retrieve all stocks.
        
        Returns:
            List of Stock domain models
        """
        pass
    
    @abstractmethod
    def update(self, stock_id: int, stock: Stock) -> bool:
        """
        Update existing stock.
        
        Args:
            stock_id: Stock identifier
            stock: Updated stock domain model
            
        Returns:
            True if update successful, False otherwise
            
        Raises:
            ValidationError: If stock data is invalid
            DatabaseError: If update fails
        """
        pass
    
    @abstractmethod
    def delete(self, stock_id: int) -> bool:
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
    def exists_by_symbol(self, symbol: str) -> bool:
        """
        Check if stock exists by symbol.
        
        Args:
            symbol: Stock symbol to check
            
        Returns:
            True if stock exists, False otherwise
        """
        pass


class IPortfolioRepository(ABC):
    """Abstract interface for portfolio data operations."""
    
    @abstractmethod
    def create(self, portfolio: Portfolio) -> int:
        """
        Create a new portfolio.
        
        Args:
            portfolio: Portfolio domain model
            
        Returns:
            ID of the created portfolio
            
        Raises:
            ValidationError: If portfolio data is invalid
            DatabaseError: If creation fails
        """
        pass
    
    @abstractmethod
    def get_by_id(self, portfolio_id: int) -> Optional[Portfolio]:
        """
        Retrieve portfolio by ID.
        
        Args:
            portfolio_id: Portfolio identifier
            
        Returns:
            Portfolio domain model or None if not found
        """
        pass
    
    @abstractmethod
    def get_all_active(self) -> List[Portfolio]:
        """
        Retrieve all active portfolios.
        
        Returns:
            List of active Portfolio domain models
        """
        pass
    
    @abstractmethod
    def get_all(self) -> List[Portfolio]:
        """
        Retrieve all portfolios (active and inactive).
        
        Returns:
            List of all Portfolio domain models
        """
        pass
    
    @abstractmethod
    def update(self, portfolio_id: int, portfolio: Portfolio) -> bool:
        """
        Update existing portfolio.
        
        Args:
            portfolio_id: Portfolio identifier
            portfolio: Updated portfolio domain model
            
        Returns:
            True if update successful, False otherwise
            
        Raises:
            ValidationError: If portfolio data is invalid
            DatabaseError: If update fails
        """
        pass
    
    @abstractmethod
    def deactivate(self, portfolio_id: int) -> bool:
        """
        Deactivate portfolio (soft delete).
        
        Args:
            portfolio_id: Portfolio identifier
            
        Returns:
            True if deactivation successful, False otherwise
        """
        pass


class ITransactionRepository(ABC):
    """Abstract interface for transaction data operations."""
    
    @abstractmethod
    def create(self, transaction: Transaction) -> int:
        """
        Create a new transaction.
        
        Args:
            transaction: Transaction domain model
            
        Returns:
            ID of the created transaction
            
        Raises:
            ValidationError: If transaction data is invalid
            BusinessLogicError: If transaction violates business rules
            DatabaseError: If creation fails
        """
        pass
    
    @abstractmethod
    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """
        Retrieve transaction by ID.
        
        Args:
            transaction_id: Transaction identifier
            
        Returns:
            Transaction domain model or None if not found
        """
        pass
    
    @abstractmethod
    def get_by_portfolio(self, portfolio_id: int, limit: Optional[int] = None) -> List[Transaction]:
        """
        Retrieve transactions for a specific portfolio.
        
        Args:
            portfolio_id: Portfolio identifier
            limit: Maximum number of transactions to return
            
        Returns:
            List of Transaction domain models, ordered by date (newest first)
        """
        pass
    
    @abstractmethod
    def get_by_stock(self, stock_id: int, portfolio_id: Optional[int] = None) -> List[Transaction]:
        """
        Retrieve transactions for a specific stock.
        
        Args:
            stock_id: Stock identifier
            portfolio_id: Optional portfolio filter
            
        Returns:
            List of Transaction domain models
        """
        pass
    
    @abstractmethod
    def get_by_date_range(self, start_date: date, end_date: date, 
                         portfolio_id: Optional[int] = None) -> List[Transaction]:
        """
        Retrieve transactions within a date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            portfolio_id: Optional portfolio filter
            
        Returns:
            List of Transaction domain models
        """
        pass
    
    @abstractmethod
    def update(self, transaction_id: int, transaction: Transaction) -> bool:
        """
        Update existing transaction.
        
        Args:
            transaction_id: Transaction identifier
            transaction: Updated transaction domain model
            
        Returns:
            True if update successful, False otherwise
            
        Raises:
            ValidationError: If transaction data is invalid
            BusinessLogicError: If update violates business rules
            DatabaseError: If update fails
        """
        pass
    
    @abstractmethod
    def delete(self, transaction_id: int) -> bool:
        """
        Delete transaction by ID.
        
        Args:
            transaction_id: Transaction identifier
            
        Returns:
            True if deletion successful, False otherwise
            
        Raises:
            DatabaseError: If deletion fails
        """
        pass


class ITargetRepository(ABC):
    """Abstract interface for target data operations."""
    
    @abstractmethod
    def create(self, target: Target) -> int:
        """
        Create a new target.
        
        Args:
            target: Target domain model
            
        Returns:
            ID of the created target
            
        Raises:
            ValidationError: If target data is invalid
            DatabaseError: If creation fails
        """
        pass
    
    @abstractmethod
    def get_by_id(self, target_id: int) -> Optional[Target]:
        """
        Retrieve target by ID.
        
        Args:
            target_id: Target identifier
            
        Returns:
            Target domain model or None if not found
        """
        pass
    
    @abstractmethod
    def get_active_by_portfolio(self, portfolio_id: int) -> List[Target]:
        """
        Retrieve active targets for a portfolio.
        
        Args:
            portfolio_id: Portfolio identifier
            
        Returns:
            List of active Target domain models
        """
        pass
    
    @abstractmethod
    def get_active_by_stock(self, stock_id: int) -> List[Target]:
        """
        Retrieve active targets for a stock.
        
        Args:
            stock_id: Stock identifier
            
        Returns:
            List of active Target domain models
        """
        pass
    
    @abstractmethod
    def get_all_active(self) -> List[Target]:
        """
        Retrieve all active targets.
        
        Returns:
            List of active Target domain models
        """
        pass
    
    @abstractmethod
    def update(self, target_id: int, target: Target) -> bool:
        """
        Update existing target.
        
        Args:
            target_id: Target identifier
            target: Updated target domain model
            
        Returns:
            True if update successful, False otherwise
            
        Raises:
            ValidationError: If target data is invalid
            DatabaseError: If update fails
        """
        pass
    
    @abstractmethod
    def update_status(self, target_id: int, status: str) -> bool:
        """
        Update target status.
        
        Args:
            target_id: Target identifier
            status: New status ('active', 'hit', 'failed', 'cancelled')
            
        Returns:
            True if update successful, False otherwise
        """
        pass


class IPortfolioBalanceRepository(ABC):
    """Abstract interface for portfolio balance data operations."""
    
    @abstractmethod
    def create(self, balance: PortfolioBalance) -> int:
        """
        Create or update portfolio balance for a date.
        
        Args:
            balance: PortfolioBalance domain model
            
        Returns:
            ID of the created/updated balance record
            
        Raises:
            ValidationError: If balance data is invalid
            DatabaseError: If operation fails
        """
        pass
    
    @abstractmethod
    def get_by_id(self, balance_id: int) -> Optional[PortfolioBalance]:
        """
        Retrieve portfolio balance by ID.
        
        Args:
            balance_id: Balance record identifier
            
        Returns:
            PortfolioBalance domain model or None if not found
        """
        pass
    
    @abstractmethod
    def get_by_portfolio_and_date(self, portfolio_id: int, balance_date: date) -> Optional[PortfolioBalance]:
        """
        Retrieve portfolio balance for a specific date.
        
        Args:
            portfolio_id: Portfolio identifier
            balance_date: Balance date
            
        Returns:
            PortfolioBalance domain model or None if not found
        """
        pass
    
    @abstractmethod
    def get_history(self, portfolio_id: int, limit: Optional[int] = None) -> List[PortfolioBalance]:
        """
        Retrieve balance history for a portfolio.
        
        Args:
            portfolio_id: Portfolio identifier
            limit: Maximum number of records to return
            
        Returns:
            List of PortfolioBalance domain models, ordered by date (newest first)
        """
        pass
    
    @abstractmethod
    def get_latest_balance(self, portfolio_id: int) -> Optional[PortfolioBalance]:
        """
        Retrieve the most recent balance for a portfolio.
        
        Args:
            portfolio_id: Portfolio identifier
            
        Returns:
            Latest PortfolioBalance domain model or None if not found
        """
        pass


class IJournalRepository(ABC):
    """Abstract interface for journal entry data operations."""
    
    @abstractmethod
    def create(self, entry: JournalEntry) -> int:
        """
        Create a new journal entry.
        
        Args:
            entry: JournalEntry domain model
            
        Returns:
            ID of the created entry
            
        Raises:
            ValidationError: If entry data is invalid
            DatabaseError: If creation fails
        """
        pass
    
    @abstractmethod
    def get_by_id(self, entry_id: int) -> Optional[JournalEntry]:
        """
        Retrieve journal entry by ID.
        
        Args:
            entry_id: Entry identifier
            
        Returns:
            JournalEntry domain model or None if not found
        """
        pass
    
    @abstractmethod
    def get_recent(self, limit: Optional[int] = None) -> List[JournalEntry]:
        """
        Retrieve recent journal entries.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of JournalEntry domain models, ordered by date (newest first)
        """
        pass
    
    @abstractmethod
    def get_by_portfolio(self, portfolio_id: int, limit: Optional[int] = None) -> List[JournalEntry]:
        """
        Retrieve journal entries for a specific portfolio.
        
        Args:
            portfolio_id: Portfolio identifier
            limit: Maximum number of entries to return
            
        Returns:
            List of JournalEntry domain models
        """
        pass
    
    @abstractmethod
    def get_by_stock(self, stock_id: int, limit: Optional[int] = None) -> List[JournalEntry]:
        """
        Retrieve journal entries for a specific stock.
        
        Args:
            stock_id: Stock identifier
            limit: Maximum number of entries to return
            
        Returns:
            List of JournalEntry domain models
        """
        pass
    
    @abstractmethod
    def get_by_transaction(self, transaction_id: int) -> List[JournalEntry]:
        """
        Retrieve journal entries for a specific transaction.
        
        Args:
            transaction_id: Transaction identifier
            
        Returns:
            List of JournalEntry domain models
        """
        pass
    
    @abstractmethod
    def get_by_date_range(self, start_date: date, end_date: date) -> List[JournalEntry]:
        """
        Retrieve journal entries within a date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of JournalEntry domain models
        """
        pass
    
    @abstractmethod
    def update(self, entry_id: int, entry: JournalEntry) -> bool:
        """
        Update existing journal entry.
        
        Args:
            entry_id: Entry identifier
            entry: Updated entry domain model
            
        Returns:
            True if update successful, False otherwise
            
        Raises:
            ValidationError: If entry data is invalid
            DatabaseError: If update fails
        """
        pass
    
    @abstractmethod
    def delete(self, entry_id: int) -> bool:
        """
        Delete journal entry by ID.
        
        Args:
            entry_id: Entry identifier
            
        Returns:
            True if deletion successful, False otherwise
            
        Raises:
            DatabaseError: If deletion fails
        """
        pass


class IUnitOfWork(ABC):
    """
    Abstract interface for Unit of Work pattern.
    
    Provides transaction management and coordinates multiple repository operations
    to ensure data consistency across multiple aggregate changes.
    """
    
    @abstractmethod
    def __enter__(self):
        """Enter transaction context."""
        pass
    
    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit transaction context with rollback on exception."""
        pass
    
    @abstractmethod
    def commit(self) -> None:
        """
        Commit all changes made within the unit of work.
        
        Raises:
            DatabaseError: If commit fails
        """
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        """
        Roll back all changes made within the unit of work.
        
        Raises:
            DatabaseError: If rollback fails
        """
        pass
    
    # Repository access properties
    @property
    @abstractmethod
    def stocks(self) -> IStockRepository:
        """Get stock repository instance."""
        pass
    
    @property
    @abstractmethod
    def portfolios(self) -> IPortfolioRepository:
        """Get portfolio repository instance."""
        pass
    
    @property
    @abstractmethod
    def transactions(self) -> ITransactionRepository:
        """Get transaction repository instance."""
        pass
    
    @property
    @abstractmethod
    def targets(self) -> ITargetRepository:
        """Get target repository instance."""
        pass
    
    @property
    @abstractmethod
    def balances(self) -> IPortfolioBalanceRepository:
        """Get portfolio balance repository instance."""
        pass
    
    @property
    @abstractmethod
    def journal(self) -> IJournalRepository:
        """Get journal repository instance."""
        pass