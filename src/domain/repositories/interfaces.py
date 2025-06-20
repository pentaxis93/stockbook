"""
Repository interface definitions for StockBook application.

This module defines abstract base classes for all repository operations,
following the Repository pattern and Interface Segregation Principle.
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Any, List, Optional

# Import domain entities and value objects
from src.domain.entities import (
    JournalEntryEntity,
    PortfolioBalanceEntity,
    PortfolioEntity,
    StockEntity,
    TargetEntity,
    TransactionEntity,
)
from src.domain.value_objects.stock_symbol import StockSymbol


class IStockRepository(ABC):
    """Abstract interface for stock data operations."""

    @abstractmethod
    def create(self, stock: StockEntity) -> int:
        """
        Create a new stock record.

        Args:
            stock: StockEntity domain model

        Returns:
            ID of the created stock

        Raises:
            ValidationError: If stock data is invalid
            DatabaseError: If creation fails
        """
        pass

    @abstractmethod
    def get_by_id(self, stock_id: int) -> Optional[StockEntity]:
        """
        Retrieve stock by ID.

        Args:
            stock_id: Stock identifier

        Returns:
            StockEntity domain model or None if not found
        """
        pass

    @abstractmethod
    def get_by_symbol(self, symbol: StockSymbol) -> Optional[StockEntity]:
        """
        Retrieve stock by symbol.

        Args:
            symbol: Stock symbol value object

        Returns:
            StockEntity domain model or None if not found
        """
        pass

    @abstractmethod
    def get_all(self) -> List[StockEntity]:
        """
        Retrieve all stocks.

        Returns:
            List of StockEntity domain models
        """
        pass

    @abstractmethod
    def update(self, stock_id: int, stock: StockEntity) -> bool:
        """
        Update existing stock.

        Args:
            stock_id: Stock identifier
            stock: Updated StockEntity domain model

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
    def get_by_grade(self, grade: str) -> List[StockEntity]:
        """
        Retrieve stocks by grade.

        Args:
            grade: Stock grade to filter by (A, B, or C)

        Returns:
            List of StockEntity domain models with the specified grade
        """
        pass

    @abstractmethod
    def get_by_industry_group(self, industry_group: str) -> List[StockEntity]:
        """
        Retrieve all stocks in a specific industry group.

        Args:
            industry_group: Industry group to filter by

        Returns:
            List of StockEntity domain models in the industry group
        """
        pass

    @abstractmethod
    def get_by_sector(self, sector: str) -> List[StockEntity]:
        """
        Retrieve all stocks in a specific sector.

        Args:
            sector: Sector to filter by

        Returns:
            List of StockEntity domain models in the sector
        """
        pass

    @abstractmethod
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
        pass


class IPortfolioRepository(ABC):
    """Abstract interface for portfolio data operations."""

    @abstractmethod
    def create(self, portfolio: PortfolioEntity) -> int:
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
    def get_by_id(self, portfolio_id: int) -> Optional[PortfolioEntity]:
        """
        Retrieve portfolio by ID.

        Args:
            portfolio_id: Portfolio identifier

        Returns:
            Portfolio domain model or None if not found
        """
        pass

    @abstractmethod
    def get_all_active(self) -> List[PortfolioEntity]:
        """
        Retrieve all active portfolios.

        Returns:
            List of active Portfolio domain models
        """
        pass

    @abstractmethod
    def get_all(self) -> List[PortfolioEntity]:
        """
        Retrieve all portfolios (active and inactive).

        Returns:
            List of all Portfolio domain models
        """
        pass

    @abstractmethod
    def update(self, portfolio_id: int, portfolio: PortfolioEntity) -> bool:
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
    def create(self, transaction: TransactionEntity) -> int:
        """
        Create a new transaction.

        Args:
            transaction: TransactionEntity domain model

        Returns:
            ID of the created transaction

        Raises:
            ValidationError: If transaction data is invalid
            BusinessLogicError: If transaction violates business rules
            DatabaseError: If creation fails
        """
        pass

    @abstractmethod
    def get_by_id(self, transaction_id: int) -> Optional[TransactionEntity]:
        """
        Retrieve transaction by ID.

        Args:
            transaction_id: Transaction identifier

        Returns:
            Transaction domain model or None if not found
        """
        pass

    @abstractmethod
    def get_by_portfolio(
        self, portfolio_id: int, limit: Optional[int] = None
    ) -> List[TransactionEntity]:
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
    def get_by_stock(
        self, stock_id: int, portfolio_id: Optional[int] = None
    ) -> List[TransactionEntity]:
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
    def get_by_date_range(
        self, start_date: date, end_date: date, portfolio_id: Optional[int] = None
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
        pass

    @abstractmethod
    def update(self, transaction_id: int, transaction: TransactionEntity) -> bool:
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
    def create(self, target: TargetEntity) -> int:
        """
        Create a new target.

        Args:
            target: TargetEntity domain model

        Returns:
            ID of the created target

        Raises:
            ValidationError: If target data is invalid
            DatabaseError: If creation fails
        """
        pass

    @abstractmethod
    def get_by_id(self, target_id: int) -> Optional[TargetEntity]:
        """
        Retrieve target by ID.

        Args:
            target_id: Target identifier

        Returns:
            Target domain model or None if not found
        """
        pass

    @abstractmethod
    def get_active_by_portfolio(self, portfolio_id: int) -> List[TargetEntity]:
        """
        Retrieve active targets for a portfolio.

        Args:
            portfolio_id: Portfolio identifier

        Returns:
            List of active Target domain models
        """
        pass

    @abstractmethod
    def get_active_by_stock(self, stock_id: int) -> List[TargetEntity]:
        """
        Retrieve active targets for a stock.

        Args:
            stock_id: Stock identifier

        Returns:
            List of active Target domain models
        """
        pass

    @abstractmethod
    def get_all_active(self) -> List[TargetEntity]:
        """
        Retrieve all active targets.

        Returns:
            List of active Target domain models
        """
        pass

    @abstractmethod
    def update(self, target_id: int, target: TargetEntity) -> bool:
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
    def create(self, balance: PortfolioBalanceEntity) -> int:
        """
        Create or update portfolio balance for a date.

        Args:
            balance: PortfolioBalanceEntity domain model

        Returns:
            ID of the created/updated balance record

        Raises:
            ValidationError: If balance data is invalid
            DatabaseError: If operation fails
        """
        pass

    @abstractmethod
    def get_by_id(self, balance_id: int) -> Optional[PortfolioBalanceEntity]:
        """
        Retrieve portfolio balance by ID.

        Args:
            balance_id: Balance record identifier

        Returns:
            PortfolioBalance domain model or None if not found
        """
        pass

    @abstractmethod
    def get_by_portfolio_and_date(
        self, portfolio_id: int, balance_date: date
    ) -> Optional[PortfolioBalanceEntity]:
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
    def get_history(
        self, portfolio_id: int, limit: Optional[int] = None
    ) -> List[PortfolioBalanceEntity]:
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
    def get_latest_balance(self, portfolio_id: int) -> Optional[PortfolioBalanceEntity]:
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
    def create(self, entry: JournalEntryEntity) -> int:
        """
        Create a new journal entry.

        Args:
            entry: JournalEntryEntity domain model

        Returns:
            ID of the created entry

        Raises:
            ValidationError: If entry data is invalid
            DatabaseError: If creation fails
        """
        pass

    @abstractmethod
    def get_by_id(self, entry_id: int) -> Optional[JournalEntryEntity]:
        """
        Retrieve journal entry by ID.

        Args:
            entry_id: Entry identifier

        Returns:
            JournalEntry domain model or None if not found
        """
        pass

    @abstractmethod
    def get_recent(self, limit: Optional[int] = None) -> List[JournalEntryEntity]:
        """
        Retrieve recent journal entries.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of JournalEntry domain models, ordered by date (newest first)
        """
        pass

    @abstractmethod
    def get_by_portfolio(
        self, portfolio_id: int, limit: Optional[int] = None
    ) -> List[JournalEntryEntity]:
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
    def get_by_stock(
        self, stock_id: int, limit: Optional[int] = None
    ) -> List[JournalEntryEntity]:
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
    def get_by_transaction(self, transaction_id: int) -> List[JournalEntryEntity]:
        """
        Retrieve journal entries for a specific transaction.

        Args:
            transaction_id: Transaction identifier

        Returns:
            List of JournalEntry domain models
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def update(self, entry_id: int, entry: JournalEntryEntity) -> bool:
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

    Defines the contract for transaction management that ensures
    data consistency across repository operations.
    """

    @abstractmethod
    def __enter__(self) -> "IUnitOfWork":
        """
        Enter the unit of work context.

        Returns:
            Self for use in context manager
        """
        pass

    @abstractmethod
    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> Optional[bool]:
        """
        Exit the unit of work context.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred

        Returns:
            Optional[bool]: True to suppress exceptions, False or None to propagate them
        """
        pass

    @abstractmethod
    def commit(self) -> None:
        """
        Commit all changes made during this unit of work.

        Raises:
            Exception: If commit fails for any reason
        """
        pass

    @abstractmethod
    def rollback(self) -> None:
        """
        Rollback all changes made during this unit of work.

        This should restore the system to the state it was in
        before this unit of work began.
        """
        pass


class IStockBookUnitOfWork(IUnitOfWork):
    """
    StockBook-specific Unit of Work interface.

    Extends the base IUnitOfWork pattern with domain-specific
    repository access for coordinating stock trading operations.
    """

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
