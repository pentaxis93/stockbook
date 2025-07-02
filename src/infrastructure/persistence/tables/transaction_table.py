"""
Transaction table definition using SQLAlchemy Core.

This module defines the transaction table structure for buy/sell transactions.
"""

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Table,
    text,
)

from src.infrastructure.persistence.tables.stock_table import metadata

# Define the transaction table using SQLAlchemy Core
transaction_table: Table = Table(
    "transactions",
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
    Column("transaction_type", String, nullable=False),
    Column(
        "quantity",
        Numeric(
            precision=15, scale=4
        ),  # Support large quantities with fractional shares
        nullable=False,
    ),
    Column(
        "price",
        Numeric(precision=15, scale=4),  # Support precise pricing
        nullable=False,
    ),
    Column(
        "commission",
        Numeric(precision=10, scale=2),
        nullable=True,
        server_default=text("0"),
    ),
    Column("notes", String, nullable=True),
    Column("transaction_date", DateTime, nullable=False),
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
    # Check constraint for transaction type
    CheckConstraint("transaction_type IN ('BUY', 'SELL')", name="ck_transaction_type"),
)
