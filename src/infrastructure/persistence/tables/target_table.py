"""
Target table definition using SQLAlchemy Core.

This module defines the target table structure for portfolio allocation targets.
"""

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Table,
    UniqueConstraint,
    text,
)

from src.infrastructure.persistence.tables.stock_table import metadata

# Define the target table using SQLAlchemy Core
target_table: Table = Table(
    "targets",
    metadata,
    Column("id", String, primary_key=True, nullable=False),
    Column(
        "portfolio_id",
        String,
        ForeignKey("portfolios.id"),
        nullable=False,
    ),
    Column(
        "stock_id",
        String,
        ForeignKey("stocks.id"),
        nullable=False,
    ),
    Column(
        "target_percentage",
        Numeric(precision=5, scale=2),  # Supports 0.00 to 999.99
        nullable=False,
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
    # Composite unique constraint
    UniqueConstraint("portfolio_id", "stock_id", name="uq_portfolio_stock"),
    # Check constraint for percentage
    CheckConstraint(
        "target_percentage >= 0 AND target_percentage <= 100",
        name="ck_target_percentage_range",
    ),
)
