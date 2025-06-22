"""
Tests for SQLite Portfolio Balance Repository implementation.

Following TDD approach - defines expected behavior before implementation.
"""

import os
import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Iterator

import pytest

from src.domain.entities.portfolio_balance_entity import PortfolioBalanceEntity

# IPortfolioBalanceRepository import removed - unused
from src.domain.value_objects import IndexChange, Money
from src.infrastructure.persistence.database_connection import DatabaseConnection
from src.infrastructure.persistence.interfaces import IDatabaseConnection
from src.infrastructure.repositories.sqlite_balance_repository import (
    SqlitePortfolioBalanceRepository,
)


@pytest.fixture
def db_connection() -> Iterator[IDatabaseConnection]:
    """Create temporary database for testing."""
    # Create temporary database file
    temp_fd, temp_path = tempfile.mkstemp(suffix=".db")
    os.close(temp_fd)

    connection = DatabaseConnection(temp_path)
    connection.initialize_schema()

    # Create test portfolio
    with connection.transaction() as conn:
        conn.execute(
            """
            INSERT INTO portfolio (id, name, description, max_positions, max_risk_per_trade, is_active)
            VALUES ('portfolio-id-1', 'Test Portfolio', 'Test portfolio for balances', 50, 0.02, 1)
        """
        )

    yield connection

    # Cleanup
    connection.close()
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def balance_repository(
    db_connection: DatabaseConnection,
) -> SqlitePortfolioBalanceRepository:
    """Create balance repository with test database."""
    return SqlitePortfolioBalanceRepository(db_connection)


@pytest.fixture
def sample_balance() -> PortfolioBalanceEntity:
    """Create sample balance entity for testing."""
    return PortfolioBalanceEntity(
        portfolio_id="portfolio-id-1",
        balance_date=date(2024, 1, 15),
        withdrawals=Money(Decimal("0.00")),
        deposits=Money(Decimal("1000.00")),
        final_balance=Money(Decimal("10500.00")),
        index_change=IndexChange(2.5),
    )


class TestPortfolioBalanceRepositoryCreate:
    """Test balance creation operations."""

    def test_create_balance_returns_id(
        self,
        balance_repository: SqlitePortfolioBalanceRepository,
        sample_balance: PortfolioBalanceEntity,
    ) -> None:
        """Should create balance and return database ID."""
        # Act
        balance_id = balance_repository.create(sample_balance)

        # Assert
        assert isinstance(balance_id, str)
        assert balance_id

    def test_create_and_retrieve_balance(
        self,
        balance_repository: SqlitePortfolioBalanceRepository,
        sample_balance: PortfolioBalanceEntity,
    ) -> None:
        """Should create and retrieve balance correctly."""
        # Act
        balance_id = balance_repository.create(sample_balance)
        retrieved = balance_repository.get_by_id(balance_id)

        # Assert
        assert retrieved is not None
        assert retrieved.portfolio_id == sample_balance.portfolio_id
        assert retrieved.balance_date == sample_balance.balance_date
        assert retrieved.final_balance.amount == sample_balance.final_balance.amount


class TestPortfolioBalanceRepositoryRead:
    """Test balance read operations."""

    def test_get_by_portfolio_and_date(
        self,
        balance_repository: SqlitePortfolioBalanceRepository,
        sample_balance: PortfolioBalanceEntity,
    ) -> None:
        """Should retrieve balance by portfolio and date."""
        # Arrange
        balance_repository.create(sample_balance)

        # Act
        retrieved = balance_repository.get_by_portfolio_and_date(
            "portfolio-id-1", date(2024, 1, 15)
        )

        # Assert
        assert retrieved is not None
        assert retrieved.portfolio_id == "portfolio-id-1"
        assert retrieved.balance_date == date(2024, 1, 15)

    def test_get_history(
        self, balance_repository: SqlitePortfolioBalanceRepository
    ) -> None:
        """Should retrieve balance history for portfolio."""
        # Arrange
        balances = [
            PortfolioBalanceEntity(
                portfolio_id="portfolio-id-1",
                balance_date=date(2024, 1, 1),
                withdrawals=Money(Decimal("0.00")),
                deposits=Money(Decimal("1000.00")),
                final_balance=Money(Decimal("10000.00")),
            ),
            PortfolioBalanceEntity(
                portfolio_id="portfolio-id-1",
                balance_date=date(2024, 1, 2),
                withdrawals=Money(Decimal("0.00")),
                deposits=Money(Decimal("0.00")),
                final_balance=Money(Decimal("10100.00")),
            ),
        ]

        for balance in balances:
            balance_repository.create(balance)

        # Act
        history = balance_repository.get_history("portfolio-id-1")

        # Assert
        assert len(history) == 2
        # Should be ordered by date (newest first)
        assert history[0].balance_date > history[1].balance_date

    def test_get_latest_balance(
        self, balance_repository: SqlitePortfolioBalanceRepository
    ) -> None:
        """Should retrieve latest balance for portfolio."""
        # Arrange
        old_balance = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-1",
            balance_date=date(2024, 1, 1),
            withdrawals=Money(Decimal("0.00")),
            deposits=Money(Decimal("1000.00")),
            final_balance=Money(Decimal("10000.00")),
        )
        new_balance = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-1",
            balance_date=date(2024, 1, 15),
            withdrawals=Money(Decimal("0.00")),
            deposits=Money(Decimal("0.00")),
            final_balance=Money(Decimal("10500.00")),
        )

        balance_repository.create(old_balance)
        balance_repository.create(new_balance)

        # Act
        latest = balance_repository.get_latest_balance("portfolio-id-1")

        # Assert
        assert latest is not None
        assert latest.balance_date == date(2024, 1, 15)
        assert latest.final_balance.amount == Decimal("10500.00")


class TestPortfolioBalanceRepositoryIntegration:
    """Integration tests for balance repository operations."""

    def test_full_balance_lifecycle(
        self, balance_repository: SqlitePortfolioBalanceRepository
    ) -> None:
        """Test complete balance operations."""
        # Create
        balance = PortfolioBalanceEntity(
            portfolio_id="portfolio-id-1",
            balance_date=date(2024, 1, 1),
            withdrawals=Money(Decimal("100.00")),
            deposits=Money(Decimal("1000.00")),
            final_balance=Money(Decimal("10000.00")),
            index_change=IndexChange(1.5),
        )
        balance_id = balance_repository.create(balance)
        assert balance_id is not None

        # Read
        retrieved = balance_repository.get_by_id(balance_id)
        assert retrieved is not None
        assert retrieved.index_change is not None
        assert retrieved.index_change.value == 1.5

        # Test portfolio queries
        by_date = balance_repository.get_by_portfolio_and_date(
            "portfolio-id-1", date(2024, 1, 1)
        )
        assert by_date is not None

        latest = balance_repository.get_latest_balance("portfolio-id-1")
        assert latest is not None
        assert latest.id == balance_id
