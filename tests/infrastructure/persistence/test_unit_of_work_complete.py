"""
Test the complete Unit of Work implementation with all repositories.
"""

import contextlib
import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from src.domain.entities.portfolio_entity import PortfolioEntity
from src.domain.entities.stock_entity import StockEntity
from src.domain.value_objects import (
    CompanyName,
    Grade,
    IndustryGroup,
    Notes,
    PortfolioName,
)
from src.domain.value_objects.sector import Sector
from src.domain.value_objects.stock_symbol import StockSymbol
from src.infrastructure.persistence.database_connection import DatabaseConnection
from src.infrastructure.persistence.unit_of_work import SqliteUnitOfWork


@pytest.fixture
def db_connection() -> Generator[DatabaseConnection, None, None]:
    """Create temporary database for testing."""
    temp_fd, temp_path = tempfile.mkstemp(suffix=".db")
    os.close(temp_fd)

    connection = DatabaseConnection(temp_path)
    connection.initialize_schema()

    yield connection

    connection.close()
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def unit_of_work(db_connection: DatabaseConnection) -> SqliteUnitOfWork:
    """Create unit of work with test database."""
    return SqliteUnitOfWork(db_connection)


def test_unit_of_work_all_repositories_accessible(
    unit_of_work: SqliteUnitOfWork,
) -> None:
    """Should provide access to all repository types."""
    # Test that all repositories are accessible
    assert unit_of_work.stocks is not None
    assert unit_of_work.portfolios is not None
    assert unit_of_work.transactions is not None
    assert unit_of_work.targets is not None
    assert unit_of_work.balances is not None
    assert unit_of_work.journal is not None


def test_unit_of_work_transactional_context(unit_of_work: SqliteUnitOfWork) -> None:
    """Should maintain transaction across multiple repositories."""

    # Create test data in a transaction
    with unit_of_work:
        # Create a stock
        stock = StockEntity(
            symbol=StockSymbol("AAPL"),
            company_name=CompanyName("Apple Inc."),
            sector=Sector("Technology"),
            industry_group=IndustryGroup("Software"),
            grade=Grade("A"),
        )
        stock_id = unit_of_work.stocks.create(stock)

        # Create a portfolio
        portfolio = PortfolioEntity(
            name=PortfolioName("Test Portfolio"),
            description=Notes("Test portfolio for unit of work"),
        )
        portfolio_id = unit_of_work.portfolios.create(portfolio)

        # Both should be accessible within the transaction
        retrieved_stock = unit_of_work.stocks.get_by_id(stock_id)
        retrieved_portfolio = unit_of_work.portfolios.get_by_id(portfolio_id)

        assert retrieved_stock is not None
        assert retrieved_portfolio is not None
        assert retrieved_stock.company_name.value == "Apple Inc."
        assert retrieved_portfolio.name.value == "Test Portfolio"


def test_unit_of_work_rollback_on_exception(unit_of_work: SqliteUnitOfWork) -> None:
    """Should rollback transaction on exception."""

    with contextlib.suppress(ValueError):
        with unit_of_work:
            # Create a stock
            stock = StockEntity(
                symbol=StockSymbol("MSFT"),
                company_name=CompanyName("Microsoft Corp."),
                sector=Sector("Technology"),
                industry_group=IndustryGroup("Software"),
                grade=Grade("A"),
            )
            stock_id = unit_of_work.stocks.create(stock)

            # Verify it exists within transaction
            retrieved = unit_of_work.stocks.get_by_id(stock_id)
            assert retrieved is not None

            # Raise an exception to trigger rollback
            raise ValueError("Test exception for rollback")

    # After rollback, the stock should not exist
    # Create a new unit of work to verify
    with unit_of_work:
        all_stocks = unit_of_work.stocks.get_all()
        msft_stocks = [s for s in all_stocks if s.symbol.value == "MSFT"]
        assert len(msft_stocks) == 0
