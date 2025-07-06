"""Stock table definition using SQLAlchemy Core.

This module defines the stock table structure using SQLAlchemy's Core
Table construct (not ORM) to maintain clean architecture separation.
"""

from sqlalchemy import Column, MetaData, String, Table

from .table_utils import id_column, timestamp_columns

# Create metadata instance for all tables
metadata: MetaData = MetaData()

# Define the stock table using SQLAlchemy Core
stock_table: Table = Table(
    "stocks",
    metadata,
    id_column(),
    Column("symbol", String, nullable=False, unique=True),
    Column("company_name", String, nullable=True),
    Column("sector", String, nullable=True),
    Column("industry_group", String, nullable=True),
    Column("grade", String, nullable=True),
    Column("notes", String, nullable=True),
    *timestamp_columns(),
)
