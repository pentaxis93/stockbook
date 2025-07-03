"""
Tests for infrastructure test fixtures.

This module tests that all fixtures work correctly and provide
the expected functionality for infrastructure testing.
"""

# pyright: reportUnusedImport=false

from typing import List, cast
from unittest.mock import Mock

import pytest
from sqlalchemy import insert, select
from sqlalchemy.engine import Connection, Engine

from src.domain.entities import Stock
from src.domain.repositories.interfaces import (
    IStockBookUnitOfWork,
    IStockRepository,
)
from src.domain.value_objects import StockSymbol
from src.infrastructure.persistence.tables.stock_table import stock_table

from .infrastructure import sqlalchemy_connection  # noqa: F401
from .infrastructure import sqlalchemy_in_memory_engine  # noqa: F401
from .infrastructure import (
    StockBuilder,
    seed_test_portfolio_sqlalchemy,
    seed_test_stocks_sqlalchemy,
)


class TestMockRepositoryFixtures:
    """Test all mock repository fixtures."""

    def test_mock_stock_repository(self, mock_stock_repository: Mock) -> None:
        """Should provide properly configured mock stock repository."""
        mock = cast(IStockRepository, mock_stock_repository)

        # Test default return values
        assert mock.create(Mock(spec=Stock)) == "stock-123"
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
        test_stock = StockBuilder.tech_stock()
        mock_stock_repository.get_by_symbol.return_value = test_stock

        # Verify custom behavior
        result = mock_stock_repository.get_by_symbol(StockSymbol("MSFT"))
        assert result == test_stock


class TestStockBuilder:
    """Test the StockBuilder class."""

    def test_builder_creates_valid_entity(self) -> None:
        """Should create valid stock entity with defaults."""
        stock = StockBuilder().build()

        assert stock.symbol.value == "AAPL"
        assert stock.company_name is not None
        assert stock.company_name.value == "Apple Inc."
        assert stock.sector is not None
        assert stock.sector.value == "Technology"
        assert stock.grade is not None
        assert stock.grade.value == "A"

    def test_builder_fluent_interface(self) -> None:
        """Should support method chaining."""
        stock = (
            StockBuilder()
            .with_symbol("GOOGL")
            .with_company_name("Alphabet Inc.")
            .with_sector("Technology")
            .with_grade("A")
            .with_notes("Search giant")
            .build()
        )

        assert stock.symbol.value == "GOOGL"
        assert stock.company_name is not None
        assert stock.company_name.value == "Alphabet Inc."
        assert stock.notes.value == "Search giant"

    def test_builder_with_id(self) -> None:
        """Should create entity with specific ID."""
        stock = StockBuilder().with_id("custom-123").build()
        assert stock.id == "custom-123"

    def test_factory_methods(self) -> None:
        """Should provide convenient factory methods."""
        # Test tech stock factory
        tech = StockBuilder.tech_stock()
        assert tech.symbol.value == "MSFT"
        assert tech.sector is not None
        assert tech.sector.value == "Technology"

        # Test financial stock factory
        financial = StockBuilder.financial_stock()
        assert financial.symbol.value == "JPM"
        assert financial.sector is not None
        assert financial.sector.value == "Financial Services"

        # Test minimal stock factory
        minimal = StockBuilder.minimal_stock()
        assert minimal.symbol.value == "TEST"
        assert minimal.sector is None
        assert minimal.industry_group is None
        assert minimal.grade is None

    def test_builder_handles_optional_fields(self) -> None:
        """Should handle None values for optional fields."""
        stock = (
            StockBuilder()
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
        self, sample_stocks: List[Stock]
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


class TestSQLAlchemyFixtures:
    """Test the SQLAlchemy-based database fixtures."""

    def test_sqlalchemy_engine_creates_all_tables(
        self, sqlalchemy_in_memory_engine: Engine
    ) -> None:
        """Should create all tables from metadata."""
        from sqlalchemy import inspect

        inspector = inspect(sqlalchemy_in_memory_engine)
        table_names = set(inspector.get_table_names())

        # Verify all expected tables exist
        expected_tables = {
            "stocks",
            "portfolios",
            "transactions",
            "targets",
            "portfolio_balances",
            "journal_entries",
        }
        assert expected_tables.issubset(table_names)

    def test_sqlalchemy_connection_rollback(
        self, sqlalchemy_connection: Connection
    ) -> None:
        """Should rollback changes after test completes."""
        # stock_table already imported at module level

        # Insert a stock
        stmt = insert(stock_table).values(
            id="rollback-test",
            symbol="ROLL",
            company_name="Rollback Test Co",
        )
        sqlalchemy_connection.execute(stmt)  # type: ignore[no-untyped-call]

        # Verify it exists in this transaction
        result = sqlalchemy_connection.execute(  # type: ignore[no-untyped-call]
            select(stock_table.c).where(stock_table.c.symbol == "ROLL")  # type: ignore[arg-type]
        )
        assert result.fetchone() is not None  # type: ignore[no-untyped-call]

        # Note: After the test, the transaction will be rolled back

    def test_sqlalchemy_fixtures_enforce_constraints(
        self, sqlalchemy_connection: Connection
    ) -> None:
        """Should enforce foreign key constraints."""
        from datetime import datetime

        from sqlalchemy.exc import IntegrityError

        from src.infrastructure.persistence.tables.transaction_table import (
            transaction_table,
        )

        # Try to insert transaction with invalid foreign keys
        stmt = insert(transaction_table).values(
            id="tx-invalid",
            portfolio_id="nonexistent-portfolio",
            stock_id="nonexistent-stock",
            transaction_type="BUY",
            quantity=100,
            price=150.00,
            transaction_date=datetime(2024, 1, 1),
        )

        with pytest.raises(IntegrityError):
            sqlalchemy_connection.execute(stmt)  # type: ignore[no-untyped-call]

    def test_sqlalchemy_seeding_functions(
        self, sqlalchemy_connection: Connection, sample_stocks: List[Stock]
    ) -> None:
        """Should seed data using SQLAlchemy functions."""
        # Seed stocks
        seed_test_stocks_sqlalchemy(sqlalchemy_connection, sample_stocks)

        # Verify stocks were inserted
        result = sqlalchemy_connection.execute(select(stock_table.c))  # type: ignore[no-untyped-call]
        rows = result.fetchall()  # type: ignore[no-untyped-call]
        assert len(rows) == len(sample_stocks)  # type: ignore[arg-type]

        # Verify specific stock
        result = sqlalchemy_connection.execute(  # type: ignore[no-untyped-call]
            select(stock_table.c).where(stock_table.c.symbol == "MSFT")  # type: ignore[arg-type]
        )
        row = result.fetchone()  # type: ignore[no-untyped-call]
        assert row is not None  # Type guard
        assert row.company_name == "Microsoft Corporation"  # type: ignore[attr-defined]

    def test_sqlalchemy_portfolio_seeding(
        self, sqlalchemy_connection: Connection
    ) -> None:
        """Should seed portfolio data using SQLAlchemy."""
        from src.infrastructure.persistence.tables.portfolio_table import (
            portfolio_table,
        )

        # Seed portfolio
        portfolio_id = seed_test_portfolio_sqlalchemy(
            sqlalchemy_connection, "Test Portfolio"
        )

        # Verify portfolio was created
        result = sqlalchemy_connection.execute(  # type: ignore[no-untyped-call]
            select(portfolio_table.c).where(portfolio_table.c.id == portfolio_id)  # type: ignore[arg-type]
        )
        row = result.fetchone()  # type: ignore[no-untyped-call]
        assert row is not None
        assert row.name == "Test Portfolio"  # type: ignore[attr-defined]
        assert row.currency == "USD"  # type: ignore[attr-defined]
