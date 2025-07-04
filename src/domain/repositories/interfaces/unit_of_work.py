"""
Unit of Work interfaces.

Defines the contracts for transaction management and repository coordination.
"""

from abc import ABC, abstractmethod
from typing import Any

from .journal_repository import IJournalRepository
from .portfolio_balance_repository import IPortfolioBalanceRepository
from .portfolio_repository import IPortfolioRepository
from .stock_repository import IStockRepository
from .target_repository import ITargetRepository
from .transaction_repository import ITransactionRepository


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
        exc_type: type | None,
        exc_val: Exception | None,
        exc_tb: Any | None,
    ) -> bool | None:
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
