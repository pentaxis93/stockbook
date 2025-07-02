"""
Journal entry table definition using SQLAlchemy Core.

This module defines the journal entry table structure for tracking
investment research, decisions, and notes.
"""

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    String,
    Table,
    Text,
    text,
)

from src.infrastructure.persistence.tables.stock_table import metadata

# Define the journal entry table using SQLAlchemy Core
journal_entry_table: Table = Table(
    "journal_entries",
    metadata,
    Column("id", String, primary_key=True, nullable=False),
    Column(
        "portfolio_id",
        String,
        ForeignKey("portfolios.id"),
        nullable=True,  # Journal entries can be general
    ),
    Column(
        "stock_id",
        String,
        ForeignKey("stocks.id"),
        nullable=True,  # Journal entries can be portfolio-level
    ),
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
    Column(
        "created_at",
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    Column(
        "updated_at",
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    # Check constraint for entry type
    CheckConstraint(
        "entry_type IN ('RESEARCH', 'DECISION', 'REVIEW', 'NOTE')", name="ck_entry_type"
    ),
    # Indexes for common queries
    Index("idx_portfolio_entries", "portfolio_id"),
    Index("idx_stock_entries", "stock_id"),
    Index("idx_entry_date", "entry_date"),
)
