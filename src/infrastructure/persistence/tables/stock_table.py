"""
Stock table definition using SQLAlchemy Core.

This module defines the stock table structure using SQLAlchemy's Core
Table construct (not ORM) to maintain clean architecture separation.
"""

from sqlalchemy import Column, DateTime, MetaData, String, Table, text

# Create metadata instance for all tables
metadata: MetaData = MetaData()

# Define the stock table using SQLAlchemy Core
stock_table: Table = Table(
    "stocks",
    metadata,
    Column("id", String, primary_key=True, nullable=False),
    Column("symbol", String, nullable=False, unique=True),
    Column("company_name", String, nullable=False),
    Column("sector", String, nullable=True),
    Column("industry_group", String, nullable=True),
    Column("grade", String, nullable=True),
    Column("notes", String, nullable=True),
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
