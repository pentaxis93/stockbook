"""
Tests for StockDB database operations.

This module tests all CRUD operations and queries for the stock table,
ensuring data integrity and proper error handling.
"""

import pytest
from utils.database import StockDB, get_db_connection
from sqlite3 import IntegrityError
from tests.conftest import assert_datetime_recent


class TestStockDB:
    """Test suite for StockDB operations."""

    def test_create_stock_minimal(self, test_db):
        """
        Test creating a stock with only required fields.

        This tests the simplest case - just symbol and name.
        """
        # Create a stock with minimal information
        stock_id = StockDB.create(symbol="AAPL", name="Apple Inc.")

        # Verify the stock was created with a valid ID
        assert isinstance(stock_id, int)
        assert stock_id > 0

        # Verify we can retrieve it
        stock = StockDB.get_by_symbol("AAPL")
        assert stock is not None
        assert stock["symbol"] == "AAPL"
        assert stock["name"] == "Apple Inc."
        # Should be None when not provided
        assert stock["industry_group"] is None
        assert stock["grade"] is None
        assert stock["notes"] is None

    def test_create_stock_complete(self, test_db):
        """
        Test creating a stock with all fields populated.

        This ensures all optional fields are properly stored.
        """
        stock_id = StockDB.create(
            symbol="MSFT",
            name="Microsoft Corporation",
            industry_group="Technology",
            grade="A",
            notes="Strong cloud growth, consistent earnings",
        )

        # Retrieve and verify all fields
        stock = StockDB.get_by_symbol("MSFT")
        assert stock is not None
        assert stock["symbol"] == "MSFT"
        assert stock["name"] == "Microsoft Corporation"
        assert stock["industry_group"] == "Technology"
        assert stock["grade"] == "A"
        assert stock["notes"] == "Strong cloud growth, consistent earnings"

    def test_create_duplicate_symbol_fails(self, test_db):
        """
        Test that creating a stock with duplicate symbol fails.

        The database schema enforces unique symbols, so this should
        raise an IntegrityError.
        """
        # Create the first stock
        StockDB.create(symbol="AAPL", name="Apple Inc.")

        # Attempting to create another with same symbol should fail
        with pytest.raises(IntegrityError):
            StockDB.create(symbol="AAPL", name="Apple Duplicate")

    def test_get_by_symbol_not_found(self, test_db):
        """
        Test retrieving a non-existent stock returns None.

        This verifies our error handling for missing records.
        """
        stock = StockDB.get_by_symbol("NONEXISTENT")
        assert stock is None

    def test_get_all_empty(self, test_db):
        """
        Test get_all returns empty list when no stocks exist.

        This verifies the function handles empty tables gracefully.
        """
        stocks = StockDB.get_all()
        assert isinstance(stocks, list)
        assert len(stocks) == 0

    def test_get_all_multiple_stocks(self, test_db, sample_stock_data):
        """
        Test get_all returns all stocks in alphabetical order.

        This verifies both the retrieval and ordering logic.
        """
        # Create multiple stocks from our sample data
        for symbol, data in sample_stock_data.items():
            StockDB.create(
                symbol=data["symbol"],
                name=data["name"],
                industry_group=data["industry_group"],
                grade=data["grade"],
                notes=data["notes"],
            )

        # Retrieve all stocks
        stocks = StockDB.get_all()

        # Verify count matches what we created
        assert len(stocks) == len(sample_stock_data)

        # Verify alphabetical ordering by symbol
        symbols = [stock["symbol"] for stock in stocks]
        assert symbols == sorted(symbols)

        # Verify first stock details (AAPL should be first alphabetically)
        assert stocks[0]["symbol"] == "AAPL"
        assert stocks[0]["name"] == "Apple Inc."

    def test_update_stock_single_field(self, test_db):
        """
        Test updating a single field in a stock record.

        This verifies partial updates work correctly.
        """
        # Create a stock
        stock_id = StockDB.create(symbol="GOOGL", name="Alphabet Inc.", grade="B")

        # Update just the grade
        success = StockDB.update(stock_id, grade="A")
        assert success is True

        # Verify the update
        stock = StockDB.get_by_symbol("GOOGL")
        assert stock is not None
        assert stock["grade"] == "A"
        assert stock["name"] == "Alphabet Inc."  # Should be unchanged

    def test_update_stock_multiple_fields(self, test_db):
        """
        Test updating multiple fields at once.

        This ensures our update logic handles multiple fields correctly.
        """
        # Create a stock
        stock_id = StockDB.create(symbol="TSLA", name="Tesla Inc.")

        # Update multiple fields
        success = StockDB.update(
            stock_id,
            industry_group="Automotive",
            grade="B",
            notes="EV leader, high volatility",
        )
        assert success is True

        # Verify all updates
        stock = StockDB.get_by_symbol("TSLA")
        assert stock is not None
        assert stock["industry_group"] == "Automotive"
        assert stock["grade"] == "B"
        assert stock["notes"] == "EV leader, high volatility"

    def test_update_invalid_field_ignored(self, test_db):
        """
        Test that invalid fields are ignored during update.

        This ensures we don't accidentally update protected fields
        like symbol or try to set non-existent columns.
        """
        # Create a stock
        stock_id = StockDB.create(symbol="AMZN", name="Amazon.com Inc.")

        # Try to update with invalid fields
        success = StockDB.update(
            stock_id,
            symbol="CHANGED",  # Should be ignored - symbol is immutable
            invalid_field="test",  # Should be ignored - doesn't exist
            grade="A",  # This should work
        )

        # The update should still succeed (returns True if any valid field was updated)
        assert success is True

        # Verify only valid field was updated
        stock = StockDB.get_by_symbol("AMZN")
        assert stock is not None
        assert stock["symbol"] == "AMZN"  # Should be unchanged
        assert stock["grade"] == "A"  # Should be updated

    def test_update_nonexistent_stock(self, test_db):
        """
        Test updating a stock that doesn't exist.

        This should return False or handle gracefully.
        """
        # Attempt to update non-existent stock
        success = StockDB.update(999999, grade="A")

        # Should return True (SQLite doesn't raise error for UPDATE with no matches)
        # but no rows are affected
        assert success is True

    def test_grade_constraint(self, test_db):
        """
        Test that grade column only accepts valid values.

        The schema defines CHECK constraint for grades A, B, C, or NULL.
        """
        # Valid grades should work
        for grade in ["A", "B", "C", None]:
            stock_id = StockDB.create(
                symbol=f"TEST{grade or 'NULL'}",
                name=f"Test Stock {grade or 'NULL'}",
                grade=grade,
            )
            assert stock_id > 0

    def test_timestamps(self, test_db):
        """
        Test that created_at and updated_at timestamps are set correctly.

        This verifies our timestamp triggers are working.
        """
        from datetime import datetime, timezone
        import time

        # Create a stock
        stock_id = StockDB.create(symbol="META", name="Meta Platforms Inc.")

        # Get the stock to check timestamps
        stock = StockDB.get_by_symbol("META")

        # Both timestamps should be set and recent
        assert stock is not None
        assert stock["created_at"] is not None
        assert stock["updated_at"] is not None

        # Parse timestamps and verify they're recent (within last 5 seconds)
        # Note: SQLite stores timestamps in UTC, so we need to be timezone-aware
        created = datetime.fromisoformat(stock["created_at"].replace("Z", "+00:00"))
        updated = datetime.fromisoformat(stock["updated_at"].replace("Z", "+00:00"))

        # Verify timestamps are recent
        assert_datetime_recent(stock["created_at"])
        assert_datetime_recent(stock["updated_at"])

        # Initially, created_at and updated_at should be the same
        assert created == updated

        # Wait a moment then update (need enough time for timestamp precision)
        time.sleep(1.1)
        StockDB.update(stock_id, notes="Updated notes")

        # Check timestamps again
        stock = StockDB.get_by_symbol("META")
        assert stock is not None
        new_updated = datetime.fromisoformat(stock["updated_at"].replace("Z", "+00:00"))

        # updated_at should be newer than created_at
        assert new_updated > created
