"""Transaction table definition using SQLAlchemy Core.

This module defines the transaction table structure for buy/sell transactions.
"""

from sqlalchemy import Column, DateTime, Numeric, String, Table, text

from src.infrastructure.persistence.tables.stock_table import metadata

from .table_utils import (
    enum_check_constraint,
    foreign_key_column,
    id_column,
    timestamp_columns,
)


# Define the transaction table using SQLAlchemy Core
transaction_table: Table = Table(
    "transactions",
    metadata,
    id_column(),
    foreign_key_column("portfolio_id", "portfolios"),
    foreign_key_column("stock_id", "stocks"),
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
    *timestamp_columns(),
    # Check constraint for transaction type
    enum_check_constraint("transaction_type", ["BUY", "SELL"], "ck_transaction_type"),
)
