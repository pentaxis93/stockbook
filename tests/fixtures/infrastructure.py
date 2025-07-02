"""
Comprehensive test fixtures for testing the infrastructure layer.

This module provides:
1. In-memory SQLite database fixture
2. Mock repository fixtures
3. Test data builder for StockEntity
4. Transaction rollback fixture for test isolation
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Generator, List, Optional
from unittest.mock import Mock

import pytest

from src.domain.entities import StockEntity
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

# =============================================================================
# In-Memory SQLite Database Fixture
# =============================================================================


@pytest.fixture
def in_memory_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Create an in-memory SQLite database for testing.

    This fixture provides a fresh database connection for each test,
    ensuring complete isolation between tests.

    Yields:
        sqlite3.Connection: Connection to the in-memory database
    """
    # Create in-memory database
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    # Enable foreign key constraints
    _ = conn.execute("PRAGMA foreign_keys = ON")

    # Create schema (simplified version for testing)
    _create_test_schema(conn)

    yield conn

    # Cleanup
    conn.close()


def _create_test_schema(conn: sqlite3.Connection) -> None:
    """Create a simplified test schema for the in-memory database."""
    # Stocks table
    _ = conn.execute(
        """
        CREATE TABLE stocks (
            id TEXT PRIMARY KEY,
            symbol TEXT UNIQUE NOT NULL,
            company_name TEXT NOT NULL,
            sector TEXT,
            industry_group TEXT,
            grade TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Portfolios table
    _ = conn.execute(
        """
        CREATE TABLE portfolios (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Transactions table
    _ = conn.execute(
        """
        CREATE TABLE transactions (
            id TEXT PRIMARY KEY,
            portfolio_id TEXT NOT NULL,
            stock_id TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            transaction_date DATE NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (portfolio_id) REFERENCES portfolios(id),
            FOREIGN KEY (stock_id) REFERENCES stocks(id)
        )
    """
    )

    # Add other tables as needed...
    conn.commit()


# =============================================================================
# Transaction Rollback Fixture
# =============================================================================


@pytest.fixture
def transaction_rollback(
    in_memory_db: sqlite3.Connection,
) -> Generator[sqlite3.Connection, None, None]:
    """
    Provide automatic transaction rollback for test isolation.

    This fixture wraps each test in a transaction that is rolled back
    after the test completes, ensuring no data persists between tests.

    Args:
        in_memory_db: The in-memory database connection

    Yields:
        sqlite3.Connection: Database connection with active transaction
    """
    # Begin transaction
    _ = in_memory_db.execute("BEGIN")

    # Create a savepoint for nested transaction support
    _ = in_memory_db.execute("SAVEPOINT test_savepoint")

    try:
        yield in_memory_db
    finally:
        # Always rollback to ensure test isolation
        _ = in_memory_db.execute("ROLLBACK TO SAVEPOINT test_savepoint")
        _ = in_memory_db.execute("ROLLBACK")


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
# Test Data Builder for StockEntity
# =============================================================================


class StockEntityBuilder:
    """
    Builder class for creating StockEntity instances with test data.

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

    def with_id(self, stock_id: str) -> "StockEntityBuilder":
        """Set the stock ID."""
        self._id = stock_id
        return self

    def with_symbol(self, symbol: str) -> "StockEntityBuilder":
        """Set the stock symbol."""
        self._symbol = symbol
        return self

    def with_company_name(self, name: str) -> "StockEntityBuilder":
        """Set the company name."""
        self._company_name = name
        return self

    def with_sector(self, sector: Optional[str]) -> "StockEntityBuilder":
        """Set the sector."""
        self._sector = sector
        return self

    def with_industry_group(self, industry: Optional[str]) -> "StockEntityBuilder":
        """Set the industry group."""
        self._industry_group = industry
        return self

    def with_grade(self, grade: Optional[str]) -> "StockEntityBuilder":
        """Set the stock grade."""
        self._grade = grade
        return self

    def with_notes(self, notes: str) -> "StockEntityBuilder":
        """Set the notes."""
        self._notes = notes
        return self

    def build(self) -> StockEntity:
        """
        Build the StockEntity with configured values.

        Returns:
            StockEntity: Configured stock entity
        """
        return StockEntity(
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
    def tech_stock(cls) -> StockEntity:
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
    def financial_stock(cls) -> StockEntity:
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
    def minimal_stock(cls) -> StockEntity:
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
    def stock_with_id(cls, stock_id: str) -> StockEntity:
        """Create a stock with a specific ID."""
        return cls().with_id(stock_id).build()


# =============================================================================
# Additional Test Data Builders
# =============================================================================


@pytest.fixture
def stock_builder() -> type[StockEntityBuilder]:
    """
    Provide StockEntityBuilder class for tests.

    Returns:
        type[StockEntityBuilder]: The builder class
    """
    return StockEntityBuilder


@pytest.fixture
def sample_stocks() -> List[StockEntity]:
    """
    Create a list of sample stock entities for testing.

    Returns:
        List[StockEntity]: List of diverse stock entities
    """
    return [
        StockEntityBuilder.tech_stock(),
        StockEntityBuilder.financial_stock(),
        StockEntityBuilder()
        .with_symbol("AMZN")
        .with_company_name("Amazon.com Inc.")
        .with_sector("Consumer Goods")
        .with_industry_group("Consumer Electronics")
        .with_grade("A")
        .with_notes("E-commerce and cloud leader")
        .build(),
        StockEntityBuilder()
        .with_symbol("JNJ")
        .with_company_name("Johnson & Johnson")
        .with_sector("Healthcare")
        .with_industry_group("Pharmaceuticals")
        .with_grade("B")
        .with_notes("Healthcare conglomerate")
        .build(),
    ]


# =============================================================================
# Database Transaction Helpers
# =============================================================================


@contextmanager
def db_transaction(conn: sqlite3.Connection) -> Generator[sqlite3.Cursor, None, None]:
    """
    Context manager for database transactions with automatic rollback.

    Args:
        conn: Database connection

    Yields:
        sqlite3.Cursor: Database cursor for executing queries
    """
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()


# =============================================================================
# Test Data Seeding Functions
# =============================================================================


def seed_test_stocks(conn: sqlite3.Connection, stocks: List[StockEntity]) -> None:
    """
    Seed the test database with stock entities.

    Args:
        conn: Database connection
        stocks: List of stock entities to insert
    """
    with db_transaction(conn) as cursor:
        for stock in stocks:
            _ = cursor.execute(
                """
                INSERT INTO stocks (id, symbol, company_name, sector, industry_group, grade, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    stock.id,
                    stock.symbol.value,
                    stock.company_name.value,
                    stock.sector.value if stock.sector else None,
                    stock.industry_group.value if stock.industry_group else None,
                    stock.grade.value if stock.grade else None,
                    stock.notes.value,
                ),
            )


def seed_test_portfolio(conn: sqlite3.Connection, name: str = "Test Portfolio") -> str:
    """
    Seed the test database with a portfolio.

    Args:
        conn: Database connection
        name: Portfolio name

    Returns:
        str: ID of the created portfolio
    """
    portfolio_id = f"portfolio-{datetime.now(timezone.utc).timestamp()}"

    with db_transaction(conn) as cursor:
        _ = cursor.execute(
            """
            INSERT INTO portfolios (id, name, description, is_active)
            VALUES (?, ?, ?, ?)
            """,
            (portfolio_id, name, "Test portfolio for testing", True),
        )

    return portfolio_id
