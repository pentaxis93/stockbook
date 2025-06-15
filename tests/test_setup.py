"""
Test file to verify pytest setup is working correctly.

This file contains basic tests that verify:
1. Pytest can discover and run tests
2. Fixtures are working properly
3. Database operations can be tested in isolation
"""

import pytest
from pathlib import Path


def test_pytest_is_working():
    """Verify that pytest can discover and run a simple test."""
    assert True, "If this fails, pytest isn't working at all!"


def test_imports_work():
    """Verify we can import project modules."""
    # These imports should work thanks to the path setup in conftest.py
    from utils.database import StockDB, PortfolioDB

    # If we get here without ImportError, our imports are configured correctly
    assert StockDB is not None
    assert PortfolioDB is not None


def test_test_database_fixture(test_db):
    """Verify the test database fixture creates a working database."""
    # The test_db fixture should provide a Path object
    assert isinstance(test_db, Path)

    # The database file should exist
    assert test_db.exists(), "Test database file was not created"

    # We should be able to import and use database utilities
    from utils.database import get_db_connection

    # Verify we can connect to the test database
    with get_db_connection() as conn:
        # Check that our schema was created by looking for the stock table
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='stock'"
        )
        result = cursor.fetchone()
        assert result is not None, "Stock table was not created in test database"


def test_sample_data_fixtures(sample_stock_data, sample_portfolio):
    """Verify our sample data fixtures are working."""
    # Check sample_stock_data structure
    assert 'AAPL' in sample_stock_data
    assert sample_stock_data['AAPL']['symbol'] == 'AAPL'
    assert sample_stock_data['AAPL']['name'] == 'Apple Inc.'

    # Check sample_portfolio structure
    assert 'id' in sample_portfolio
    assert sample_portfolio['name'] == 'Test Portfolio'
    assert sample_portfolio['max_positions'] == 10


@pytest.mark.slow
def test_marker_functionality():
    """
    Verify that pytest markers are working.

    This test is marked as 'slow' to demonstrate marker functionality.
    Run with 'pytest -m "not slow"' to skip this test.
    """
    import time

    # Simulate a slow operation
    start_time = time.time()
    time.sleep(0.1)  # Sleep for 100ms
    elapsed = time.time() - start_time

    assert elapsed >= 0.1, "Sleep didn't last long enough"
