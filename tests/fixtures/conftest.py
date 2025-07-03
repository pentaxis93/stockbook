"""
Pytest configuration for infrastructure fixtures.

This file makes all fixtures from infrastructure.py available to tests
in this directory and subdirectories.
"""

# Import all fixtures to make them available
from .infrastructure import (
    mock_journal_repository,
    mock_portfolio_balance_repository,
    mock_portfolio_repository,
    mock_stock_repository,
    mock_target_repository,
    mock_transaction_repository,
    mock_unit_of_work,
    sample_stocks,
    seed_test_portfolio_sqlalchemy,
    seed_test_stocks_sqlalchemy,
    sqlalchemy_connection,
    sqlalchemy_in_memory_engine,
    stock_builder,
)

# Re-export for pytest discovery
__all__ = [
    "sqlalchemy_in_memory_engine",
    "sqlalchemy_connection",
    "mock_stock_repository",
    "mock_portfolio_repository",
    "mock_transaction_repository",
    "mock_target_repository",
    "mock_portfolio_balance_repository",
    "mock_journal_repository",
    "mock_unit_of_work",
    "stock_builder",
    "sample_stocks",
    "seed_test_stocks_sqlalchemy",
    "seed_test_portfolio_sqlalchemy",
]
