"""Tests for portfolio table definition."""

import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.engine import Engine

from src.infrastructure.persistence.tables.portfolio_table import (
    metadata,
    portfolio_table,
)


class TestPortfolioTable:
    """Test suite for portfolio table definition."""

    def test_portfolio_table_exists(self) -> None:
        """Test that portfolio table is defined."""
        assert portfolio_table is not None
        assert portfolio_table.name == "portfolios"

    def test_portfolio_table_columns(self) -> None:
        """Test that portfolio table has all required columns."""
        columns = {col.name: col for col in portfolio_table.columns}

        # Check required columns exist
        assert "id" in columns
        assert "name" in columns
        assert "description" in columns
        assert "currency" in columns
        assert "created_at" in columns
        assert "updated_at" in columns

    def test_portfolio_table_column_types(self) -> None:
        """Test that portfolio table columns have correct types."""
        columns = {col.name: col for col in portfolio_table.columns}

        # Check column types
        assert isinstance(columns["id"].type, sa.String)
        assert isinstance(columns["name"].type, sa.String)
        assert isinstance(columns["description"].type, sa.String)
        assert isinstance(columns["currency"].type, sa.String)
        assert isinstance(columns["created_at"].type, sa.DateTime)
        assert isinstance(columns["updated_at"].type, sa.DateTime)

    def test_portfolio_table_constraints(self) -> None:
        """Test that portfolio table has correct constraints."""
        columns = {col.name: col for col in portfolio_table.columns}

        # Primary key
        assert columns["id"].primary_key is True

        # Not nullable columns
        assert columns["id"].nullable is False
        assert columns["name"].nullable is False
        assert columns["currency"].nullable is False
        assert columns["created_at"].nullable is False
        assert columns["updated_at"].nullable is False

        # Nullable columns
        assert columns["description"].nullable is True

    def test_portfolio_table_unique_constraints(self) -> None:
        """Test that portfolio table has unique constraint on name."""
        columns = {col.name: col for col in portfolio_table.columns}
        assert columns["name"].unique is True

    def test_portfolio_table_defaults(self) -> None:
        """Test that portfolio table has correct default values."""
        columns = {col.name: col for col in portfolio_table.columns}

        # Default currency should be USD
        assert columns["currency"].server_default is not None
        assert "USD" in str(columns["currency"].server_default.arg)

        # Timestamps should have defaults
        assert columns["created_at"].server_default is not None
        assert columns["updated_at"].server_default is not None

    def test_portfolio_table_metadata(self) -> None:
        """Test that portfolio table uses the shared metadata instance."""
        assert portfolio_table.metadata is metadata

    def test_portfolio_table_can_be_created(self, temp_database: Engine) -> None:
        """Test that portfolio table can be created in a database."""
        # Create the table
        portfolio_table.create(temp_database)

        # Verify it was created
        inspector = inspect(temp_database)
        assert "portfolios" in inspector.get_table_names()

        # Verify column structure
        columns = inspector.get_columns("portfolios")
        column_names = {col["name"] for col in columns}
        expected_columns = {
            "id",
            "name",
            "description",
            "currency",
            "created_at",
            "updated_at",
        }
        assert column_names == expected_columns
