"""Portfolio balance table definition using SQLAlchemy Core.

This module defines the portfolio balance table structure for tracking
current stock holdings and average costs.
"""

from sqlalchemy import Column, Numeric, Table, UniqueConstraint, text

from src.infrastructure.persistence.tables.stock_table import metadata

from .table_utils import base_columns, foreign_key_column

# Define the portfolio balance table using SQLAlchemy Core
portfolio_balance_table: Table = Table(
    "portfolio_balances",
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
    # Composite unique constraint - one balance per stock per portfolio
    UniqueConstraint("portfolio_id", "stock_id", name="uq_portfolio_stock_balance"),
)
