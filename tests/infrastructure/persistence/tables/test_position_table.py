"""Tests for position table definition."""

import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.engine import Engine

from src.infrastructure.persistence.tables.position_table import (
    metadata,
    position_table,
)


class TestPositionTable:
    """Test suite for position table definition."""

    def test_position_table_exists(self) -> None:
        """Test that position table is defined."""
        assert position_table is not None
        assert position_table.name == "positions"

    def test_position_table_columns(self) -> None:
        """Test that position table has all required columns."""
        columns = {col.name: col for col in position_table.columns}

        # Check required columns exist
        assert "id" in columns
        assert "portfolio_id" in columns
        assert "stock_id" in columns
        assert "quantity" in columns
        assert "average_cost" in columns
        assert "last_transaction_date" in columns
        assert "created_at" in columns
        assert "updated_at" in columns

    def test_position_table_column_types(self) -> None:
        """Test that position table columns have correct types."""
        columns = {col.name: col for col in position_table.columns}

        # Check column types
        assert isinstance(columns["id"].type, sa.String)
        assert isinstance(columns["portfolio_id"].type, sa.String)
        assert isinstance(columns["stock_id"].type, sa.String)
        assert isinstance(columns["quantity"].type, sa.Numeric)
        assert isinstance(columns["average_cost"].type, sa.Numeric)
        assert isinstance(columns["last_transaction_date"].type, sa.DateTime)
        assert isinstance(columns["created_at"].type, sa.DateTime)
        assert isinstance(columns["updated_at"].type, sa.DateTime)

    def test_position_table_constraints(self) -> None:
        """Test that position table has correct constraints."""
        columns = {col.name: col for col in position_table.columns}

        # Primary key
        assert columns["id"].primary_key is True

        # Not nullable columns
        assert columns["id"].nullable is False
        assert columns["portfolio_id"].nullable is False
        assert columns["stock_id"].nullable is False
        assert columns["quantity"].nullable is False
        assert columns["average_cost"].nullable is False
        assert columns["created_at"].nullable is False
        assert columns["updated_at"].nullable is False

        # Nullable columns
        assert columns["last_transaction_date"].nullable is True

    def test_position_table_foreign_keys(self) -> None:
        """Test that position table has correct foreign key relationships."""
        foreign_keys = list(position_table.foreign_keys)

        # Should have two foreign keys
        assert len(foreign_keys) == 2

        # Check foreign key targets
        fk_targets = {fk.target_fullname for fk in foreign_keys}
        assert "portfolios.id" in fk_targets
        assert "stocks.id" in fk_targets

    def test_position_table_unique_constraint(self) -> None:
        """Test that position table has unique constraint on
        portfolio_id + stock_id."""
        # Check for composite unique constraint
        constraints = [
            c for c in position_table.constraints if isinstance(c, sa.UniqueConstraint)
        ]
        assert len(constraints) >= 1

        # Find the constraint with both columns
        found = False
        for constraint in constraints:
            col_names = {col.name for col in constraint.columns}
            if col_names == {"portfolio_id", "stock_id"}:
                found = True
                break
        assert found, "Missing unique constraint on (portfolio_id, stock_id)"

    def test_numeric_column_precision(self) -> None:
        """Test that numeric columns have appropriate precision."""
        columns = {col.name: col for col in position_table.columns}

        # Quantity precision
        quantity_type = columns["quantity"].type
        assert isinstance(quantity_type, sa.Numeric)
        assert quantity_type.precision == 15
        assert quantity_type.scale == 4

        # Average cost precision
        avg_cost_type = columns["average_cost"].type
        assert isinstance(avg_cost_type, sa.Numeric)
        assert avg_cost_type.precision == 15
        assert avg_cost_type.scale == 4

    def test_position_table_defaults(self) -> None:
        """Test that position table has correct default values."""
        columns = {col.name: col for col in position_table.columns}

        # Quantity should default to 0
        assert columns["quantity"].server_default is not None

        # Average cost should default to 0
        assert columns["average_cost"].server_default is not None

        # Timestamps should have defaults
        assert columns["created_at"].server_default is not None
        assert columns["updated_at"].server_default is not None

        # last_transaction_date should not have a default
        assert columns["last_transaction_date"].server_default is None

    def test_position_table_metadata(self) -> None:
        """Test that position table uses the shared metadata instance."""
        assert position_table.metadata is metadata

    def test_position_table_can_be_created(
        self,
        temp_database: Engine,
    ) -> None:
        """Test that position table can be created in a database."""
        # Need to create referenced tables first
        from src.infrastructure.persistence.tables.portfolio_table import (
            portfolio_table,
        )
        from src.infrastructure.persistence.tables.stock_table import stock_table

        stock_table.create(temp_database)
        portfolio_table.create(temp_database)
        position_table.create(temp_database)

        # Verify it was created
        inspector = inspect(temp_database)
        assert "positions" in inspector.get_table_names()

        # Verify column structure
        columns = inspector.get_columns("positions")
        column_names = {col["name"] for col in columns}
        expected_columns = {
            "id",
            "portfolio_id",
            "stock_id",
            "quantity",
            "average_cost",
            "last_transaction_date",
            "created_at",
            "updated_at",
        }
        assert column_names == expected_columns

    def test_position_table_unique_constraint_name(self) -> None:
        """Test that the unique constraint has the correct name."""
        constraints = [
            c for c in position_table.constraints if isinstance(c, sa.UniqueConstraint)
        ]

        # Find the portfolio_id + stock_id constraint
        found_constraint = None
        for constraint in constraints:
            col_names = {col.name for col in constraint.columns}
            if col_names == {"portfolio_id", "stock_id"}:
                found_constraint = constraint
                break

        assert found_constraint is not None
        assert found_constraint.name == "uq_portfolio_stock_position"

    def test_position_table_different_from_portfolio_balance(self) -> None:
        """Test that position table differs from portfolio_balance table."""
        # Position table should have last_transaction_date column
        columns = {col.name: col for col in position_table.columns}
        assert "last_transaction_date" in columns

        # last_transaction_date should be nullable (key difference)
        assert columns["last_transaction_date"].nullable is True

        # Table name should be different
        assert position_table.name == "positions"
        assert position_table.name != "portfolio_balances"
