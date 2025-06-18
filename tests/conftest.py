"""
Shared test configuration and fixtures for StockBook tests.

This file is automatically loaded by pytest and provides common test utilities
that can be used across all test files without explicit imports.
"""

import sqlite3
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from config import config
from infrastructure.persistence.database_connection import DatabaseConnection

# Add the project root to Python path so we can import our modules
# This allows tests to import from 'utils' and other project packages
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def test_db():
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
def sample_stock_data():
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
def sample_portfolio(test_db):
    """
    Create a sample portfolio with some test data.

    This fixture depends on test_db, ensuring we have a database
    before creating the portfolio. It's useful for tests that need
    a pre-populated portfolio to work with.

    Args:
        test_db: The test database fixture

    Returns:
        dict: Portfolio information including ID
    """
    from domain.entities import PortfolioEntity
    from infrastructure.persistence.database_connection import \
        DatabaseConnection
    from infrastructure.persistence.unit_of_work import SqliteUnitOfWork
    from infrastructure.repositories.sqlite_portfolio_repository import \
        SqlitePortfolioRepository

    # Create portfolio using clean architecture
    db_connection = DatabaseConnection(str(test_db))
    portfolio_repo = SqlitePortfolioRepository(db_connection)
    uow = SqliteUnitOfWork(db_connection)

    portfolio = PortfolioEntity(
        name="Test Portfolio", description="Test portfolio for testing", is_active=True
    )

    with uow:
        uow.portfolio_repository = portfolio_repo
        saved_portfolio = uow.portfolio_repository.add(portfolio)
        uow.commit()

    return {
        "id": saved_portfolio.id,
        "name": saved_portfolio.name,
        "description": saved_portfolio.description,
        "is_active": saved_portfolio.is_active,
    }


# Test helper functions that can be imported by test files
def assert_datetime_recent(dt, seconds=5):
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
    from datetime import timezone

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    time_diff = abs((now - dt).total_seconds())
    assert (
        time_diff < seconds
    ), f"Datetime {dt} is not recent (difference: {time_diff} seconds, limit: {seconds})"


def count_db_rows(table_name, test_db_path):
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
