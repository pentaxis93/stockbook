"""
Tests for SQLite Transaction Repository implementation.

Following TDD approach - defines expected behavior before implementation.
"""

import os
import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Iterator

import pytest

from src.domain.entities.transaction_entity import TransactionEntity

# ITransactionRepository import removed - unused
from src.domain.value_objects import Money, Notes, Quantity, TransactionType
from src.infrastructure.persistence.database_connection import DatabaseConnection
from src.infrastructure.repositories.sqlite_transaction_repository import (
    SqliteTransactionRepository,
)


@pytest.fixture
def db_connection() -> Iterator[DatabaseConnection]:
    """Create temporary database for testing."""
    # Create temporary database file
    temp_fd, temp_path = tempfile.mkstemp(suffix=".db")
    os.close(temp_fd)

    connection = DatabaseConnection(temp_path)
    connection.initialize_schema()

    # Create test portfolios and stocks
    with connection.transaction() as conn:
        # Create test portfolio
        _ = conn.execute(
            """
            INSERT INTO portfolio (id, name, description, max_positions, max_risk_per_trade, is_active)
            VALUES ('portfolio-id-1', 'Test Portfolio', 'Test portfolio for transactions', 50, 0.02, 1)
        """
        )

        # Create test stock
        _ = conn.execute(
            """
            INSERT INTO stock (id, symbol, name, industry_group, grade, notes)
            VALUES ('stock-id-1', 'AAPL', 'Apple Inc.', 'Technology', 'A', 'Test stock')
        """
        )

    yield connection

    # Cleanup
    connection.close()
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def transaction_repository(
    db_connection: DatabaseConnection,
) -> SqliteTransactionRepository:
    """Create transaction repository with test database."""
    return SqliteTransactionRepository(db_connection)


@pytest.fixture
def sample_transaction() -> TransactionEntity:
    """Create sample transaction entity for testing."""
    return TransactionEntity(
        portfolio_id="portfolio-id-1",
        stock_id="stock-id-1",
        transaction_type=TransactionType("buy"),
        quantity=Quantity(100),
        price=Money(Decimal("150.50")),
        transaction_date=date(2024, 1, 15),
        notes=Notes("Test transaction"),
    )


class TestTransactionRepositoryCreate:
    """Test transaction creation operations."""

    def test_create_transaction_returns_id(
        self,
        transaction_repository: SqliteTransactionRepository,
        sample_transaction: TransactionEntity,
    ) -> None:
        """Should create transaction and return database ID."""
        # Act
        _ = transaction_id = transaction_repository.create(sample_transaction)

        # Assert
        assert isinstance(transaction_id, str)
        assert transaction_id

    def test_create_buy_transaction(
        self, transaction_repository: SqliteTransactionRepository
    ) -> None:
        """Should create buy transaction with all fields."""
        # Arrange
        buy_transaction = TransactionEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("buy"),
            quantity=Quantity(50),
            price=Money(Decimal("100.25")),
            transaction_date=date(2024, 2, 1),
            notes=Notes("Buy order"),
        )

        # Act
        _ = transaction_id = transaction_repository.create(buy_transaction)

        # Assert
        created_transaction = transaction_repository.get_by_id(transaction_id)
        assert created_transaction is not None
        assert created_transaction.transaction_type.value == "buy"
        assert created_transaction.quantity.value == 50
        assert created_transaction.price.amount == Decimal("100.25")
        assert created_transaction.notes.value == "Buy order"

    def test_create_sell_transaction(
        self, transaction_repository: SqliteTransactionRepository
    ) -> None:
        """Should create sell transaction."""
        # Arrange
        sell_transaction = TransactionEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("sell"),
            quantity=Quantity(25),
            price=Money(Decimal("105.75")),
            transaction_date=date(2024, 2, 15),
            notes=Notes("Sell order"),
        )

        # Act
        _ = transaction_id = transaction_repository.create(sell_transaction)

        # Assert
        created_transaction = transaction_repository.get_by_id(transaction_id)
        assert created_transaction is not None
        assert created_transaction.transaction_type.value == "sell"
        assert created_transaction.quantity.value == 25
        assert created_transaction.price.amount == Decimal("105.75")

    def test_create_transaction_minimal_data(
        self, transaction_repository: SqliteTransactionRepository
    ) -> None:
        """Should create transaction with minimal required data."""
        # Arrange
        minimal_transaction = TransactionEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("buy"),
            quantity=Quantity(10),
            price=Money(Decimal("50.00")),
            transaction_date=date.today(),
        )

        # Act
        _ = transaction_id = transaction_repository.create(minimal_transaction)

        # Assert
        assert transaction_id is not None
        created = transaction_repository.get_by_id(transaction_id)
        assert created is not None
        assert created.notes.value == ""


class TestTransactionRepositoryRead:
    """Test transaction read operations."""

    def test_get_by_id_existing_transaction(
        self,
        transaction_repository: SqliteTransactionRepository,
        sample_transaction: TransactionEntity,
    ) -> None:
        """Should retrieve transaction by ID."""
        # Arrange
        _ = transaction_id = transaction_repository.create(sample_transaction)

        # Act
        retrieved_transaction = transaction_repository.get_by_id(transaction_id)

        # Assert
        assert retrieved_transaction is not None
        assert retrieved_transaction.id == transaction_id
        assert retrieved_transaction.portfolio_id == sample_transaction.portfolio_id
        assert retrieved_transaction.stock_id == sample_transaction.stock_id
        assert (
            retrieved_transaction.transaction_type
            == sample_transaction.transaction_type
        )

    def test_get_by_id_nonexistent_transaction(
        self, transaction_repository: SqliteTransactionRepository
    ) -> None:
        """Should return None for non-existent transaction."""
        # Act
        result = transaction_repository.get_by_id("nonexistent-id")

        # Assert
        assert result is None

    def test_get_by_portfolio_empty(
        self, transaction_repository: SqliteTransactionRepository
    ) -> None:
        """Should return empty list when no transactions exist for portfolio."""
        # Act
        transactions = transaction_repository.get_by_portfolio("portfolio-id-1")

        # Assert
        assert transactions == []

    def test_get_by_portfolio_with_transactions(
        self, transaction_repository: SqliteTransactionRepository
    ) -> None:
        """Should return transactions for specific portfolio."""
        # Arrange
        transaction1 = TransactionEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("50.00")),
            transaction_date=date(2024, 1, 1),
        )
        transaction2 = TransactionEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("sell"),
            quantity=Quantity(50),
            price=Money(Decimal("55.00")),
            transaction_date=date(2024, 1, 15),
        )

        id1 = transaction_repository.create(transaction1)
        id2 = transaction_repository.create(transaction2)

        # Act
        portfolio_transactions = transaction_repository.get_by_portfolio(
            "portfolio-id-1"
        )

        # Assert
        assert len(portfolio_transactions) == 2
        transaction_ids = [t.id for t in portfolio_transactions]
        assert id1 in transaction_ids
        assert id2 in transaction_ids

    def test_get_by_portfolio_with_limit(
        self, transaction_repository: SqliteTransactionRepository
    ) -> None:
        """Should respect limit parameter for portfolio transactions."""
        # Arrange - create 5 transactions
        for i in range(5):
            transaction = TransactionEntity(
                portfolio_id="portfolio-id-1",
                stock_id="stock-id-1",
                transaction_type=TransactionType("buy"),
                quantity=Quantity(10),
                price=Money(Decimal("50.00")),
                transaction_date=date(2024, 1, i + 1),
            )
            _ = transaction_repository.create(transaction)

        # Act
        limited_transactions = transaction_repository.get_by_portfolio(
            "portfolio-id-1", limit=3
        )

        # Assert
        assert len(limited_transactions) == 3

    def test_get_by_stock(
        self, transaction_repository: SqliteTransactionRepository
    ) -> None:
        """Should return transactions for specific stock."""
        # Arrange
        transaction = TransactionEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("50.00")),
            transaction_date=date(2024, 1, 1),
        )
        _ = transaction_id = transaction_repository.create(transaction)

        # Act
        stock_transactions = transaction_repository.get_by_stock("stock-id-1")

        # Assert
        assert len(stock_transactions) == 1
        assert stock_transactions[0].id == transaction_id

    def test_get_by_stock_with_portfolio_filter(
        self, transaction_repository: SqliteTransactionRepository
    ) -> None:
        """Should filter stock transactions by portfolio."""
        # Arrange - create transaction for stock 1 in portfolio 1
        transaction = TransactionEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("50.00")),
            transaction_date=date(2024, 1, 1),
        )
        _ = transaction_id = transaction_repository.create(transaction)

        # Act
        filtered_transactions = transaction_repository.get_by_stock(
            "stock-id-1", portfolio_id="portfolio-id-1"
        )
        unfiltered_transactions = transaction_repository.get_by_stock(
            "stock-id-1", portfolio_id="stock-id-999"
        )

        # Assert
        assert len(filtered_transactions) == 1
        assert filtered_transactions[0].id == transaction_id
        assert len(unfiltered_transactions) == 0

    def test_get_by_date_range(
        self, transaction_repository: SqliteTransactionRepository
    ) -> None:
        """Should return transactions within date range."""
        # Arrange
        early_transaction = TransactionEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("50.00")),
            transaction_date=date(2024, 1, 1),
        )
        middle_transaction = TransactionEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("sell"),
            quantity=Quantity(50),
            price=Money(Decimal("55.00")),
            transaction_date=date(2024, 1, 15),
        )
        late_transaction = TransactionEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("buy"),
            quantity=Quantity(25),
            price=Money(Decimal("60.00")),
            transaction_date=date(2024, 2, 1),
        )

        early_id = transaction_repository.create(early_transaction)
        middle_id = transaction_repository.create(middle_transaction)
        late_id = transaction_repository.create(late_transaction)

        # Act
        january_transactions = transaction_repository.get_by_date_range(
            date(2024, 1, 1), date(2024, 1, 31)
        )

        # Assert
        assert len(january_transactions) == 2
        transaction_ids = [t.id for t in january_transactions]
        assert early_id in transaction_ids
        assert middle_id in transaction_ids
        assert late_id not in transaction_ids

    def test_get_by_date_range_with_portfolio_filter(
        self, transaction_repository: SqliteTransactionRepository
    ) -> None:
        """Should filter by date range and portfolio."""
        # Arrange
        # Create transactions for different portfolios
        portfolio1_transaction = TransactionEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("buy"),
            quantity=Quantity(50),
            price=Money(Decimal("100.00")),
            transaction_date=date(2024, 1, 15),
        )

        # Create second portfolio entry first
        with transaction_repository.db_connection.transaction() as conn:
            _ = conn.execute(
                """
                INSERT INTO portfolio (id, name, description, max_positions, max_risk_per_trade, is_active)
                VALUES ('portfolio-id-2', 'Test Portfolio 2', 'Second test portfolio', 50, 0.02, 1)
            """
            )

        portfolio2_transaction = TransactionEntity(
            portfolio_id="portfolio-id-2",
            stock_id="stock-id-1",
            transaction_type=TransactionType("buy"),
            quantity=Quantity(75),
            price=Money(Decimal("105.00")),
            transaction_date=date(2024, 1, 16),
        )

        portfolio1_id = transaction_repository.create(portfolio1_transaction)
        _ = transaction_repository.create(portfolio2_transaction)

        # Act
        portfolio1_transactions = transaction_repository.get_by_date_range(
            date(2024, 1, 1), date(2024, 1, 31), portfolio_id="portfolio-id-1"
        )

        # Assert
        assert len(portfolio1_transactions) == 1
        assert portfolio1_transactions[0].id == portfolio1_id
        assert portfolio1_transactions[0].portfolio_id == "portfolio-id-1"


class TestTransactionRepositoryUpdate:
    """Test transaction update operations."""

    def test_update_existing_transaction(
        self,
        transaction_repository: SqliteTransactionRepository,
        sample_transaction: TransactionEntity,
    ) -> None:
        """Should update existing transaction successfully."""
        # Arrange
        _ = transaction_id = transaction_repository.create(sample_transaction)
        updated_transaction = TransactionEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("sell"),
            quantity=Quantity(75),
            price=Money(Decimal("155.25")),
            transaction_date=date(2024, 1, 20),
            notes=Notes("Updated transaction"),
        )

        # Act
        result = transaction_repository.update(transaction_id, updated_transaction)

        # Assert
        assert result is True

        # Verify changes
        retrieved = transaction_repository.get_by_id(transaction_id)
        assert retrieved is not None
        assert retrieved.transaction_type.value == "sell"
        assert retrieved.quantity.value == 75
        assert retrieved.price.amount == Decimal("155.25")
        assert retrieved.notes.value == "Updated transaction"

    def test_update_nonexistent_transaction(
        self, transaction_repository: SqliteTransactionRepository
    ) -> None:
        """Should return False when updating non-existent transaction."""
        # Arrange
        transaction = TransactionEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("buy"),
            quantity=Quantity(10),
            price=Money(Decimal("50.00")),
            transaction_date=date.today(),
        )

        # Act
        result = transaction_repository.update("nonexistent-id", transaction)

        # Assert
        assert result is False


class TestTransactionRepositoryDelete:
    """Test transaction deletion operations."""

    def test_delete_existing_transaction(
        self,
        transaction_repository: SqliteTransactionRepository,
        sample_transaction: TransactionEntity,
    ) -> None:
        """Should delete existing transaction."""
        # Arrange
        _ = transaction_id = transaction_repository.create(sample_transaction)

        # Act
        result = transaction_repository.delete(transaction_id)

        # Assert
        assert result is True

        # Verify deletion
        retrieved = transaction_repository.get_by_id(transaction_id)
        assert retrieved is None

    def test_delete_nonexistent_transaction(
        self, transaction_repository: SqliteTransactionRepository
    ) -> None:
        """Should return False when deleting non-existent transaction."""
        # Act
        result = transaction_repository.delete("999")

        # Assert
        assert result is False


class TestTransactionRepositoryIntegration:
    """Integration tests for transaction repository operations."""

    def test_full_transaction_lifecycle(
        self, transaction_repository: SqliteTransactionRepository
    ) -> None:
        """Test complete CRUD operations in sequence."""
        # Create
        transaction = TransactionEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("buy"),
            quantity=Quantity(100),
            price=Money(Decimal("50.00")),
            transaction_date=date(2024, 1, 1),
            notes=Notes("Lifecycle test"),
        )
        _ = transaction_id = transaction_repository.create(transaction)
        assert transaction_id is not None

        # Read
        retrieved = transaction_repository.get_by_id(transaction_id)
        assert retrieved is not None
        assert retrieved.notes.value == "Lifecycle test"

        # Update
        updated_transaction = TransactionEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            transaction_type=TransactionType("sell"),
            quantity=Quantity(50),
            price=Money(Decimal("55.00")),
            transaction_date=date(2024, 1, 15),
            notes=Notes("Updated lifecycle test"),
        )
        update_result = transaction_repository.update(
            transaction_id, updated_transaction
        )
        assert update_result is True

        # Verify update
        updated_retrieved = transaction_repository.get_by_id(transaction_id)
        assert updated_retrieved is not None
        assert updated_retrieved.transaction_type.value == "sell"
        assert updated_retrieved.notes.value == "Updated lifecycle test"

        # Delete
        delete_result = transaction_repository.delete(transaction_id)
        assert delete_result is True

        # Verify deletion
        final_retrieved = transaction_repository.get_by_id(transaction_id)
        assert final_retrieved is None


class TestTransactionRepositoryErrorHandling:
    """Test error handling and edge cases."""

    def test_create_transaction_with_invalid_entity(
        self, transaction_repository: SqliteTransactionRepository
    ) -> None:
        """Should raise validation error for invalid transaction entity."""
        with pytest.raises(ValueError):
            invalid_transaction = TransactionEntity(
                portfolio_id="",  # Invalid portfolio ID
                stock_id="stock-id-1",
                transaction_type=TransactionType("buy"),
                quantity=Quantity(10),
                price=Money(Decimal("50.00")),
                transaction_date=date.today(),
            )
            _ = transaction_repository.create(invalid_transaction)

    def test_create_transaction_with_invalid_type(
        self, transaction_repository: SqliteTransactionRepository
    ) -> None:
        """Should raise validation error for invalid transaction type."""
        # Error now happens at TransactionType value object construction
        with pytest.raises(
            ValueError, match="Transaction type must be 'buy' or 'sell'"
        ):
            _ = TransactionType("invalid")  # Error happens at value object level
