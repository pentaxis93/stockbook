"""
Pytest configuration for infrastructure fixtures.

This file makes all fixtures from infrastructure.py available to tests
in this directory and subdirectories.
"""

# Import all fixtures to make them available
from .infrastructure import (
    db_transaction,
    in_memory_db,
    mock_journal_repository,
    mock_portfolio_balance_repository,
    mock_portfolio_repository,
    mock_stock_repository,
    mock_target_repository,
    mock_transaction_repository,
    mock_unit_of_work,
    sample_stocks,
    seed_test_portfolio,
    seed_test_stocks,
    stock_builder,
    transaction_rollback,
)

# Re-export for pytest discovery
__all__ = [
    "in_memory_db",
    "transaction_rollback",
    "mock_stock_repository",
    "mock_portfolio_repository",
    "mock_transaction_repository",
    "mock_target_repository",
    "mock_portfolio_balance_repository",
    "mock_journal_repository",
    "mock_unit_of_work",
    "stock_builder",
    "sample_stocks",
    "db_transaction",
    "seed_test_stocks",
    "seed_test_portfolio",
]
