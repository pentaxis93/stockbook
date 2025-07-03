"""
Comprehensive test fixtures for testing the infrastructure layer.

This module provides:
1. SQLAlchemy-based in-memory database fixtures
2. Mock repository fixtures
3. Test data builder for Stock
4. SQLAlchemy-based data seeding functions
"""

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false
# pyright: reportUnusedVariable=false, reportUnknownArgumentType=false

from datetime import datetime, timezone
from typing import Generator, List, Optional
from unittest.mock import Mock

import pytest
from sqlalchemy import create_engine, insert, text
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.pool import StaticPool

from src.domain.entities import Stock
from src.domain.repositories.interfaces import (
    IJournalRepository,
    IPortfolioBalanceRepository,
    IPortfolioRepository,
    IStockBookUnitOfWork,
    IStockRepository,
    ITargetRepository,
    ITransactionRepository,
)
from src.domain.value_objects import (
    CompanyName,
    Grade,
    IndustryGroup,
    Notes,
    Sector,
    StockSymbol,
)
from src.infrastructure.persistence.tables import metadata
from src.infrastructure.persistence.tables.portfolio_table import portfolio_table
from src.infrastructure.persistence.tables.stock_table import stock_table

# =============================================================================
# SQLAlchemy-based Database Fixtures
# =============================================================================


@pytest.fixture
def sqlalchemy_in_memory_engine() -> Generator[Engine, None, None]:
    """
    Create an in-memory SQLite database engine using SQLAlchemy.

    This fixture provides a fresh SQLAlchemy engine for each test,
    with all tables created from the application's table definitions.

    Yields:
        Engine: SQLAlchemy engine connected to in-memory database
    """
    # Create engine with StaticPool to ensure same connection is reused
    # This is important for in-memory SQLite databases
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,  # Set to True for SQL debugging
    )

    # Create all tables using the application's metadata
    metadata.create_all(engine)

    # Enable foreign keys for SQLite
    with engine.begin() as conn:
        conn.execute(text("PRAGMA foreign_keys = ON"))

    yield engine

    # Cleanup
    engine.dispose()


@pytest.fixture
def sqlalchemy_connection(
    sqlalchemy_in_memory_engine: Engine,
) -> Generator[Connection, None, None]:
    """
    Provide a SQLAlchemy connection with automatic rollback.

    This fixture wraps each test in a transaction that is rolled back
    after the test completes, ensuring complete isolation between tests.

    Args:
        sqlalchemy_in_memory_engine: The in-memory database engine

    Yields:
        Connection: SQLAlchemy connection with active transaction
    """
    # Start a connection and transaction
    with sqlalchemy_in_memory_engine.connect() as connection:
        # Begin a transaction
        with connection.begin() as transaction:
            yield connection
            # Transaction is automatically rolled back when exiting context


# =============================================================================
# Mock Repository Fixtures
# =============================================================================


@pytest.fixture
def mock_stock_repository() -> Mock:
    """
    Create a mock IStockRepository for testing.

    Returns:
        Mock: Properly typed mock of IStockRepository
    """
    mock = Mock(spec=IStockRepository)

    # Set up default return values
    mock.create.return_value = "stock-123"
    mock.get_by_id.return_value = None
    mock.get_by_symbol.return_value = None
    mock.get_all.return_value = []
    mock.update.return_value = True
    mock.delete.return_value = True
    mock.exists_by_symbol.return_value = False

    mock.search_stocks.return_value = []

    return mock


@pytest.fixture
def mock_portfolio_repository() -> Mock:
    """
    Create a mock IPortfolioRepository for testing.

    Returns:
        Mock: Properly typed mock of IPortfolioRepository
    """
    mock = Mock(spec=IPortfolioRepository)

    # Set up default return values
    mock.create.return_value = "portfolio-123"
    mock.get_by_id.return_value = None
    mock.get_all_active.return_value = []
    mock.get_all.return_value = []
    mock.update.return_value = True
    mock.deactivate.return_value = True

    return mock


@pytest.fixture
def mock_transaction_repository() -> Mock:
    """
    Create a mock ITransactionRepository for testing.

    Returns:
        Mock: Properly typed mock of ITransactionRepository
    """
    mock = Mock(spec=ITransactionRepository)

    # Set up default return values
    mock.create.return_value = "transaction-123"
    mock.get_by_id.return_value = None
    mock.get_by_portfolio.return_value = []
    mock.get_by_stock.return_value = []
    mock.get_by_date_range.return_value = []
    mock.update.return_value = True
    mock.delete.return_value = True

    return mock


@pytest.fixture
def mock_target_repository() -> Mock:
    """
    Create a mock ITargetRepository for testing.

    Returns:
        Mock: Properly typed mock of ITargetRepository
    """
    mock = Mock(spec=ITargetRepository)

    # Set up default return values
    mock.create.return_value = "target-123"
    mock.get_by_id.return_value = None
    mock.get_active_by_portfolio.return_value = []
    mock.get_active_by_stock.return_value = []
    mock.get_all_active.return_value = []
    mock.update.return_value = True
    mock.update_status.return_value = True

    return mock


@pytest.fixture
def mock_portfolio_balance_repository() -> Mock:
    """
    Create a mock IPortfolioBalanceRepository for testing.

    Returns:
        Mock: Properly typed mock of IPortfolioBalanceRepository
    """
    mock = Mock(spec=IPortfolioBalanceRepository)

    # Set up default return values
    mock.create.return_value = "balance-123"
    mock.get_by_id.return_value = None
    mock.get_by_portfolio_and_date.return_value = None
    mock.get_history.return_value = []
    mock.get_latest_balance.return_value = None

    return mock


@pytest.fixture
def mock_journal_repository() -> Mock:
    """
    Create a mock IJournalRepository for testing.

    Returns:
        Mock: Properly typed mock of IJournalRepository
    """
    mock = Mock(spec=IJournalRepository)

    # Set up default return values
    mock.create.return_value = "journal-123"
    mock.get_by_id.return_value = None
    mock.get_recent.return_value = []
    mock.get_by_portfolio.return_value = []
    mock.get_by_stock.return_value = []
    mock.get_by_transaction.return_value = []
    mock.get_by_date_range.return_value = []
    mock.update.return_value = True
    mock.delete.return_value = True

    return mock


@pytest.fixture
def mock_unit_of_work(
    mock_stock_repository: Mock,
    mock_portfolio_repository: Mock,
    mock_transaction_repository: Mock,
    mock_target_repository: Mock,
    mock_portfolio_balance_repository: Mock,
    mock_journal_repository: Mock,
) -> Mock:
    """
    Create a mock IStockBookUnitOfWork with all repositories.

    Args:
        mock_stock_repository: Mock stock repository
        mock_portfolio_repository: Mock portfolio repository
        mock_transaction_repository: Mock transaction repository
        mock_target_repository: Mock target repository
        mock_portfolio_balance_repository: Mock balance repository
        mock_journal_repository: Mock journal repository

    Returns:
        Mock: Properly typed mock of IStockBookUnitOfWork
    """
    mock = Mock(spec=IStockBookUnitOfWork)

    # Set up repository properties
    mock.stocks = mock_stock_repository
    mock.portfolios = mock_portfolio_repository
    mock.transactions = mock_transaction_repository
    mock.targets = mock_target_repository
    mock.balances = mock_portfolio_balance_repository
    mock.journal = mock_journal_repository

    # Set up context manager methods
    mock.__enter__ = Mock(return_value=mock)
    mock.__exit__ = Mock(return_value=None)

    # Set up transaction methods
    mock.commit = Mock()
    mock.rollback = Mock()

    return mock


# =============================================================================
# Test Data Builder for Stock
# =============================================================================


class StockBuilder:
    """
    Builder class for creating Stock instances with test data.

    Provides a fluent interface for creating stock entities with
    customizable properties and sensible defaults.
    """

    def __init__(self) -> None:
        """Initialize builder with default values."""
        self._id: Optional[str] = None
        self._symbol: str = "AAPL"
        self._company_name: str = "Apple Inc."
        self._sector: Optional[str] = "Technology"
        self._industry_group: Optional[str] = "Software"
        self._grade: Optional[str] = "A"
        self._notes: str = "Test stock entity"

    def with_id(self, stock_id: str) -> "StockBuilder":
        """Set the stock ID."""
        self._id = stock_id
        return self

    def with_symbol(self, symbol: str) -> "StockBuilder":
        """Set the stock symbol."""
        self._symbol = symbol
        return self

    def with_company_name(self, name: str) -> "StockBuilder":
        """Set the company name."""
        self._company_name = name
        return self

    def with_sector(self, sector: Optional[str]) -> "StockBuilder":
        """Set the sector."""
        self._sector = sector
        return self

    def with_industry_group(self, industry: Optional[str]) -> "StockBuilder":
        """Set the industry group."""
        self._industry_group = industry
        return self

    def with_grade(self, grade: Optional[str]) -> "StockBuilder":
        """Set the stock grade."""
        self._grade = grade
        return self

    def with_notes(self, notes: str) -> "StockBuilder":
        """Set the notes."""
        self._notes = notes
        return self

    def build(self) -> Stock:
        """
        Build the Stock with configured values.

        Returns:
            Stock: Configured stock entity
        """
        return Stock(
            id=self._id,
            symbol=StockSymbol(self._symbol),
            company_name=CompanyName(self._company_name),
            sector=Sector(self._sector) if self._sector else None,
            industry_group=(
                IndustryGroup(self._industry_group) if self._industry_group else None
            ),
            grade=Grade(self._grade) if self._grade else None,
            notes=Notes(self._notes),
        )

    # Factory methods for common test scenarios

    @classmethod
    def tech_stock(cls) -> Stock:
        """Create a technology stock for testing."""
        return (
            cls()
            .with_symbol("MSFT")
            .with_company_name("Microsoft Corporation")
            .with_sector("Technology")
            .with_industry_group("Software")
            .with_grade("A")
            .with_notes("Tech giant with cloud services")
            .build()
        )

    @classmethod
    def financial_stock(cls) -> Stock:
        """Create a financial stock for testing."""
        return (
            cls()
            .with_symbol("JPM")
            .with_company_name("JPMorgan Chase & Co.")
            .with_sector("Financial Services")
            .with_industry_group("Banks")
            .with_grade("B")
            .with_notes("Major US bank")
            .build()
        )

    @classmethod
    def minimal_stock(cls) -> Stock:
        """Create a stock with minimal required fields."""
        return (
            cls()
            .with_symbol("TEST")
            .with_company_name("Test Company")
            .with_sector(None)
            .with_industry_group(None)
            .with_grade(None)
            .with_notes("")
            .build()
        )

    @classmethod
    def stock_with_id(cls, stock_id: str) -> Stock:
        """Create a stock with a specific ID."""
        return cls().with_id(stock_id).build()


# =============================================================================
# Additional Test Data Builders
# =============================================================================


@pytest.fixture
def stock_builder() -> type[StockBuilder]:
    """
    Provide StockBuilder class for tests.

    Returns:
        type[StockBuilder]: The builder class
    """
    return StockBuilder


@pytest.fixture
def sample_stocks() -> List[Stock]:
    """
    Create a list of sample stock entities for testing.

    Returns:
        List[Stock]: List of diverse stock entities
    """
    return [
        StockBuilder.tech_stock(),
        StockBuilder.financial_stock(),
        StockBuilder()
        .with_symbol("AMZN")
        .with_company_name("Amazon.com Inc.")
        .with_sector("Consumer Goods")
        .with_industry_group("Consumer Electronics")
        .with_grade("A")
        .with_notes("E-commerce and cloud leader")
        .build(),
        StockBuilder()
        .with_symbol("JNJ")
        .with_company_name("Johnson & Johnson")
        .with_sector("Healthcare")
        .with_industry_group("Pharmaceuticals")
        .with_grade("B")
        .with_notes("Healthcare conglomerate")
        .build(),
    ]


# =============================================================================
# Test Data Seeding Functions
# =============================================================================


def seed_test_stocks_sqlalchemy(conn: Connection, stocks: List[Stock]) -> None:
    """
    Seed the test database with stock entities using SQLAlchemy.

    Args:
        conn: SQLAlchemy database connection
        stocks: List of stock entities to insert
    """
    for stock in stocks:
        stmt = insert(stock_table).values(
            id=stock.id,
            symbol=stock.symbol.value,
            company_name=stock.company_name.value if stock.company_name else None,
            sector=stock.sector.value if stock.sector else None,
            industry_group=stock.industry_group.value if stock.industry_group else None,
            grade=stock.grade.value if stock.grade else None,
            notes=stock.notes.value,
        )
        conn.execute(stmt)
    # Don't commit here - let the caller manage transactions


def seed_test_portfolio_sqlalchemy(
    conn: Connection, name: str = "Test Portfolio"
) -> str:
    """
    Seed the test database with a portfolio using SQLAlchemy.

    Args:
        conn: SQLAlchemy database connection
        name: Name of the portfolio

    Returns:
        str: ID of the created portfolio
    """
    portfolio_id = f"portfolio-{datetime.now(timezone.utc).timestamp()}"
    stmt = insert(portfolio_table).values(
        id=portfolio_id,
        name=name,
        description=f"Test portfolio created at {datetime.now(timezone.utc)}",
        currency="USD",
    )
    conn.execute(stmt)
    # Don't commit here - let the caller manage transactions
    return portfolio_id
