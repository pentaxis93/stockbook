"""Repository interfaces for the StockBook domain.

These interfaces define the contracts for data persistence
without coupling the domain to specific implementations.
"""

# Re-export all interfaces from the new package structure
from .interfaces import (
    IJournalRepository,
    IPortfolioBalanceRepository,
    IPortfolioRepository,
    IStockBookUnitOfWork,
    IStockRepository,
    ITargetRepository,
    ITransactionRepository,
    IUnitOfWork,
)


# pylint: disable=duplicate-code
# Rationale: This duplicate list is necessary for proper module re-exports.
# The interfaces package defines the same list, but both modules need it
# to properly expose the public API at different import levels.
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
