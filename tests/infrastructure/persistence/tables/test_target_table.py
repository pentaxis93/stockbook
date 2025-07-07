"""Tests for target table definition."""

import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.engine import Engine

from src.infrastructure.persistence.tables.target_table import metadata, target_table


class TestTargetTable:
    """Test suite for target table definition."""

    def test_target_table_exists(self) -> None:
        """Test that target table is defined."""
        assert target_table is not None
        assert target_table.name == "targets"

    def test_target_table_columns(self) -> None:
        """Test that target table has all required columns."""
        columns = {col.name: col for col in target_table.columns}

        # Check required columns exist
        assert "id" in columns
        assert "portfolio_id" in columns
        assert "stock_id" in columns
        assert "target_percentage" in columns
        assert "created_at" in columns
        assert "updated_at" in columns

    def test_target_table_column_types(self) -> None:
        """Test that target table columns have correct types."""
        columns = {col.name: col for col in target_table.columns}

        # Check column types
        assert isinstance(columns["id"].type, sa.String)
        assert isinstance(columns["portfolio_id"].type, sa.String)
        assert isinstance(columns["stock_id"].type, sa.String)
        assert isinstance(columns["target_percentage"].type, sa.Numeric)
        assert isinstance(columns["created_at"].type, sa.DateTime)
        assert isinstance(columns["updated_at"].type, sa.DateTime)

    def test_target_table_constraints(self) -> None:
        """Test that target table has correct constraints."""
        columns = {col.name: col for col in target_table.columns}

        # Primary key
        assert columns["id"].primary_key is True

        # Not nullable columns
        assert columns["id"].nullable is False
        assert columns["portfolio_id"].nullable is False
        assert columns["stock_id"].nullable is False
        assert columns["target_percentage"].nullable is False
        assert columns["created_at"].nullable is False
        assert columns["updated_at"].nullable is False

    def test_target_table_foreign_keys(self) -> None:
        """Test that target table has correct foreign key relationships."""
        foreign_keys = list(target_table.foreign_keys)

        # Should have two foreign keys
        assert len(foreign_keys) == 2

        # Check foreign key targets
        fk_targets = {fk.target_fullname for fk in foreign_keys}
        assert "portfolios.id" in fk_targets
        assert "stocks.id" in fk_targets

    def test_target_table_unique_constraint(self) -> None:
        """Test that target table has unique constraint on portfolio_id + stock_id."""
        # Check for composite unique constraint
        constraints = [
            c for c in target_table.constraints if isinstance(c, sa.UniqueConstraint)
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

    def test_target_percentage_precision(self) -> None:
        """Test that target_percentage has correct precision for percentages."""
        columns = {col.name: col for col in target_table.columns}
        percentage_type = columns["target_percentage"].type

        # Should be Numeric with precision for percentages (e.g., 99.99%)
        assert isinstance(percentage_type, sa.Numeric)
        assert percentage_type.precision is not None
        assert percentage_type.precision >= 5
        assert percentage_type.scale is not None
        assert percentage_type.scale >= 2

    def test_target_table_defaults(self) -> None:
        """Test that target table has correct default values."""
        columns = {col.name: col for col in target_table.columns}

        # Timestamps should have defaults
        assert columns["created_at"].server_default is not None
        assert columns["updated_at"].server_default is not None

    def test_target_table_metadata(self) -> None:
        """Test that target table uses the shared metadata instance."""
        assert target_table.metadata is metadata

    def test_target_table_can_be_created(self, temp_database: Engine) -> None:
        """Test that target table can be created in a database."""
        # Need to create referenced tables first
        from src.infrastructure.persistence.tables.portfolio_table import (
            portfolio_table,
        )
        from src.infrastructure.persistence.tables.stock_table import stock_table

        stock_table.create(temp_database)
        portfolio_table.create(temp_database)
        target_table.create(temp_database)

        # Verify it was created
        inspector = inspect(temp_database)
        assert "targets" in inspector.get_table_names()

        # Verify column structure
        columns = inspector.get_columns("targets")
        column_names = {col["name"] for col in columns}
        expected_columns = {
            "id",
            "portfolio_id",
            "stock_id",
            "target_percentage",
            "created_at",
            "updated_at",
        }
        assert column_names == expected_columns
