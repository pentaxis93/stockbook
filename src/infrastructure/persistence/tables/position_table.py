"""Position table definition using SQLAlchemy Core.

This module defines the position table structure for tracking
current stock holdings in portfolios with transaction history.
"""

from sqlalchemy import Column, DateTime, Numeric, Table, UniqueConstraint, text

from src.infrastructure.persistence.tables.stock_table import metadata

from .table_utils import base_columns, foreign_key_column

# Define the position table using SQLAlchemy Core
position_table: Table = Table(
    "positions",
    metadata,
    *base_columns(),
    foreign_key_column("portfolio_id", "portfolios"),
    foreign_key_column("stock_id", "stocks"),
    Column(
        "quantity",
        Numeric(
            precision=15,
            scale=4,
        ),  # Support large quantities with fractional shares
        nullable=False,
        server_default=text("0"),
    ),
    Column(
        "average_cost",
        Numeric(precision=15, scale=4),  # Support precise average cost tracking
        nullable=False,
        server_default=text("0"),
    ),
    Column(
        "last_transaction_date",
        DateTime,
        nullable=True,  # Can be null if no transactions yet
    ),
    # Composite unique constraint - one position per stock per portfolio
    UniqueConstraint("portfolio_id", "stock_id", name="uq_portfolio_stock_position"),
)
