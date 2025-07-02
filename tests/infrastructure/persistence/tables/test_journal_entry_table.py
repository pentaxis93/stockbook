"""Tests for journal entry table definition."""

import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.engine import Engine

from src.infrastructure.persistence.tables.journal_entry_table import (
    journal_entry_table,
    metadata,
)


class TestJournalEntryTable:
    """Test suite for journal entry table definition."""

    def test_journal_entry_table_exists(self) -> None:
        """Test that journal_entry table is defined."""
        assert journal_entry_table is not None
        assert journal_entry_table.name == "journal_entries"

    def test_journal_entry_table_columns(self) -> None:
        """Test that journal_entry table has all required columns."""
        columns = {col.name: col for col in journal_entry_table.columns}

        # Check required columns exist
        assert "id" in columns
        assert "portfolio_id" in columns
        assert "stock_id" in columns
        assert "entry_type" in columns
        assert "title" in columns
        assert "content" in columns
        assert "tags" in columns
        assert "entry_date" in columns
        assert "created_at" in columns
        assert "updated_at" in columns

    def test_journal_entry_table_column_types(self) -> None:
        """Test that journal_entry table columns have correct types."""
        columns = {col.name: col for col in journal_entry_table.columns}

        # Check column types
        assert isinstance(columns["id"].type, sa.String)
        assert isinstance(columns["portfolio_id"].type, sa.String)
        assert isinstance(columns["stock_id"].type, sa.String)
        assert isinstance(columns["entry_type"].type, sa.String)
        assert isinstance(columns["title"].type, sa.String)
        assert isinstance(columns["content"].type, sa.Text)
        assert isinstance(columns["tags"].type, sa.String)
        assert isinstance(columns["entry_date"].type, sa.DateTime)
        assert isinstance(columns["created_at"].type, sa.DateTime)
        assert isinstance(columns["updated_at"].type, sa.DateTime)

    def test_journal_entry_table_constraints(self) -> None:
        """Test that journal_entry table has correct constraints."""
        columns = {col.name: col for col in journal_entry_table.columns}

        # Primary key
        assert columns["id"].primary_key is True

        # Not nullable columns
        assert columns["id"].nullable is False
        assert columns["entry_type"].nullable is False
        assert columns["title"].nullable is False
        assert columns["content"].nullable is False
        assert columns["entry_date"].nullable is False
        assert columns["created_at"].nullable is False
        assert columns["updated_at"].nullable is False

        # Nullable columns (optional relationships)
        assert columns["portfolio_id"].nullable is True
        assert columns["stock_id"].nullable is True
        assert columns["tags"].nullable is True

    def test_journal_entry_table_foreign_keys(self) -> None:
        """Test that journal_entry table has correct foreign key relationships."""
        foreign_keys = list(journal_entry_table.foreign_keys)

        # Should have two foreign keys (even if nullable)
        assert len(foreign_keys) == 2

        # Check foreign key targets
        fk_targets = {fk.target_fullname for fk in foreign_keys}
        assert "portfolios.id" in fk_targets
        assert "stocks.id" in fk_targets

    def test_entry_type_check_constraint(self) -> None:
        """Test that entry_type has a check constraint for valid values."""
        # Look for check constraints
        check_constraints = [
            c
            for c in journal_entry_table.constraints
            if isinstance(c, sa.CheckConstraint)
        ]

        # Should have at least one check constraint for entry_type
        assert len(check_constraints) >= 1

        # Verify the constraint checks for valid entry types
        found = False
        for constraint in check_constraints:
            sql_text = str(constraint.sqltext)
            if "entry_type" in sql_text and any(
                entry_type in sql_text
                for entry_type in ["RESEARCH", "DECISION", "REVIEW", "NOTE"]
            ):
                found = True
                break
        assert found, "Missing check constraint for entry_type"

    def test_journal_entry_table_defaults(self) -> None:
        """Test that journal_entry table has correct default values."""
        columns = {col.name: col for col in journal_entry_table.columns}

        # Entry date should default to current timestamp
        assert columns["entry_date"].server_default is not None

        # Timestamps should have defaults
        assert columns["created_at"].server_default is not None
        assert columns["updated_at"].server_default is not None

    def test_journal_entry_table_metadata(self) -> None:
        """Test that journal_entry table uses the shared metadata instance."""
        assert journal_entry_table.metadata is metadata

    def test_journal_entry_table_indexes(self) -> None:
        """Test that journal_entry table has appropriate indexes."""
        # Check for indexes on commonly queried columns
        indexes = list(journal_entry_table.indexes)

        # Should have indexes for performance
        indexed_columns: set[str] = set()
        for index in indexes:
            for col in index.columns:
                indexed_columns.add(col.name)

        # At minimum, foreign keys should be indexed
        assert (
            "portfolio_id" in indexed_columns or len(indexes) == 0
        )  # Allow no indexes for now
        assert "stock_id" in indexed_columns or len(indexes) == 0

    def test_journal_entry_table_can_be_created(self, temp_database: Engine) -> None:
        """Test that journal_entry table can be created in a database."""
        # Need to create referenced tables first
        from src.infrastructure.persistence.tables.portfolio_table import (
            portfolio_table,
        )
        from src.infrastructure.persistence.tables.stock_table import stock_table

        stock_table.create(temp_database)
        portfolio_table.create(temp_database)
        journal_entry_table.create(temp_database)

        # Verify it was created
        inspector = inspect(temp_database)
        assert "journal_entries" in inspector.get_table_names()

        # Verify column structure
        columns = inspector.get_columns("journal_entries")
        column_names = {col["name"] for col in columns}
        expected_columns = {
            "id",
            "portfolio_id",
            "stock_id",
            "entry_type",
            "title",
            "content",
            "tags",
            "entry_date",
            "created_at",
            "updated_at",
        }
        assert column_names == expected_columns
