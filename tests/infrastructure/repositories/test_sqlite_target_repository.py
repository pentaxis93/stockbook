"""
Tests for SQLite Target Repository implementation.

Following TDD approach - defines expected behavior before implementation.
"""

import os
import tempfile
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from shared_kernel.value_objects import Money
from src.domain.entities.target_entity import TargetEntity
from src.domain.repositories.interfaces import ITargetRepository
from src.domain.value_objects import Notes, TargetStatus
from src.infrastructure.persistence.database_connection import DatabaseConnection
from src.infrastructure.repositories.sqlite_target_repository import (
    SqliteTargetRepository,
)


@pytest.fixture
def db_connection():
    """Create temporary database for testing."""
    # Create temporary database file
    temp_fd, temp_path = tempfile.mkstemp(suffix=".db")
    os.close(temp_fd)

    connection = DatabaseConnection(temp_path)
    connection.initialize_schema()

    # Create test portfolios and stocks
    with connection.transaction() as conn:
        # Create test portfolio
        conn.execute(
            """
            INSERT INTO portfolio (id, name, description, max_positions, max_risk_per_trade, is_active)
            VALUES (1, 'Test Portfolio', 'Test portfolio for targets', 50, 0.02, 1)
        """
        )

        # Create test stock
        conn.execute(
            """
            INSERT INTO stock (id, symbol, name, industry_group, grade, notes)
            VALUES (1, 'AAPL', 'Apple Inc.', 'Technology', 'A', 'Test stock')
        """
        )

    yield connection

    # Cleanup
    connection.close()
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def target_repository(db_connection):
    """Create target repository with test database."""
    return SqliteTargetRepository(db_connection)


@pytest.fixture
def sample_target():
    """Create sample target entity for testing."""
    return TargetEntity(
        portfolio_id=1,
        stock_id=1,
        pivot_price=Money(Decimal("150.00"), "USD"),
        failure_price=Money(Decimal("140.00"), "USD"),
        status=TargetStatus("active"),
        created_date=date(2024, 1, 1),
        notes=Notes("Test target"),
    )


class TestTargetRepositoryCreate:
    """Test target creation operations."""

    def test_create_target_returns_id(self, target_repository, sample_target):
        """Should create target and return database ID."""
        # Act
        target_id = target_repository.create(sample_target)

        # Assert
        assert isinstance(target_id, int)
        assert target_id > 0

    def test_create_active_target(self, target_repository):
        """Should create active target with all fields."""
        # Arrange
        active_target = TargetEntity(
            portfolio_id=1,
            stock_id=1,
            pivot_price=Money(Decimal("100.00"), "USD"),
            failure_price=Money(Decimal("95.00"), "USD"),
            status=TargetStatus("active"),
            created_date=date(2024, 1, 1),
            notes=Notes("Active target test"),
        )

        # Act
        target_id = target_repository.create(active_target)

        # Assert
        created_target = target_repository.get_by_id(target_id)
        assert created_target.status.value == "active"
        assert created_target.pivot_price.amount == Decimal("100.00")
        assert created_target.failure_price.amount == Decimal("95.00")
        assert created_target.notes.value == "Active target test"

    def test_create_target_minimal_data(self, target_repository):
        """Should create target with minimal required data."""
        # Arrange
        minimal_target = TargetEntity(
            portfolio_id=1,
            stock_id=1,
            pivot_price=Money(Decimal("50.00"), "USD"),
            failure_price=Money(Decimal("45.00"), "USD"),
            status=TargetStatus("active"),
            created_date=date(2024, 1, 1),
        )

        # Act
        target_id = target_repository.create(minimal_target)

        # Assert
        assert target_id is not None
        created = target_repository.get_by_id(target_id)
        assert created.notes.value == ""


class TestTargetRepositoryRead:
    """Test target read operations."""

    def test_get_by_id_existing_target(self, target_repository, sample_target):
        """Should retrieve target by ID."""
        # Arrange
        target_id = target_repository.create(sample_target)

        # Act
        retrieved_target = target_repository.get_by_id(target_id)

        # Assert
        assert retrieved_target is not None
        assert retrieved_target.id == target_id
        assert retrieved_target.portfolio_id == sample_target.portfolio_id
        assert retrieved_target.stock_id == sample_target.stock_id
        assert retrieved_target.status.value == sample_target.status.value

    def test_get_by_id_nonexistent_target(self, target_repository):
        """Should return None for non-existent target."""
        # Act
        result = target_repository.get_by_id(999)

        # Assert
        assert result is None

    def test_get_active_by_portfolio_empty(self, target_repository):
        """Should return empty list when no active targets exist for portfolio."""
        # Act
        targets = target_repository.get_active_by_portfolio(1)

        # Assert
        assert targets == []

    def test_get_active_by_portfolio_with_targets(self, target_repository):
        """Should return only active targets for specific portfolio."""
        # Arrange
        active_target = TargetEntity(
            portfolio_id=1,
            stock_id=1,
            pivot_price=Money(Decimal("100.00"), "USD"),
            failure_price=Money(Decimal("95.00"), "USD"),
            status=TargetStatus("active"),
            created_date=date(2024, 1, 1),
        )
        inactive_target = TargetEntity(
            portfolio_id=1,
            stock_id=1,
            pivot_price=Money(Decimal("105.00"), "USD"),
            failure_price=Money(Decimal("98.00"), "USD"),
            status=TargetStatus("hit"),
            created_date=date(2024, 1, 1),
        )

        active_id = target_repository.create(active_target)
        target_repository.create(inactive_target)

        # Act
        active_targets = target_repository.get_active_by_portfolio(1)

        # Assert
        assert len(active_targets) == 1
        assert active_targets[0].id == active_id
        assert active_targets[0].status.value == "active"

    def test_get_active_by_stock(self, target_repository):
        """Should return active targets for specific stock."""
        # Arrange
        target = TargetEntity(
            portfolio_id=1,
            stock_id=1,
            pivot_price=Money(Decimal("100.00"), "USD"),
            failure_price=Money(Decimal("95.00"), "USD"),
            status=TargetStatus("active"),
            created_date=date(2024, 1, 1),
        )
        target_id = target_repository.create(target)

        # Act
        stock_targets = target_repository.get_active_by_stock(1)

        # Assert
        assert len(stock_targets) == 1
        assert stock_targets[0].id == target_id

    def test_get_all_active(self, target_repository):
        """Should return all active targets across portfolios."""
        # Arrange
        target1 = TargetEntity(
            portfolio_id=1,
            stock_id=1,
            pivot_price=Money(Decimal("100.00"), "USD"),
            failure_price=Money(Decimal("95.00"), "USD"),
            status=TargetStatus("active"),
            created_date=date.today(),
        )
        target2 = TargetEntity(
            portfolio_id=1,
            stock_id=1,
            pivot_price=Money(Decimal("110.00"), "USD"),
            failure_price=Money(Decimal("105.00"), "USD"),
            status=TargetStatus("failed"),
            created_date=date.today(),
        )

        active_id = target_repository.create(target1)
        target_repository.create(target2)

        # Act
        all_active = target_repository.get_all_active()

        # Assert
        assert len(all_active) == 1
        assert all_active[0].id == active_id


class TestTargetRepositoryUpdate:
    """Test target update operations."""

    def test_update_existing_target(self, target_repository, sample_target):
        """Should update existing target successfully."""
        # Arrange
        target_id = target_repository.create(sample_target)
        updated_target = TargetEntity(
            portfolio_id=1,
            stock_id=1,
            pivot_price=Money(Decimal("160.00"), "USD"),
            failure_price=Money(Decimal("145.00"), "USD"),
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
        assert retrieved.pivot_price.amount == Decimal("160.00")
        assert retrieved.failure_price.amount == Decimal("145.00")
        assert retrieved.status.value == "hit"
        assert retrieved.notes.value == "Updated target"

    def test_update_nonexistent_target(self, target_repository):
        """Should return False when updating non-existent target."""
        # Arrange
        target = TargetEntity(
            portfolio_id=1,
            stock_id=1,
            pivot_price=Money(Decimal("100.00"), "USD"),
            failure_price=Money(Decimal("95.00"), "USD"),
            status=TargetStatus("active"),
            created_date=date(2024, 1, 1),
        )

        # Act
        result = target_repository.update(999, target)

        # Assert
        assert result is False

    def test_update_status(self, target_repository, sample_target):
        """Should update target status."""
        # Arrange
        target_id = target_repository.create(sample_target)

        # Act
        result = target_repository.update_status(target_id, "hit")

        # Assert
        assert result is True

        # Verify status change
        retrieved = target_repository.get_by_id(target_id)
        assert retrieved.status.value == "hit"

    def test_update_status_nonexistent_target(self, target_repository):
        """Should return False when updating status of non-existent target."""
        # Act
        result = target_repository.update_status(999, "hit")

        # Assert
        assert result is False


class TestTargetRepositoryIntegration:
    """Integration tests for target repository operations."""

    def test_full_target_lifecycle(self, target_repository):
        """Test complete CRUD operations in sequence."""
        # Create
        target = TargetEntity(
            portfolio_id=1,
            stock_id=1,
            pivot_price=Money(Decimal("100.00"), "USD"),
            failure_price=Money(Decimal("95.00"), "USD"),
            status=TargetStatus("active"),
            created_date=date(2024, 1, 1),
            notes=Notes("Lifecycle test"),
        )
        target_id = target_repository.create(target)
        assert target_id is not None

        # Read
        retrieved = target_repository.get_by_id(target_id)
        assert retrieved.notes.value == "Lifecycle test"

        # Update
        updated_target = TargetEntity(
            portfolio_id=1,
            stock_id=1,
            pivot_price=Money(Decimal("105.00"), "USD"),
            failure_price=Money(Decimal("98.00"), "USD"),
            status=TargetStatus("hit"),
            created_date=date(2024, 1, 1),
            notes=Notes("Updated lifecycle test"),
        )
        update_result = target_repository.update(target_id, updated_target)
        assert update_result is True

        # Verify update
        updated_retrieved = target_repository.get_by_id(target_id)
        assert updated_retrieved.status.value == "hit"
        assert updated_retrieved.notes.value == "Updated lifecycle test"

        # Update status
        status_result = target_repository.update_status(target_id, "cancelled")
        assert status_result is True

        # Verify status update
        final_retrieved = target_repository.get_by_id(target_id)
        assert final_retrieved.status.value == "cancelled"

    def test_multiple_targets_filtering(self, target_repository):
        """Test filtering behavior with multiple targets."""
        # Create targets with different statuses
        targets = [
            TargetEntity(
                portfolio_id=1,
                stock_id=1,
                pivot_price=Money(Decimal("100.00"), "USD"),
                failure_price=Money(Decimal("95.00"), "USD"),
                status=TargetStatus("active"),
                created_date=date(2024, 1, 1),
            ),
            TargetEntity(
                portfolio_id=1,
                stock_id=1,
                pivot_price=Money(Decimal("110.00"), "USD"),
                failure_price=Money(Decimal("105.00"), "USD"),
                status=TargetStatus("hit"),
                created_date=date(2024, 1, 1),
            ),
            TargetEntity(
                portfolio_id=1,
                stock_id=1,
                pivot_price=Money(Decimal("120.00"), "USD"),
                failure_price=Money(Decimal("115.00"), "USD"),
                status=TargetStatus("active"),
                created_date=date(2024, 1, 1),
            ),
        ]

        for target in targets:
            target_repository.create(target)

        # Test get_active_by_portfolio
        active_targets = target_repository.get_active_by_portfolio(1)
        assert len(active_targets) == 2

        # Test get_all_active
        all_active = target_repository.get_all_active()
        assert len(all_active) == 2


class TestTargetRepositoryErrorHandling:
    """Test error handling and edge cases."""

    def test_create_target_with_invalid_entity(self, target_repository):
        """Should raise validation error for invalid target entity."""
        with pytest.raises(ValueError):
            invalid_target = TargetEntity(
                portfolio_id=0,  # Invalid portfolio ID
                stock_id=1,
                pivot_price=Money(Decimal("100.00"), "USD"),
                failure_price=Money(Decimal("95.00"), "USD"),
                status=TargetStatus("active"),
                created_date=date(2024, 1, 1),
            )
            target_repository.create(invalid_target)

    def test_create_target_with_invalid_status(self, target_repository):
        """Should raise validation error for invalid status."""
        with pytest.raises(ValueError):
            invalid_target = TargetEntity(
                portfolio_id=1,
                stock_id=1,
                pivot_price=Money(Decimal("100.00"), "USD"),
                failure_price=Money(Decimal("95.00"), "USD"),
                status=TargetStatus("invalid_status"),  # Invalid status
                created_date=date(2024, 1, 1),
            )
            target_repository.create(invalid_target)
