"""
Tests for SQLite Portfolio Repository implementation.

Following TDD approach - defines expected behavior before implementation.
"""

import os
import tempfile
from datetime import date
from pathlib import Path
from typing import Iterator

import pytest

from src.domain.entities.portfolio_entity import PortfolioEntity

# IPortfolioRepository import removed - unused
from src.domain.value_objects import Notes, PortfolioName
from src.infrastructure.persistence.database_connection import DatabaseConnection
from src.infrastructure.repositories.sqlite_portfolio_repository import (
    SqlitePortfolioRepository,
)


@pytest.fixture
def db_connection() -> Iterator[DatabaseConnection]:
    """Create temporary database for testing."""
    # Create temporary database file
    temp_fd, temp_path = tempfile.mkstemp(suffix=".db")
    os.close(temp_fd)

    connection = DatabaseConnection(temp_path)
    connection.initialize_schema()

    yield connection

    # Cleanup
    connection.close()
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def portfolio_repository(
    db_connection: DatabaseConnection,
) -> SqlitePortfolioRepository:
    """Create portfolio repository with test database."""
    return SqlitePortfolioRepository(db_connection)


@pytest.fixture
def sample_portfolio() -> PortfolioEntity:
    """Create sample portfolio entity for testing."""
    return PortfolioEntity(
        name=PortfolioName("Test Portfolio"),
        description=Notes("A test portfolio for unit testing"),
        created_date=date(2024, 1, 15),
        is_active=True,
    )


class TestPortfolioRepositoryCreate:
    """Test portfolio creation operations."""

    def test_create_portfolio_returns_id(
        self,
        portfolio_repository: SqlitePortfolioRepository,
        sample_portfolio: PortfolioEntity,
    ) -> None:
        """Should create portfolio and return database ID."""
        # Act
        portfolio_id = portfolio_repository.create(sample_portfolio)

        # Assert
        assert isinstance(portfolio_id, str)
        assert portfolio_id

    def test_create_portfolio_with_minimal_data(
        self, portfolio_repository: SqlitePortfolioRepository
    ) -> None:
        """Should create portfolio with only required fields."""
        # Arrange
        minimal_portfolio = PortfolioEntity(name=PortfolioName("Minimal Portfolio"))

        # Act
        portfolio_id = portfolio_repository.create(minimal_portfolio)

        # Assert
        assert portfolio_id is not None

        # Verify in database
        created_portfolio = portfolio_repository.get_by_id(portfolio_id)
        assert created_portfolio is not None
        assert created_portfolio.name.value == "Minimal Portfolio"
        assert created_portfolio.is_active is True

    def test_create_portfolio_with_all_fields(
        self,
        portfolio_repository: SqlitePortfolioRepository,
        sample_portfolio: PortfolioEntity,
    ) -> None:
        """Should create portfolio with all fields populated."""
        # Act
        portfolio_id = portfolio_repository.create(sample_portfolio)

        # Assert
        created_portfolio = portfolio_repository.get_by_id(portfolio_id)
        assert created_portfolio is not None
        assert created_portfolio.name == sample_portfolio.name
        assert created_portfolio.description == sample_portfolio.description
        assert (
            created_portfolio.created_date is not None
        )  # Database sets this automatically
        assert created_portfolio.is_active == sample_portfolio.is_active

    def test_create_duplicate_portfolio_name_allowed(
        self, portfolio_repository: SqlitePortfolioRepository
    ) -> None:
        """Should allow duplicate portfolio names (no unique constraint)."""
        # Arrange
        portfolio1 = PortfolioEntity(name=PortfolioName("Duplicate Name"))
        portfolio2 = PortfolioEntity(name=PortfolioName("Duplicate Name"))

        # Act
        id1 = portfolio_repository.create(portfolio1)
        id2 = portfolio_repository.create(portfolio2)

        # Assert
        assert id1 != id2
        portfolio1_retrieved = portfolio_repository.get_by_id(id1)
        portfolio2_retrieved = portfolio_repository.get_by_id(id2)
        assert portfolio1_retrieved is not None
        assert portfolio2_retrieved is not None
        assert portfolio1_retrieved.name.value == "Duplicate Name"
        assert portfolio2_retrieved.name.value == "Duplicate Name"


class TestPortfolioRepositoryRead:
    """Test portfolio read operations."""

    def test_get_by_id_existing_portfolio(
        self,
        portfolio_repository: SqlitePortfolioRepository,
        sample_portfolio: PortfolioEntity,
    ) -> None:
        """Should retrieve portfolio by ID."""
        # Arrange
        portfolio_id = portfolio_repository.create(sample_portfolio)

        # Act
        retrieved_portfolio = portfolio_repository.get_by_id(portfolio_id)

        # Assert
        assert retrieved_portfolio is not None
        assert retrieved_portfolio.id == portfolio_id
        assert retrieved_portfolio.name == sample_portfolio.name

    def test_get_by_id_nonexistent_portfolio(
        self, portfolio_repository: SqlitePortfolioRepository
    ) -> None:
        """Should return None for non-existent portfolio."""
        # Act
        result = portfolio_repository.get_by_id("nonexistent-id")

        # Assert
        assert result is None

    def test_get_all_active_empty_database(
        self, portfolio_repository: SqlitePortfolioRepository
    ) -> None:
        """Should return empty list when no active portfolios exist."""
        # Act
        portfolios = portfolio_repository.get_all_active()

        # Assert
        assert portfolios == []

    def test_get_all_active_with_active_portfolios(
        self, portfolio_repository: SqlitePortfolioRepository
    ) -> None:
        """Should return only active portfolios."""
        # Arrange
        active_portfolio = PortfolioEntity(
            name=PortfolioName("Active Portfolio"), is_active=True
        )
        inactive_portfolio = PortfolioEntity(
            name=PortfolioName("Inactive Portfolio"), is_active=False
        )

        active_id = portfolio_repository.create(active_portfolio)
        _ = portfolio_repository.create(inactive_portfolio)

        # Act
        active_portfolios = portfolio_repository.get_all_active()

        # Assert
        assert len(active_portfolios) == 1
        assert active_portfolios[0].id == active_id
        assert active_portfolios[0].name.value == "Active Portfolio"

    def test_get_all_portfolios(
        self, portfolio_repository: SqlitePortfolioRepository
    ) -> None:
        """Should return all portfolios regardless of active status."""
        # Arrange
        active_portfolio = PortfolioEntity(
            name=PortfolioName("Active Portfolio"), is_active=True
        )
        inactive_portfolio = PortfolioEntity(
            name=PortfolioName("Inactive Portfolio"), is_active=False
        )

        _ = portfolio_repository.create(active_portfolio)
        _ = portfolio_repository.create(inactive_portfolio)

        # Act
        all_portfolios = portfolio_repository.get_all()

        # Assert
        assert len(all_portfolios) == 2
        portfolio_names = [p.name.value for p in all_portfolios]
        assert "Active Portfolio" in portfolio_names
        assert "Inactive Portfolio" in portfolio_names


class TestPortfolioRepositoryUpdate:
    """Test portfolio update operations."""

    def test_update_existing_portfolio(
        self,
        portfolio_repository: SqlitePortfolioRepository,
        sample_portfolio: PortfolioEntity,
    ) -> None:
        """Should update existing portfolio successfully."""
        # Arrange
        portfolio_id = portfolio_repository.create(sample_portfolio)
        updated_portfolio = PortfolioEntity(
            name=PortfolioName("Updated Portfolio Name"),
            description=Notes("Updated description"),
            is_active=False,
        )

        # Act
        result = portfolio_repository.update(portfolio_id, updated_portfolio)

        # Assert
        assert result is True

        # Verify changes
        retrieved = portfolio_repository.get_by_id(portfolio_id)
        assert retrieved is not None
        assert retrieved.name.value == "Updated Portfolio Name"
        assert retrieved.description.value == "Updated description"
        assert retrieved.is_active is False

    def test_update_nonexistent_portfolio(
        self, portfolio_repository: SqlitePortfolioRepository
    ) -> None:
        """Should return False when updating non-existent portfolio."""
        # Arrange
        portfolio = PortfolioEntity(name=PortfolioName("Non-existent"))

        # Act
        result = portfolio_repository.update("nonexistent-id", portfolio)

        # Assert
        assert result is False

    def test_partial_update_portfolio(
        self,
        portfolio_repository: SqlitePortfolioRepository,
        sample_portfolio: PortfolioEntity,
    ) -> None:
        """Should update only specified fields."""
        # Arrange
        portfolio_id = portfolio_repository.create(sample_portfolio)
        partial_update = PortfolioEntity(
            name=PortfolioName("Partially Updated"),
            description=sample_portfolio.description,  # Keep original
            is_active=sample_portfolio.is_active,  # Keep original
        )

        # Act
        _ = portfolio_repository.update(portfolio_id, partial_update)

        # Assert
        retrieved = portfolio_repository.get_by_id(portfolio_id)
        assert retrieved is not None
        assert retrieved.name.value == "Partially Updated"
        assert retrieved.description == sample_portfolio.description
        assert retrieved.is_active == sample_portfolio.is_active


class TestPortfolioRepositoryDeactivate:
    """Test portfolio deactivation (soft delete) operations."""

    def test_deactivate_existing_portfolio(
        self,
        portfolio_repository: SqlitePortfolioRepository,
        sample_portfolio: PortfolioEntity,
    ) -> None:
        """Should deactivate existing portfolio."""
        # Arrange
        portfolio_id = portfolio_repository.create(sample_portfolio)

        # Act
        result = portfolio_repository.deactivate(portfolio_id)

        # Assert
        assert result is True

        # Verify deactivation
        retrieved = portfolio_repository.get_by_id(portfolio_id)
        assert retrieved is not None
        assert retrieved.is_active is False

    def test_deactivate_nonexistent_portfolio(
        self, portfolio_repository: SqlitePortfolioRepository
    ) -> None:
        """Should return False when deactivating non-existent portfolio."""
        # Act
        result = portfolio_repository.deactivate("nonexistent-id")

        # Assert
        assert result is False

    def test_deactivate_already_inactive_portfolio(
        self, portfolio_repository: SqlitePortfolioRepository
    ) -> None:
        """Should handle deactivating already inactive portfolio."""
        # Arrange
        inactive_portfolio = PortfolioEntity(
            name=PortfolioName("Already Inactive"), is_active=False
        )
        portfolio_id = portfolio_repository.create(inactive_portfolio)

        # Act
        result = portfolio_repository.deactivate(portfolio_id)

        # Assert
        assert result is True  # Operation succeeds even if already inactive

        # Verify still inactive
        retrieved = portfolio_repository.get_by_id(portfolio_id)
        assert retrieved is not None
        assert retrieved.is_active is False


class TestPortfolioRepositoryIntegration:
    """Integration tests for portfolio repository operations."""

    def test_full_portfolio_lifecycle(
        self, portfolio_repository: SqlitePortfolioRepository
    ) -> None:
        """Test complete CRUD operations in sequence."""
        # Create
        portfolio = PortfolioEntity(
            name=PortfolioName("Lifecycle Test Portfolio"),
            description=Notes("Testing full lifecycle"),
            is_active=True,
        )
        portfolio_id = portfolio_repository.create(portfolio)
        assert portfolio_id is not None

        # Read
        retrieved = portfolio_repository.get_by_id(portfolio_id)
        assert retrieved is not None
        assert retrieved.name.value == "Lifecycle Test Portfolio"

        # Update
        updated_portfolio = PortfolioEntity(
            name=PortfolioName("Updated Lifecycle Portfolio"),
            description=Notes("Updated description"),
            is_active=True,
        )
        update_result = portfolio_repository.update(portfolio_id, updated_portfolio)
        assert update_result is True

        # Verify update
        updated_retrieved = portfolio_repository.get_by_id(portfolio_id)
        assert updated_retrieved is not None
        assert updated_retrieved.name.value == "Updated Lifecycle Portfolio"

        # Deactivate
        deactivate_result = portfolio_repository.deactivate(portfolio_id)
        assert deactivate_result is True

        # Verify deactivation
        final_retrieved = portfolio_repository.get_by_id(portfolio_id)
        assert final_retrieved is not None
        assert final_retrieved.is_active is False

    def test_multiple_portfolios_active_filter(
        self, portfolio_repository: SqlitePortfolioRepository
    ) -> None:
        """Test filtering behavior with multiple portfolios."""
        # Create multiple portfolios
        portfolios = [
            PortfolioEntity(name=PortfolioName("Active 1"), is_active=True),
            PortfolioEntity(name=PortfolioName("Active 2"), is_active=True),
            PortfolioEntity(name=PortfolioName("Inactive 1"), is_active=False),
            PortfolioEntity(name=PortfolioName("Inactive 2"), is_active=False),
        ]

        for portfolio in portfolios:
            _ = portfolio_repository.create(portfolio)

        # Test get_all_active
        active_portfolios = portfolio_repository.get_all_active()
        assert len(active_portfolios) == 2
        active_names = [p.name.value for p in active_portfolios]
        assert "Active 1" in active_names
        assert "Active 2" in active_names

        # Test get_all
        all_portfolios = portfolio_repository.get_all()
        assert len(all_portfolios) == 4


class TestPortfolioRepositoryErrorHandling:
    """Test error handling and edge cases."""

    def test_create_portfolio_with_invalid_entity(
        self, portfolio_repository: SqlitePortfolioRepository
    ) -> None:
        """Should raise validation error for invalid portfolio entity."""
        # This test will pass once PortfolioEntity validation is implemented
        with pytest.raises(ValueError):
            invalid_portfolio = PortfolioEntity(
                name=PortfolioName("")
            )  # Empty name should fail
            _ = portfolio_repository.create(invalid_portfolio)

    def test_database_connection_handling(
        self, portfolio_repository: SqlitePortfolioRepository
    ) -> None:
        """Should handle database connection properly."""
        # Create a portfolio to ensure connection works
        portfolio = PortfolioEntity(name=PortfolioName("Connection Test"))
        portfolio_id = portfolio_repository.create(portfolio)

        # Verify we can retrieve it
        retrieved = portfolio_repository.get_by_id(portfolio_id)
        assert retrieved is not None
        assert retrieved.name.value == "Connection Test"
