"""Tests for transaction table definition."""

import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.engine import Engine

from src.infrastructure.persistence.tables.transaction_table import (
    metadata,
    transaction_table,
)


class TestTransactionTable:
    """Test suite for transaction table definition."""

    def test_transaction_table_exists(self) -> None:
        """Test that transaction table is defined."""
        assert transaction_table is not None
        assert transaction_table.name == "transactions"

    def test_transaction_table_columns(self) -> None:
        """Test that transaction table has all required columns."""
        columns = {col.name: col for col in transaction_table.columns}

        # Check required columns exist
        assert "id" in columns
        assert "portfolio_id" in columns
        assert "stock_id" in columns
        assert "transaction_type" in columns
        assert "quantity" in columns
        assert "price" in columns
        assert "commission" in columns
        assert "notes" in columns
        assert "transaction_date" in columns
        assert "created_at" in columns
        assert "updated_at" in columns

    def test_transaction_table_column_types(self) -> None:
        """Test that transaction table columns have correct types."""
        columns = {col.name: col for col in transaction_table.columns}

        # Check column types
        assert isinstance(columns["id"].type, sa.String)
        assert isinstance(columns["portfolio_id"].type, sa.String)
        assert isinstance(columns["stock_id"].type, sa.String)
        assert isinstance(columns["transaction_type"].type, sa.String)
        assert isinstance(columns["quantity"].type, sa.Numeric)
        assert isinstance(columns["price"].type, sa.Numeric)
        assert isinstance(columns["commission"].type, sa.Numeric)
        assert isinstance(columns["notes"].type, sa.String)
        assert isinstance(columns["transaction_date"].type, sa.DateTime)
        assert isinstance(columns["created_at"].type, sa.DateTime)
        assert isinstance(columns["updated_at"].type, sa.DateTime)

    def test_transaction_table_constraints(self) -> None:
        """Test that transaction table has correct constraints."""
        columns = {col.name: col for col in transaction_table.columns}

        # Primary key
        assert columns["id"].primary_key is True

        # Not nullable columns
        assert columns["id"].nullable is False
        assert columns["portfolio_id"].nullable is False
        assert columns["stock_id"].nullable is False
        assert columns["transaction_type"].nullable is False
        assert columns["quantity"].nullable is False
        assert columns["price"].nullable is False
        assert columns["transaction_date"].nullable is False
        assert columns["created_at"].nullable is False
        assert columns["updated_at"].nullable is False

        # Nullable columns
        assert columns["commission"].nullable is True
        assert columns["notes"].nullable is True

    def test_transaction_table_foreign_keys(self) -> None:
        """Test that transaction table has correct foreign key relationships."""
        foreign_keys = list(transaction_table.foreign_keys)

        # Should have two foreign keys
        assert len(foreign_keys) == 2

        # Check foreign key targets
        fk_targets = {fk.target_fullname for fk in foreign_keys}
        assert "portfolios.id" in fk_targets
        assert "stocks.id" in fk_targets

    def test_transaction_type_check_constraint(self) -> None:
        """Test that transaction_type has a check constraint for valid values."""
        # Look for check constraints
        check_constraints = [
            c
            for c in transaction_table.constraints
            if isinstance(c, sa.CheckConstraint)
        ]

        # Should have at least one check constraint for transaction_type
        assert len(check_constraints) >= 1

        # Verify the constraint checks for BUY/SELL
        found = False
        for constraint in check_constraints:
            sql_text = str(constraint.sqltext)
            if "transaction_type" in sql_text and (
                "BUY" in sql_text or "SELL" in sql_text
            ):
                found = True
                break
        assert found, "Missing check constraint for transaction_type"

    def test_numeric_column_precision(self) -> None:
        """Test that numeric columns have appropriate precision."""
        columns = {col.name: col for col in transaction_table.columns}

        # Quantity precision
        quantity_type = columns["quantity"].type
        assert isinstance(quantity_type, sa.Numeric)
        assert (
            quantity_type.precision is not None and quantity_type.precision >= 10
        )  # Support large share counts
        assert (
            quantity_type.scale is not None and quantity_type.scale >= 4
        )  # Support fractional shares

        # Price precision
        price_type = columns["price"].type
        assert isinstance(price_type, sa.Numeric)
        assert (
            price_type.precision is not None and price_type.precision >= 10
        )  # Support high-priced stocks
        assert (
            price_type.scale is not None and price_type.scale >= 4
        )  # Support precise pricing

        # Commission precision
        commission_type = columns["commission"].type
        assert isinstance(commission_type, sa.Numeric)
        assert commission_type.precision is not None and commission_type.precision >= 8
        assert commission_type.scale is not None and commission_type.scale >= 2

    def test_transaction_table_defaults(self) -> None:
        """Test that transaction table has correct default values."""
        columns = {col.name: col for col in transaction_table.columns}

        # Commission should default to 0
        assert columns["commission"].server_default is not None
        if hasattr(columns["commission"].server_default, "arg"):
            assert "0" in str(getattr(columns["commission"].server_default, "arg"))

        # Timestamps should have defaults
        assert columns["created_at"].server_default is not None
        assert columns["updated_at"].server_default is not None

    def test_transaction_table_metadata(self) -> None:
        """Test that transaction table uses the shared metadata instance."""
        assert transaction_table.metadata is metadata

    def test_transaction_table_can_be_created(self, temp_database: Engine) -> None:
        """Test that transaction table can be created in a database."""
        # Need to create referenced tables first
        from src.infrastructure.persistence.tables.portfolio_table import (
            portfolio_table,
        )
        from src.infrastructure.persistence.tables.stock_table import stock_table

        stock_table.create(temp_database)
        portfolio_table.create(temp_database)
        transaction_table.create(temp_database)

        # Verify it was created
        inspector = inspect(temp_database)
        assert "transactions" in inspector.get_table_names()

        # Verify column structure
        columns = inspector.get_columns("transactions")
        column_names = {col["name"] for col in columns}
        expected_columns = {
            "id",
            "portfolio_id",
            "stock_id",
            "transaction_type",
            "quantity",
            "price",
            "commission",
            "notes",
            "transaction_date",
            "created_at",
            "updated_at",
        }
        assert column_names == expected_columns
