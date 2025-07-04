"""
Target table definition using SQLAlchemy Core.

This module defines the target table structure for portfolio allocation targets.
"""

from sqlalchemy import (
    CheckConstraint,
    Column,
    Numeric,
    Table,
    UniqueConstraint,
)

from src.infrastructure.persistence.tables.stock_table import metadata

from .table_utils import foreign_key_column, id_column, timestamp_columns

# Define the target table using SQLAlchemy Core
target_table: Table = Table(
    "targets",
    metadata,
    id_column(),
    foreign_key_column("portfolio_id", "portfolios"),
    foreign_key_column("stock_id", "stocks"),
    Column(
        "target_percentage",
        Numeric(precision=5, scale=2),  # Supports 0.00 to 999.99
        nullable=False,
    ),
    *timestamp_columns(),
    # Composite unique constraint
    UniqueConstraint("portfolio_id", "stock_id", name="uq_portfolio_stock"),
    # Check constraint for percentage
    CheckConstraint(
        "target_percentage >= 0 AND target_percentage <= 100",
        name="ck_target_percentage_range",
    ),
)
