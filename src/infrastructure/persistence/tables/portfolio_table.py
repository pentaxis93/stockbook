"""
Portfolio table definition using SQLAlchemy Core.

This module defines the portfolio table structure using SQLAlchemy's Core
Table construct (not ORM) to maintain clean architecture separation.
"""

from sqlalchemy import Column, DateTime, String, Table, text

from src.infrastructure.persistence.tables.stock_table import metadata

# Define the portfolio table using SQLAlchemy Core
portfolio_table: Table = Table(
    "portfolios",
    metadata,
    Column("id", String, primary_key=True, nullable=False),
    Column("name", String, nullable=False, unique=True),
    Column("description", String, nullable=True),
    Column("currency", String, nullable=False, server_default=text("'USD'")),
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
)
