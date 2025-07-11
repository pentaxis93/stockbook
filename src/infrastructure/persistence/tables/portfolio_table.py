"""Portfolio table definition using SQLAlchemy Core.

This module defines the portfolio table structure using SQLAlchemy's Core
Table construct (not ORM) to maintain clean architecture separation.
"""

from sqlalchemy import Column, String, Table, text

from src.infrastructure.persistence.tables.stock_table import metadata

from .table_utils import base_columns

# Define the portfolio table using SQLAlchemy Core
portfolio_table: Table = Table(
    "portfolios",
    metadata,
    *base_columns(),
    Column("name", String, nullable=False, unique=True),
    Column("description", String, nullable=True),
    Column("currency", String, nullable=False, server_default=text("'USD'")),
)
