"""
Portfolio balance table definition using SQLAlchemy Core.

This module defines the portfolio balance table structure for tracking
current stock holdings and average costs.
"""

from sqlalchemy import (
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

# Define the portfolio balance table using SQLAlchemy Core
portfolio_balance_table: Table = Table(
    "portfolio_balances",
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
        "quantity",
        Numeric(
            precision=15, scale=4
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
    # Composite unique constraint - one balance per stock per portfolio
    UniqueConstraint("portfolio_id", "stock_id", name="uq_portfolio_stock_balance"),
)
