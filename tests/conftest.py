"""
Shared test configuration and fixtures for StockBook tests.

This file is automatically loaded by pytest and provides common test utilities
that can be used across all test files without explicit imports.
"""

import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Generator

import pytest

from config import config
from src.domain.entities import PortfolioEntity
from src.domain.value_objects import Notes, PortfolioName
from src.infrastructure.persistence.database_connection import DatabaseConnection
from src.infrastructure.persistence.unit_of_work import SqliteUnitOfWork

# Add the project root to Python path so we can import our modules
# This allows tests to import from project packages
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def test_db() -> Generator[Path, None, None]:
    """
    Create a temporary test database for each test.

    This fixture ensures each test runs with a fresh, isolated database,
    preventing tests from interfering with each other. The database is
    automatically cleaned up after each test completes.

    Yields:
        Path: Path to the temporary database file
    """
    # Create a temporary file for the test database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        test_db_path = Path(f.name)

    # Also update the config for consistency
    original_config_path = config.db_path
    config.db_path = test_db_path

    # Initialize the test database with the schema using clean architecture
    db_connection = DatabaseConnection(str(test_db_path))
    db_connection.initialize_schema()

    # Yield control back to the test
    yield test_db_path

    # Cleanup: This runs after the test completes
    # Restore the original database path
    config.db_path = original_config_path

    # Delete the temporary test database
    if test_db_path.exists():
        test_db_path.unlink()


@pytest.fixture
def sample_stock_data() -> Dict[str, Dict[str, str]]:
    """
    Provide sample stock data for testing.

    Returns a dictionary of stock information that can be used
    to create consistent test data across different tests.
    """
    return {
        "AAPL": {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "industry_group": "Technology",
            "grade": "A",
            "notes": "Strong fundamentals, market leader",
        },
        "MSFT": {
            "symbol": "MSFT",
            "name": "Microsoft Corporation",
            "industry_group": "Technology",
            "grade": "A",
            "notes": "Cloud growth, stable earnings",
        },
        "JPM": {
            "symbol": "JPM",
            "name": "JPMorgan Chase & Co.",
            "industry_group": "Financials",
            "grade": "B",
            "notes": "Leading bank, interest rate sensitive",
        },
    }


@pytest.fixture
def sample_portfolio(test_db: Path) -> Dict[str, Any]:
    """
    Create a sample portfolio with some test data.

    This fixture depends on test_db, ensuring we have a database
    before creating the portfolio. It's useful for tests that need
    a pre-populated portfolio to work with.

    Args:
        test_database: The test database fixture

    Returns:
        dict: Portfolio information including ID
    """
    # Create portfolio using clean architecture
    db_conn = DatabaseConnection(str(test_db))
    uow = SqliteUnitOfWork(db_conn)

    portfolio = PortfolioEntity(
        name=PortfolioName("Test Portfolio"),
        description=Notes("Test portfolio for testing"),
        is_active=True,
    )

    with uow:
        portfolio_id = uow.portfolios.create(portfolio)
        uow.commit()
        # Get the created portfolio for return
        saved_portfolio = uow.portfolios.get_by_id(portfolio_id)
        assert saved_portfolio is not None

    return {
        "id": saved_portfolio.id,
        "name": saved_portfolio.name.value,
        "description": saved_portfolio.description.value,
        "is_active": saved_portfolio.is_active,
    }


# Test helper functions that can be imported by test files
def assert_datetime_recent(dt: datetime | str, seconds: int = 5) -> None:
    """
    Assert that a datetime is recent (within the specified seconds).

    Useful for testing timestamp fields where we can't predict
    the exact time but want to ensure it's freshly created.

    Args:
        dt: datetime object or string to check
        seconds: Maximum age in seconds (default: 5)
    """
    if isinstance(dt, str):
        # Parse string timestamps without timezone conversion for SQLite consistency
        dt = datetime.fromisoformat(dt.replace("Z", ""))

    # Use UTC time for consistency since SQLite CURRENT_TIMESTAMP is UTC
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    time_diff = abs((now - dt).total_seconds())
    assert (
        time_diff < seconds
    ), f"Datetime {dt} is not recent (difference: {time_diff} seconds, limit: {seconds})"


def count_db_rows(table_name: str, test_db_path: Path) -> int:
    """
    Count rows in a database table.

    Useful for verifying that records were created or deleted
    as expected during tests.

    Args:
        table_name: Name of the table to count
        test_db_path: Path to the test database

    Returns:
        int: Number of rows in the table
    """
    conn = sqlite3.connect(test_db_path)
    cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    conn.close()
    return count
