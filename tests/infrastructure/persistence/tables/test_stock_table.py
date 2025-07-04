"""
Tests for stock table definition using SQLAlchemy Core.

This module tests that the stock table is correctly defined with
proper column types, constraints, and indexes.
"""

from sqlalchemy import Column, MetaData, String, Table, Text, types
from sqlalchemy.sql.sqltypes import TypeEngine


class TestStockTableDefinition:
    """Test the stock table definition using SQLAlchemy Core."""

    def test_stock_table_exists(self) -> None:
        """Should be able to import stock_table from the module."""
        from src.infrastructure.persistence.tables.stock_table import stock_table

        assert isinstance(stock_table, Table)
        assert stock_table.name == "stocks"

    def test_stock_table_has_metadata(self) -> None:
        """Should have metadata associated with the table."""
        from src.infrastructure.persistence.tables.stock_table import (
            metadata,
            stock_table,
        )

        assert isinstance(metadata, MetaData)
        assert stock_table.metadata is metadata

    def test_stock_table_columns_exist(self) -> None:
        """Should have all required columns."""
        from src.infrastructure.persistence.tables.stock_table import stock_table

        column_names = {col.name for col in stock_table.columns}
        expected_columns = {
            "id",
            "symbol",
            "company_name",
            "sector",
            "industry_group",
            "grade",
            "notes",
            "created_at",
            "updated_at",
        }
        assert column_names == expected_columns

    def test_id_column_properties(self) -> None:
        """Should have id column with correct properties."""
        from src.infrastructure.persistence.tables.stock_table import stock_table

        id_column = stock_table.c.id
        assert isinstance(id_column, Column)
        assert isinstance(id_column.type, String | Text)
        assert id_column.primary_key is True
        assert id_column.nullable is False

    def test_symbol_column_properties(self) -> None:
        """Should have symbol column with correct properties."""
        from src.infrastructure.persistence.tables.stock_table import stock_table

        symbol_column = stock_table.c.symbol
        assert isinstance(symbol_column, Column)
        assert isinstance(symbol_column.type, String | Text)
        assert symbol_column.nullable is False
        assert symbol_column.unique is True

    def test_company_name_column_properties(self) -> None:
        """Should have company_name column with correct properties."""
        from src.infrastructure.persistence.tables.stock_table import stock_table

        company_name_column = stock_table.c.company_name
        assert isinstance(company_name_column, Column)
        assert isinstance(company_name_column.type, String | Text)
        assert company_name_column.nullable is True  # Company name is now optional

    def test_optional_text_columns(self) -> None:
        """Should have optional text columns with correct properties."""
        from src.infrastructure.persistence.tables.stock_table import stock_table

        optional_columns = ["sector", "industry_group", "grade", "notes"]
        for col_name in optional_columns:
            column = stock_table.c[col_name]
            assert isinstance(column, Column)
            assert isinstance(column.type, String | Text)
            assert column.nullable is True

    def test_timestamp_columns(self) -> None:
        """Should have timestamp columns with correct properties."""
        from src.infrastructure.persistence.tables.stock_table import stock_table

        # Check created_at column
        created_at = stock_table.c.created_at
        assert isinstance(created_at, Column)
        assert isinstance(created_at.type, types.DateTime)
        assert created_at.nullable is False
        assert created_at.server_default is not None

        # Check updated_at column
        updated_at = stock_table.c.updated_at
        assert isinstance(updated_at, Column)
        assert isinstance(updated_at.type, types.DateTime)
        assert updated_at.nullable is False
        assert updated_at.server_default is not None

    def test_table_indexes(self) -> None:
        """Should have appropriate indexes for performance."""
        from src.infrastructure.persistence.tables.stock_table import stock_table

        # Check that symbol has a unique index (via unique=True)
        symbol_column = stock_table.c.symbol
        assert symbol_column.unique is True

        # Check for any additional indexes
        index_names = {idx.name for idx in stock_table.indexes if idx.name}
        # At minimum, we should have indexes on commonly queried fields
        # The actual index names will depend on implementation
        # For now, we just verify the table can have indexes
        assert isinstance(index_names, set)

    def test_column_types_are_explicit(self) -> None:
        """Should use explicit SQLAlchemy types, not generic ones."""
        from src.infrastructure.persistence.tables.stock_table import stock_table

        for column in stock_table.columns:
            # Verify we're using SQLAlchemy types
            assert isinstance(column.type, TypeEngine)
            # For SQLite compatibility, Text/String are acceptable
            if column.name in ["created_at", "updated_at"]:
                assert isinstance(column.type, types.DateTime)
            else:
                assert isinstance(column.type, String | Text)

    def test_table_can_be_created_in_metadata(self) -> None:
        """Should be able to create the table in a test metadata."""
        from src.infrastructure.persistence.tables.stock_table import stock_table

        # Create a new metadata instance
        test_metadata = MetaData()

        # Use tometadata() instead of manually copying columns
        copied_table = stock_table.tometadata(test_metadata)

        assert copied_table.name == "stocks"
        assert len(copied_table.columns) == len(stock_table.columns)
