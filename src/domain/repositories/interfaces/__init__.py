"""Repository interfaces for domain entities.

This package contains abstract base classes defining repository contracts
for each aggregate root in the domain model, following Interface Segregation Principle.
"""

from .journal_repository import IJournalRepository
from .portfolio_balance_repository import IPortfolioBalanceRepository
from .portfolio_repository import IPortfolioRepository
from .stock_repository import IStockRepository
from .target_repository import ITargetRepository
from .transaction_repository import ITransactionRepository
from .unit_of_work import IStockBookUnitOfWork, IUnitOfWork

__all__ = [
    "IJournalRepository",
    "IPortfolioBalanceRepository",
    "IPortfolioRepository",
    "IStockBookUnitOfWork",
    "IStockRepository",
    "ITargetRepository",
    "ITransactionRepository",
    "IUnitOfWork",
]
