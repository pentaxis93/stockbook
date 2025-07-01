"""
Tests for infrastructure test fixtures.

This module tests that all fixtures work correctly and provide
the expected functionality for infrastructure testing.
"""

import sqlite3
from typing import List, cast
from unittest.mock import Mock

import pytest

from src.domain.entities import StockEntity
from src.domain.repositories.interfaces import (
    IStockBookUnitOfWork,
    IStockRepository,
)
from src.domain.value_objects import StockSymbol

from .infrastructure import (
    StockEntityBuilder,
    db_transaction,
    seed_test_portfolio,
    seed_test_stocks,
)


class TestInMemoryDatabaseFixture:
    """Test the in-memory SQLite database fixture."""

    def test_database_creates_schema(self, in_memory_db: sqlite3.Connection) -> None:
        """Should create all required tables."""
        cursor = in_memory_db.cursor()

        # Check stocks table exists
        _ = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='stocks'"
        )
        assert cursor.fetchone() is not None

        # Check portfolios table exists
        _ = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='portfolios'"
        )
        assert cursor.fetchone() is not None

        # Check transactions table exists
        _ = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'"
        )
        assert cursor.fetchone() is not None

    def test_database_enforces_foreign_keys(
        self, in_memory_db: sqlite3.Connection
    ) -> None:
        """Should enforce foreign key constraints."""
        with pytest.raises(sqlite3.IntegrityError):
            _ = in_memory_db.execute(
                """
                INSERT INTO transactions (id, portfolio_id, stock_id, transaction_type,
                                        quantity, price, transaction_date)
                VALUES ('tx-1', 'invalid-portfolio', 'invalid-stock', 'BUY', 100, 150.00, '2024-01-01')
                """
            )

    def test_database_is_isolated_between_tests(
        self, in_memory_db: sqlite3.Connection
    ) -> None:
        """Each test should get a fresh database."""
        # Insert a stock
        _ = in_memory_db.execute(
            """
            INSERT INTO stocks (id, symbol, company_name)
            VALUES ('test-1', 'TEST', 'Test Company')
            """
        )
        in_memory_db.commit()

        # Verify it exists
        cursor = in_memory_db.cursor()
        _ = cursor.execute("SELECT COUNT(*) FROM stocks")
        assert cursor.fetchone()[0] == 1


class TestTransactionRollbackFixture:
    """Test the transaction rollback fixture."""

    def test_rollback_prevents_data_persistence(
        self, transaction_rollback: sqlite3.Connection
    ) -> None:
        """Should rollback all changes after test."""
        conn = transaction_rollback

        # Insert data within the test
        _ = conn.execute(
            """
            INSERT INTO stocks (id, symbol, company_name)
            VALUES ('rollback-test', 'ROLL', 'Rollback Test')
            """
        )

        # Verify it exists during the test
        cursor = conn.cursor()
        _ = cursor.execute("SELECT COUNT(*) FROM stocks WHERE id = 'rollback-test'")
        assert cursor.fetchone()[0] == 1

        # Note: After the test, the fixture will rollback this insert

    def test_nested_transactions_work(
        self, transaction_rollback: sqlite3.Connection
    ) -> None:
        """Should support nested transaction savepoints."""
        conn = transaction_rollback

        # Create a savepoint
        _ = conn.execute("SAVEPOINT nested_test")

        # Insert data
        _ = conn.execute(
            """
            INSERT INTO stocks (id, symbol, company_name)
            VALUES ('nested-1', 'NEST1', 'Nested Test 1')
            """
        )

        # Rollback to savepoint
        _ = conn.execute("ROLLBACK TO SAVEPOINT nested_test")

        # Verify the insert was rolled back
        cursor = conn.cursor()
        _ = cursor.execute("SELECT COUNT(*) FROM stocks WHERE id = 'nested-1'")
        assert cursor.fetchone()[0] == 0


class TestMockRepositoryFixtures:
    """Test all mock repository fixtures."""

    def test_mock_stock_repository(self, mock_stock_repository: Mock) -> None:
        """Should provide properly configured mock stock repository."""
        mock = cast(IStockRepository, mock_stock_repository)

        # Test default return values
        assert mock.create(Mock(spec=StockEntity)) == "stock-123"
        assert mock.get_by_id("any-id") is None
        assert mock.get_all() == []
        assert mock.update("id", Mock()) is True
        assert mock.exists_by_symbol(StockSymbol("TEST")) is False

        # Verify it has correct interface
        assert hasattr(mock, "get_by_symbol")
        assert hasattr(mock, "search_stocks")

    def test_mock_unit_of_work(self, mock_unit_of_work: Mock) -> None:
        """Should provide properly configured mock unit of work."""
        uow = cast(IStockBookUnitOfWork, mock_unit_of_work)

        # Test repository access
        assert hasattr(uow, "stocks")
        assert hasattr(uow, "portfolios")
        assert hasattr(uow, "transactions")

        # Test context manager
        with uow as context:
            assert context is uow

        # Test transaction methods
        uow.commit()
        uow.rollback()

        # Verify methods were called
        commit_mock = cast(Mock, uow.commit)
        rollback_mock = cast(Mock, uow.rollback)
        assert commit_mock.call_count == 1
        assert rollback_mock.call_count == 1

    def test_mock_repositories_can_be_configured(
        self, mock_stock_repository: Mock
    ) -> None:
        """Should allow configuring mock behavior."""
        # Configure custom behavior
        test_stock = StockEntityBuilder.tech_stock()
        mock_stock_repository.get_by_symbol.return_value = test_stock

        # Verify custom behavior
        result = mock_stock_repository.get_by_symbol(StockSymbol("MSFT"))
        assert result == test_stock


class TestStockEntityBuilder:
    """Test the StockEntityBuilder class."""

    def test_builder_creates_valid_entity(self) -> None:
        """Should create valid stock entity with defaults."""
        stock = StockEntityBuilder().build()

        assert stock.symbol.value == "AAPL"
        assert stock.company_name.value == "Apple Inc."
        assert stock.sector is not None
        assert stock.sector.value == "Technology"
        assert stock.grade is not None
        assert stock.grade.value == "A"

    def test_builder_fluent_interface(self) -> None:
        """Should support method chaining."""
        stock = (
            StockEntityBuilder()
            .with_symbol("GOOGL")
            .with_company_name("Alphabet Inc.")
            .with_sector("Technology")
            .with_grade("A")
            .with_notes("Search giant")
            .build()
        )

        assert stock.symbol.value == "GOOGL"
        assert stock.company_name.value == "Alphabet Inc."
        assert stock.notes.value == "Search giant"

    def test_builder_with_id(self) -> None:
        """Should create entity with specific ID."""
        stock = StockEntityBuilder().with_id("custom-123").build()
        assert stock.id == "custom-123"

    def test_factory_methods(self) -> None:
        """Should provide convenient factory methods."""
        # Test tech stock factory
        tech = StockEntityBuilder.tech_stock()
        assert tech.symbol.value == "MSFT"
        assert tech.sector is not None
        assert tech.sector.value == "Technology"

        # Test financial stock factory
        financial = StockEntityBuilder.financial_stock()
        assert financial.symbol.value == "JPM"
        assert financial.sector is not None
        assert financial.sector.value == "Financial Services"

        # Test minimal stock factory
        minimal = StockEntityBuilder.minimal_stock()
        assert minimal.symbol.value == "TEST"
        assert minimal.sector is None
        assert minimal.industry_group is None
        assert minimal.grade is None

    def test_builder_handles_optional_fields(self) -> None:
        """Should handle None values for optional fields."""
        stock = (
            StockEntityBuilder()
            .with_sector(None)
            .with_industry_group(None)
            .with_grade(None)
            .build()
        )

        assert stock.sector is None
        assert stock.industry_group is None
        assert stock.grade is None


class TestSampleStocksFixture:
    """Test the sample stocks fixture."""

    def test_sample_stocks_provides_diverse_data(
        self, sample_stocks: List[StockEntity]
    ) -> None:
        """Should provide diverse test stock data."""
        assert len(sample_stocks) == 4

        # Check we have different sectors
        sectors = {stock.sector.value for stock in sample_stocks if stock.sector}
        assert len(sectors) >= 3

        # Check all have required fields
        for stock in sample_stocks:
            assert stock.symbol is not None
            assert stock.company_name is not None


class TestDatabaseHelpers:
    """Test database helper functions."""

    def test_db_transaction_context_manager(
        self, in_memory_db: sqlite3.Connection
    ) -> None:
        """Should provide transaction context with automatic commit/rollback."""
        # Test successful transaction
        with db_transaction(in_memory_db) as cursor:
            _ = cursor.execute(
                """
                INSERT INTO stocks (id, symbol, company_name)
                VALUES ('ctx-1', 'CTX', 'Context Test')
                """
            )

        # Verify commit happened
        cursor = in_memory_db.cursor()
        _ = cursor.execute("SELECT COUNT(*) FROM stocks WHERE id = 'ctx-1'")
        assert cursor.fetchone()[0] == 1

        # Test rollback on exception
        with pytest.raises(sqlite3.IntegrityError):
            with db_transaction(in_memory_db) as cursor:
                # This should fail due to duplicate ID
                _ = cursor.execute(
                    """
                    INSERT INTO stocks (id, symbol, company_name)
                    VALUES ('ctx-1', 'CTX2', 'Context Test 2')
                    """
                )

    def test_seed_test_stocks(
        self, in_memory_db: sqlite3.Connection, sample_stocks: List[StockEntity]
    ) -> None:
        """Should seed database with stock entities."""
        seed_test_stocks(in_memory_db, sample_stocks)

        # Verify all stocks were inserted
        cursor = in_memory_db.cursor()
        _ = cursor.execute("SELECT COUNT(*) FROM stocks")
        assert cursor.fetchone()[0] == len(sample_stocks)

        # Verify data integrity
        _ = cursor.execute(
            "SELECT symbol, company_name FROM stocks WHERE symbol = 'MSFT'"
        )
        row = cursor.fetchone()
        assert row[0] == "MSFT"
        assert row[1] == "Microsoft Corporation"

    def test_seed_test_portfolio(self, in_memory_db: sqlite3.Connection) -> None:
        """Should seed database with a portfolio."""
        portfolio_id = seed_test_portfolio(in_memory_db, "My Test Portfolio")

        assert portfolio_id.startswith("portfolio-")

        # Verify portfolio was created
        cursor = in_memory_db.cursor()
        _ = cursor.execute(
            "SELECT name, is_active FROM portfolios WHERE id = ?", (portfolio_id,)
        )
        row = cursor.fetchone()
        assert row[0] == "My Test Portfolio"
        assert row[1] == 1  # is_active = True
