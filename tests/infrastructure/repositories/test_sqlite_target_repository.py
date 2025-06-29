"""
Tests for SQLite Target Repository implementation.

Following TDD approach - defines expected behavior before implementation.
"""

import os
import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Iterator

import pytest

from src.domain.entities.target_entity import TargetEntity

# ITargetRepository import removed - unused
from src.domain.value_objects import Money, Notes, TargetStatus
from src.infrastructure.persistence.database_connection import DatabaseConnection
from src.infrastructure.repositories.sqlite_target_repository import (
    SqliteTargetRepository,
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
            VALUES ('portfolio-id-1', 'Test Portfolio', 'Test portfolio for targets', 50, 0.02, 1)
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
def target_repository(db_connection: DatabaseConnection) -> SqliteTargetRepository:
    """Create target repository with test database."""
    return SqliteTargetRepository(db_connection)


@pytest.fixture
def sample_target() -> TargetEntity:
    """Create sample target entity for testing."""
    return TargetEntity(
        portfolio_id="portfolio-id-1",
        stock_id="stock-id-1",
        pivot_price=Money(Decimal("150.00")),
        failure_price=Money(Decimal("140.00")),
        status=TargetStatus("active"),
        created_date=date(2024, 1, 1),
        notes=Notes("Test target"),
    )


class TestTargetRepositoryCreate:
    """Test target creation operations."""

    def test_create_target_returns_id(
        self, target_repository: SqliteTargetRepository, sample_target: TargetEntity
    ) -> None:
        """Should create target and return database ID."""
        # Act
        _ = target_id = target_repository.create(sample_target)

        # Assert
        assert isinstance(target_id, str)
        assert target_id

    def test_create_active_target(
        self, target_repository: SqliteTargetRepository
    ) -> None:
        """Should create active target with all fields."""
        # Arrange
        active_target = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("95.00")),
            status=TargetStatus("active"),
            created_date=date(2024, 1, 1),
            notes=Notes("Active target test"),
        )

        # Act
        _ = target_id = target_repository.create(active_target)

        # Assert
        created_target = target_repository.get_by_id(target_id)
        assert created_target is not None
        assert created_target.status.value == "active"
        assert created_target.pivot_price.amount == Decimal("100.00")
        assert created_target.failure_price.amount == Decimal("95.00")
        assert created_target.notes.value == "Active target test"

    def test_create_target_minimal_data(
        self, target_repository: SqliteTargetRepository
    ) -> None:
        """Should create target with minimal required data."""
        # Arrange
        minimal_target = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("50.00")),
            failure_price=Money(Decimal("45.00")),
            status=TargetStatus("active"),
            created_date=date(2024, 1, 1),
        )

        # Act
        _ = target_id = target_repository.create(minimal_target)

        # Assert
        assert target_id is not None
        created = target_repository.get_by_id(target_id)
        assert created is not None
        assert created.notes.value == ""


class TestTargetRepositoryRead:
    """Test target read operations."""

    def test_get_by_id_existing_target(
        self, target_repository: SqliteTargetRepository, sample_target: TargetEntity
    ) -> None:
        """Should retrieve target by ID."""
        # Arrange
        _ = target_id = target_repository.create(sample_target)

        # Act
        retrieved_target = target_repository.get_by_id(target_id)

        # Assert
        assert retrieved_target is not None
        assert retrieved_target.id == target_id
        assert retrieved_target.portfolio_id == sample_target.portfolio_id
        assert retrieved_target.stock_id == sample_target.stock_id
        assert retrieved_target.status.value == sample_target.status.value

    def test_get_by_id_nonexistent_target(
        self, target_repository: SqliteTargetRepository
    ) -> None:
        """Should return None for non-existent target."""
        # Act
        result = target_repository.get_by_id("nonexistent-id")

        # Assert
        assert result is None

    def test_get_active_by_portfolio_empty(
        self, target_repository: SqliteTargetRepository
    ) -> None:
        """Should return empty list when no active targets exist for portfolio."""
        # Act
        targets = target_repository.get_active_by_portfolio("portfolio-id-1")

        # Assert
        assert targets == []

    def test_get_active_by_portfolio_with_targets(
        self, target_repository: SqliteTargetRepository
    ) -> None:
        """Should return only active targets for specific portfolio."""
        # Arrange
        active_target = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("95.00")),
            status=TargetStatus("active"),
            created_date=date(2024, 1, 1),
        )
        inactive_target = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("105.00")),
            failure_price=Money(Decimal("98.00")),
            status=TargetStatus("hit"),
            created_date=date(2024, 1, 1),
        )

        _ = active_id = target_repository.create(active_target)
        _ = target_repository.create(inactive_target)

        # Act
        active_targets = target_repository.get_active_by_portfolio("portfolio-id-1")

        # Assert
        assert len(active_targets) == 1
        assert active_targets[0].id == active_id
        assert active_targets[0].status.value == "active"

    def test_get_active_by_stock(
        self, target_repository: SqliteTargetRepository
    ) -> None:
        """Should return active targets for specific stock."""
        # Arrange
        target = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("95.00")),
            status=TargetStatus("active"),
            created_date=date(2024, 1, 1),
        )
        _ = target_id = target_repository.create(target)

        # Act
        stock_targets = target_repository.get_active_by_stock("stock-id-1")

        # Assert
        assert len(stock_targets) == 1
        assert stock_targets[0].id == target_id

    def test_get_all_active(self, target_repository: SqliteTargetRepository) -> None:
        """Should return all active targets across portfolios."""
        # Arrange
        target1 = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("95.00")),
            status=TargetStatus("active"),
            created_date=date.today(),
        )
        target2 = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("110.00")),
            failure_price=Money(Decimal("105.00")),
            status=TargetStatus("failed"),
            created_date=date.today(),
        )

        _ = active_id = target_repository.create(target1)
        _ = target_repository.create(target2)

        # Act
        all_active = target_repository.get_all_active()

        # Assert
        assert len(all_active) == 1
        assert all_active[0].id == active_id


class TestTargetRepositoryUpdate:
    """Test target update operations."""

    def test_update_existing_target(
        self, target_repository: SqliteTargetRepository, sample_target: TargetEntity
    ) -> None:
        """Should update existing target successfully."""
        # Arrange
        _ = target_id = target_repository.create(sample_target)
        updated_target = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("160.00")),
            failure_price=Money(Decimal("145.00")),
            status=TargetStatus("hit"),
            created_date=date.today(),
            notes=Notes("Updated target"),
        )

        # Act
        result = target_repository.update(target_id, updated_target)

        # Assert
        assert result is True

        # Verify changes
        retrieved = target_repository.get_by_id(target_id)
        assert retrieved is not None
        assert retrieved.pivot_price.amount == Decimal("160.00")
        assert retrieved.failure_price.amount == Decimal("145.00")
        assert retrieved.status.value == "hit"
        assert retrieved.notes.value == "Updated target"

    def test_update_nonexistent_target(
        self, target_repository: SqliteTargetRepository
    ) -> None:
        """Should return False when updating non-existent target."""
        # Arrange
        target = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("95.00")),
            status=TargetStatus("active"),
            created_date=date(2024, 1, 1),
        )

        # Act
        result = target_repository.update("nonexistent-id", target)

        # Assert
        assert result is False

    def test_update_status(
        self, target_repository: SqliteTargetRepository, sample_target: TargetEntity
    ) -> None:
        """Should update target status."""
        # Arrange
        _ = target_id = target_repository.create(sample_target)

        # Act
        result = target_repository.update_status(target_id, "hit")

        # Assert
        assert result is True

        # Verify status change
        retrieved = target_repository.get_by_id(target_id)
        assert retrieved is not None
        assert retrieved.status.value == "hit"

    def test_update_status_nonexistent_target(
        self, target_repository: SqliteTargetRepository
    ) -> None:
        """Should return False when updating status of non-existent target."""
        # Act
        result = target_repository.update_status("nonexistent-id", "hit")

        # Assert
        assert result is False


class TestTargetRepositoryIntegration:
    """Integration tests for target repository operations."""

    def test_full_target_lifecycle(
        self, target_repository: SqliteTargetRepository
    ) -> None:
        """Test complete CRUD operations in sequence."""
        # Create
        target = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("100.00")),
            failure_price=Money(Decimal("95.00")),
            status=TargetStatus("active"),
            created_date=date(2024, 1, 1),
            notes=Notes("Lifecycle test"),
        )
        _ = target_id = target_repository.create(target)
        assert target_id is not None

        # Read
        retrieved = target_repository.get_by_id(target_id)
        assert retrieved is not None
        assert retrieved.notes.value == "Lifecycle test"

        # Update
        updated_target = TargetEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            pivot_price=Money(Decimal("105.00")),
            failure_price=Money(Decimal("98.00")),
            status=TargetStatus("hit"),
            created_date=date(2024, 1, 1),
            notes=Notes("Updated lifecycle test"),
        )
        update_result = target_repository.update(target_id, updated_target)
        assert update_result is True

        # Verify update
        updated_retrieved = target_repository.get_by_id(target_id)
        assert updated_retrieved is not None
        assert updated_retrieved.status.value == "hit"
        assert updated_retrieved.notes.value == "Updated lifecycle test"

        # Update status
        status_result = target_repository.update_status(target_id, "cancelled")
        assert status_result is True

        # Verify status update
        final_retrieved = target_repository.get_by_id(target_id)
        assert final_retrieved is not None
        assert final_retrieved.status.value == "cancelled"

    def test_multiple_targets_filtering(
        self, target_repository: SqliteTargetRepository
    ) -> None:
        """Test filtering behavior with multiple targets."""
        # Create targets with different statuses
        targets = [
            TargetEntity(
                portfolio_id="portfolio-id-1",
                stock_id="stock-id-1",
                pivot_price=Money(Decimal("100.00")),
                failure_price=Money(Decimal("95.00")),
                status=TargetStatus("active"),
                created_date=date(2024, 1, 1),
            ),
            TargetEntity(
                portfolio_id="portfolio-id-1",
                stock_id="stock-id-1",
                pivot_price=Money(Decimal("110.00")),
                failure_price=Money(Decimal("105.00")),
                status=TargetStatus("hit"),
                created_date=date(2024, 1, 1),
            ),
            TargetEntity(
                portfolio_id="portfolio-id-1",
                stock_id="stock-id-1",
                pivot_price=Money(Decimal("120.00")),
                failure_price=Money(Decimal("115.00")),
                status=TargetStatus("active"),
                created_date=date(2024, 1, 1),
            ),
        ]

        for target in targets:
            _ = target_repository.create(target)

        # Test get_active_by_portfolio
        active_targets = target_repository.get_active_by_portfolio("portfolio-id-1")
        assert len(active_targets) == 2

        # Test get_all_active
        all_active = target_repository.get_all_active()
        assert len(all_active) == 2


class TestTargetRepositoryDateParsing:
    """Test date parsing edge cases in _row_to_entity method."""

    def setup_method(self) -> None:
        """Set up test database and repository."""
        # Create temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()

        # Initialize database connection and repository
        self.db_connection = DatabaseConnection(self.temp_db.name)
        self.db_connection.initialize_schema()

        self.repository = SqliteTargetRepository(self.db_connection)

        # Create test portfolio and stock
        with self.db_connection.transaction() as conn:
            _ = conn.execute(
                """
                INSERT INTO portfolio (id, name, description, max_positions, max_risk_per_trade, is_active)
                VALUES ('portfolio-id-1', 'Test Portfolio', 'Test portfolio for targets', 50, 0.02, 1)
            """
            )
            _ = conn.execute(
                """
                INSERT INTO stock (id, symbol, name, industry_group, grade, notes)
                VALUES ('stock-id-1', 'AAPL', 'Apple Inc.', 'Technology', 'A', 'Test stock')
            """
            )

    def teardown_method(self) -> None:
        """Clean up test database."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_row_to_entity_handles_invalid_date_format(self) -> None:
        """Should use today's date when created_at parsing fails."""
        from unittest.mock import patch

        # Arrange
        # Create a mock row with invalid date format that would cause parsing to fail
        mock_row = {
            "id": "test-id",
            "created_at": "invalid-date-format",  # This will cause parsing to fail
            "portfolio_id": "portfolio-1",
            "stock_id": "stock-1",
            "pivot_price": "100.00",
            "failure_price": "95.00",
            "target_price": "110.00",
            "status": "active",
            "notes": "Test notes",
        }

        # Mock date.today() to return a predictable date
        expected_date = date(2024, 6, 23)
        with patch(
            "src.infrastructure.repositories.sqlite_target_repository.date"
        ) as mock_date:
            mock_date.today.return_value = expected_date

            # Act
            entity = self.repository._row_to_entity(mock_row)  # type: ignore[attr-defined,arg-type]

            # Assert
            assert entity.created_date == expected_date
            mock_date.today.assert_called_once()


class TestTargetRepositoryErrorHandling:
    """Test error handling and edge cases."""

    def test_create_target_with_invalid_entity(
        self, target_repository: SqliteTargetRepository
    ) -> None:
        """Should raise validation error for invalid target entity."""
        with pytest.raises(ValueError):
            invalid_target = TargetEntity(
                portfolio_id="",  # Invalid portfolio ID
                stock_id="stock-id-1",
                pivot_price=Money(Decimal("100.00")),
                failure_price=Money(Decimal("95.00")),
                status=TargetStatus("active"),
                created_date=date(2024, 1, 1),
            )
            _ = target_repository.create(invalid_target)

    def test_create_target_with_invalid_status(
        self, target_repository: SqliteTargetRepository
    ) -> None:
        """Should raise validation error for invalid status."""
        with pytest.raises(ValueError):
            invalid_target = TargetEntity(
                portfolio_id="portfolio-id-1",
                stock_id="stock-id-1",
                pivot_price=Money(Decimal("100.00")),
                failure_price=Money(Decimal("95.00")),
                status=TargetStatus("invalid_status"),  # Invalid status
                created_date=date(2024, 1, 1),
            )
            _ = target_repository.create(invalid_target)
