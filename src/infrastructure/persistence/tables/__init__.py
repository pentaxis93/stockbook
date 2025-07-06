"""Database table definitions for StockBook.

This package contains SQLAlchemy Core table definitions.
All tables share a common metadata instance for schema management.
"""

from src.infrastructure.persistence.tables.journal_entry_table import (
    journal_entry_table,
)
from src.infrastructure.persistence.tables.portfolio_balance_table import (
    portfolio_balance_table,
)
from src.infrastructure.persistence.tables.portfolio_table import portfolio_table
from src.infrastructure.persistence.tables.stock_table import metadata, stock_table
from src.infrastructure.persistence.tables.target_table import target_table
from src.infrastructure.persistence.tables.transaction_table import transaction_table


__all__ = [
    "journal_entry_table",
    "metadata",
    "portfolio_balance_table",
    "portfolio_table",
    "stock_table",
    "target_table",
    "transaction_table",
]
