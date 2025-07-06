"""Journal entry table definition using SQLAlchemy Core.

This module defines the journal entry table structure for tracking
investment research, decisions, and notes.
"""

from sqlalchemy import Column, DateTime, Index, String, Table, Text, text

from src.infrastructure.persistence.tables.stock_table import metadata

from .table_utils import (
    enum_check_constraint,
    foreign_key_column,
    id_column,
    timestamp_columns,
)


# Define the journal entry table using SQLAlchemy Core
journal_entry_table: Table = Table(
    "journal_entries",
    metadata,
    id_column(),
    foreign_key_column("portfolio_id", "portfolios", nullable=True),  # Can be general
    foreign_key_column("stock_id", "stocks", nullable=True),  # Can be portfolio-level
    Column("entry_type", String, nullable=False),
    Column("title", String, nullable=False),
    Column("content", Text, nullable=False),
    Column("tags", String, nullable=True),  # Comma-separated tags
    Column(
        "entry_date",
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    *timestamp_columns(),
    # Check constraint for entry type
    enum_check_constraint(
        "entry_type", ["RESEARCH", "DECISION", "REVIEW", "NOTE"], "ck_entry_type"
    ),
    # Indexes for common queries
    Index("idx_portfolio_entries", "portfolio_id"),
    Index("idx_stock_entries", "stock_id"),
    Index("idx_entry_date", "entry_date"),
)
