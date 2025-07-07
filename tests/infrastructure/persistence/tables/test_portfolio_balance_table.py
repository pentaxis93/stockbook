"""Tests for portfolio balance table definition."""

import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.engine import Engine

from src.infrastructure.persistence.tables.portfolio_balance_table import (
    metadata,
    portfolio_balance_table,
)


class TestPortfolioBalanceTable:
    """Test suite for portfolio balance table definition."""

    def test_portfolio_balance_table_exists(self) -> None:
        """Test that portfolio_balance table is defined."""
        assert portfolio_balance_table is not None
        assert portfolio_balance_table.name == "portfolio_balances"

    def test_portfolio_balance_table_columns(self) -> None:
        """Test that portfolio_balance table has all required columns."""
        columns = {col.name: col for col in portfolio_balance_table.columns}

        # Check required columns exist
        assert "id" in columns
        assert "portfolio_id" in columns
        assert "stock_id" in columns
        assert "quantity" in columns
        assert "average_cost" in columns
        assert "created_at" in columns
        assert "updated_at" in columns

    def test_portfolio_balance_table_column_types(self) -> None:
        """Test that portfolio_balance table columns have correct types."""
        columns = {col.name: col for col in portfolio_balance_table.columns}

        # Check column types
        assert isinstance(columns["id"].type, sa.String)
        assert isinstance(columns["portfolio_id"].type, sa.String)
        assert isinstance(columns["stock_id"].type, sa.String)
        assert isinstance(columns["quantity"].type, sa.Numeric)
        assert isinstance(columns["average_cost"].type, sa.Numeric)
        assert isinstance(columns["created_at"].type, sa.DateTime)
        assert isinstance(columns["updated_at"].type, sa.DateTime)

    def test_portfolio_balance_table_constraints(self) -> None:
        """Test that portfolio_balance table has correct constraints."""
        columns = {col.name: col for col in portfolio_balance_table.columns}

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

    def test_portfolio_balance_table_foreign_keys(self) -> None:
        """Test that portfolio_balance table has correct foreign key relationships."""
        foreign_keys = list(portfolio_balance_table.foreign_keys)

        # Should have two foreign keys
        assert len(foreign_keys) == 2

        # Check foreign key targets
        fk_targets = {fk.target_fullname for fk in foreign_keys}
        assert "portfolios.id" in fk_targets
        assert "stocks.id" in fk_targets

    def test_portfolio_balance_table_unique_constraint(self) -> None:
        """Test that portfolio_balance table has unique constraint on
        portfolio_id + stock_id."""
        # Check for composite unique constraint
        constraints = [
            c
            for c in portfolio_balance_table.constraints
            if isinstance(c, sa.UniqueConstraint)
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
        columns = {col.name: col for col in portfolio_balance_table.columns}

        # Quantity precision
        quantity_type = columns["quantity"].type
        assert isinstance(quantity_type, sa.Numeric)
        assert quantity_type.precision is not None
        assert quantity_type.precision >= 10
        assert quantity_type.scale is not None
        assert quantity_type.scale >= 4

        # Average cost precision
        avg_cost_type = columns["average_cost"].type
        assert isinstance(avg_cost_type, sa.Numeric)
        assert avg_cost_type.precision is not None
        assert avg_cost_type.precision >= 10
        assert avg_cost_type.scale is not None
        assert avg_cost_type.scale >= 4

    def test_portfolio_balance_table_defaults(self) -> None:
        """Test that portfolio_balance table has correct default values."""
        columns = {col.name: col for col in portfolio_balance_table.columns}

        # Quantity should default to 0
        assert columns["quantity"].server_default is not None

        # Average cost should default to 0
        assert columns["average_cost"].server_default is not None

        # Timestamps should have defaults
        assert columns["created_at"].server_default is not None
        assert columns["updated_at"].server_default is not None

    def test_portfolio_balance_table_metadata(self) -> None:
        """Test that portfolio_balance table uses the shared metadata instance."""
        assert portfolio_balance_table.metadata is metadata

    def test_portfolio_balance_table_can_be_created(
        self,
        temp_database: Engine,
    ) -> None:
        """Test that portfolio_balance table can be created in a database."""
        # Need to create referenced tables first
        from src.infrastructure.persistence.tables.portfolio_table import (
            portfolio_table,
        )
        from src.infrastructure.persistence.tables.stock_table import stock_table

        stock_table.create(temp_database)
        portfolio_table.create(temp_database)
        portfolio_balance_table.create(temp_database)

        # Verify it was created
        inspector = inspect(temp_database)
        assert "portfolio_balances" in inspector.get_table_names()

        # Verify column structure
        columns = inspector.get_columns("portfolio_balances")
        column_names = {col["name"] for col in columns}
        expected_columns = {
            "id",
            "portfolio_id",
            "stock_id",
            "quantity",
            "average_cost",
            "created_at",
            "updated_at",
        }
        assert column_names == expected_columns
