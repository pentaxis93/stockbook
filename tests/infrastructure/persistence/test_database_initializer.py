"""Tests for database initialization functionality."""

import os
import tempfile
from typing import Generator
from unittest.mock import Mock, patch

import pytest
import sqlalchemy as sa
from sqlalchemy import inspect

from src.infrastructure.persistence.database_initializer import initialize_database


class TestDatabaseInitializer:
    """Test suite for database initialization."""

    @pytest.fixture
    def temp_db_path(self) -> Generator[str, None, None]:
        """Create a temporary database file path."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp_path = tmp.name

        yield tmp_path

        # Cleanup
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    @pytest.fixture
    def mock_metadata(self) -> Mock:
        """Create a mock metadata object."""
        metadata = Mock(spec=sa.MetaData)
        metadata.tables = {}
        return metadata

    def test_initialize_database_creates_new_database(self, temp_db_path: str) -> None:
        """Test that initialize_database creates a new database with all tables."""
        # Initialize the database
        initialize_database(f"sqlite:///{temp_db_path}")

        # Verify database file was created
        assert os.path.exists(temp_db_path)

        # Verify tables were created
        engine = sa.create_engine(f"sqlite:///{temp_db_path}")
        inspector = inspect(engine)
        table_names = inspector.get_table_names()

        # Check that all expected tables exist
        expected_tables = {
            "stocks",
            "portfolios",
            "targets",
            "transactions",
            "portfolio_balances",
            "journal_entries",
        }
        assert set(table_names) == expected_tables

    def test_initialize_database_is_idempotent(self, temp_db_path: str) -> None:
        """Test that initialize_database can be called multiple times safely."""
        db_url = f"sqlite:///{temp_db_path}"

        # Initialize twice
        initialize_database(db_url)
        initialize_database(db_url)

        # Verify tables still exist and weren't duplicated
        engine = sa.create_engine(db_url)
        inspector = inspect(engine)
        table_names = inspector.get_table_names()

        # Should have the same tables, not duplicates
        expected_tables = {
            "stocks",
            "portfolios",
            "targets",
            "transactions",
            "portfolio_balances",
            "journal_entries",
        }
        assert set(table_names) == expected_tables

    def test_initialize_database_with_invalid_url(self) -> None:
        """Test that initialize_database handles invalid database URLs gracefully."""
        with pytest.raises(Exception):
            initialize_database("invalid://url")

    def test_initialize_database_with_existing_data(self, temp_db_path: str) -> None:
        """Test that initialize_database preserves existing data."""
        # First initialize the database
        initialize_database(temp_db_path)

        # Insert some test data
        engine = sa.create_engine(f"sqlite:///{temp_db_path}")
        with engine.begin() as conn:  # type: ignore[attr-defined]
            conn.execute(  # type: ignore[attr-defined]
                sa.text("INSERT INTO stocks (id, symbol) VALUES (:id, :symbol)"),
                {"id": "test-id", "symbol": "AAPL"},
            )

        # Initialize again
        initialize_database(temp_db_path)

        # Verify data is still there
        with engine.connect() as conn:  # type: ignore[attr-defined]
            result = conn.execute(  # type: ignore[attr-defined]
                sa.text("SELECT symbol FROM stocks WHERE id = :id"), {"id": "test-id"}
            ).fetchone()
            assert result is not None
            assert result[0] == "AAPL"

    @patch("src.infrastructure.persistence.database_initializer.logger")
    def test_initialize_database_logs_success(
        self, mock_logger: Mock, temp_db_path: str
    ) -> None:
        """Test that successful initialization is logged."""
        initialize_database(f"sqlite:///{temp_db_path}")

        # Should log initialization start and completion
        assert mock_logger.info.call_count >= 2
        calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any("initializing" in call.lower() for call in calls)
        assert any("initialized" in call.lower() for call in calls)

    @patch("src.infrastructure.persistence.database_initializer.logger")
    def test_initialize_database_logs_errors(self, mock_logger: Mock) -> None:
        """Test that initialization errors are logged."""
        with pytest.raises(Exception):
            initialize_database("invalid://url")

        # Should log the error
        mock_logger.error.assert_called_once()
        error_message = mock_logger.error.call_args[0][0]
        assert "failed" in error_message.lower()

    def test_initialize_database_with_file_url(self, temp_db_path: str) -> None:
        """Test initialization with a file path instead of URL."""
        # Should convert file path to SQLite URL
        initialize_database(temp_db_path)

        # Verify database was created
        assert os.path.exists(temp_db_path)

        # Verify tables were created
        engine = sa.create_engine(f"sqlite:///{temp_db_path}")
        inspector = inspect(engine)
        assert len(inspector.get_table_names()) > 0
