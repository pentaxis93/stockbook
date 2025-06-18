"""
Tests for SQLite Portfolio Repository implementation.

Following TDD approach - defines expected behavior before implementation.
"""

import os
import tempfile
from datetime import date
from pathlib import Path

import pytest

from domain.entities.portfolio_entity import PortfolioEntity
from domain.repositories.interfaces import IPortfolioRepository
from infrastructure.persistence.database_connection import DatabaseConnection
from infrastructure.repositories.sqlite_portfolio_repository import (
    SqlitePortfolioRepository,
)


@pytest.fixture
def db_connection():
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
def portfolio_repository(db_connection):
    """Create portfolio repository with test database."""
    return SqlitePortfolioRepository(db_connection)


@pytest.fixture
def sample_portfolio():
    """Create sample portfolio entity for testing."""
    return PortfolioEntity(
        name="Test Portfolio",
        description="A test portfolio for unit testing",
        created_date=date(2024, 1, 15),
        is_active=True,
    )


class TestPortfolioRepositoryCreate:
    """Test portfolio creation operations."""

    def test_create_portfolio_returns_id(self, portfolio_repository, sample_portfolio):
        """Should create portfolio and return database ID."""
        # Act
        portfolio_id = portfolio_repository.create(sample_portfolio)

        # Assert
        assert isinstance(portfolio_id, int)
        assert portfolio_id > 0

    def test_create_portfolio_with_minimal_data(self, portfolio_repository):
        """Should create portfolio with only required fields."""
        # Arrange
        minimal_portfolio = PortfolioEntity(name="Minimal Portfolio")

        # Act
        portfolio_id = portfolio_repository.create(minimal_portfolio)

        # Assert
        assert portfolio_id is not None

        # Verify in database
        created_portfolio = portfolio_repository.get_by_id(portfolio_id)
        assert created_portfolio.name == "Minimal Portfolio"
        assert created_portfolio.is_active is True

    def test_create_portfolio_with_all_fields(
        self, portfolio_repository, sample_portfolio
    ):
        """Should create portfolio with all fields populated."""
        # Act
        portfolio_id = portfolio_repository.create(sample_portfolio)

        # Assert
        created_portfolio = portfolio_repository.get_by_id(portfolio_id)
        assert created_portfolio.name == sample_portfolio.name
        assert created_portfolio.description == sample_portfolio.description
        assert (
            created_portfolio.created_date is not None
        )  # Database sets this automatically
        assert created_portfolio.is_active == sample_portfolio.is_active

    def test_create_duplicate_portfolio_name_allowed(self, portfolio_repository):
        """Should allow duplicate portfolio names (no unique constraint)."""
        # Arrange
        portfolio1 = PortfolioEntity(name="Duplicate Name")
        portfolio2 = PortfolioEntity(name="Duplicate Name")

        # Act
        id1 = portfolio_repository.create(portfolio1)
        id2 = portfolio_repository.create(portfolio2)

        # Assert
        assert id1 != id2
        assert portfolio_repository.get_by_id(id1).name == "Duplicate Name"
        assert portfolio_repository.get_by_id(id2).name == "Duplicate Name"


class TestPortfolioRepositoryRead:
    """Test portfolio read operations."""

    def test_get_by_id_existing_portfolio(self, portfolio_repository, sample_portfolio):
        """Should retrieve portfolio by ID."""
        # Arrange
        portfolio_id = portfolio_repository.create(sample_portfolio)

        # Act
        retrieved_portfolio = portfolio_repository.get_by_id(portfolio_id)

        # Assert
        assert retrieved_portfolio is not None
        assert retrieved_portfolio.id == portfolio_id
        assert retrieved_portfolio.name == sample_portfolio.name

    def test_get_by_id_nonexistent_portfolio(self, portfolio_repository):
        """Should return None for non-existent portfolio."""
        # Act
        result = portfolio_repository.get_by_id(999)

        # Assert
        assert result is None

    def test_get_all_active_empty_database(self, portfolio_repository):
        """Should return empty list when no active portfolios exist."""
        # Act
        portfolios = portfolio_repository.get_all_active()

        # Assert
        assert portfolios == []

    def test_get_all_active_with_active_portfolios(self, portfolio_repository):
        """Should return only active portfolios."""
        # Arrange
        active_portfolio = PortfolioEntity(name="Active Portfolio", is_active=True)
        inactive_portfolio = PortfolioEntity(name="Inactive Portfolio", is_active=False)

        active_id = portfolio_repository.create(active_portfolio)
        portfolio_repository.create(inactive_portfolio)

        # Act
        active_portfolios = portfolio_repository.get_all_active()

        # Assert
        assert len(active_portfolios) == 1
        assert active_portfolios[0].id == active_id
        assert active_portfolios[0].name == "Active Portfolio"

    def test_get_all_portfolios(self, portfolio_repository):
        """Should return all portfolios regardless of active status."""
        # Arrange
        active_portfolio = PortfolioEntity(name="Active Portfolio", is_active=True)
        inactive_portfolio = PortfolioEntity(name="Inactive Portfolio", is_active=False)

        portfolio_repository.create(active_portfolio)
        portfolio_repository.create(inactive_portfolio)

        # Act
        all_portfolios = portfolio_repository.get_all()

        # Assert
        assert len(all_portfolios) == 2
        portfolio_names = [p.name for p in all_portfolios]
        assert "Active Portfolio" in portfolio_names
        assert "Inactive Portfolio" in portfolio_names


class TestPortfolioRepositoryUpdate:
    """Test portfolio update operations."""

    def test_update_existing_portfolio(self, portfolio_repository, sample_portfolio):
        """Should update existing portfolio successfully."""
        # Arrange
        portfolio_id = portfolio_repository.create(sample_portfolio)
        updated_portfolio = PortfolioEntity(
            name="Updated Portfolio Name",
            description="Updated description",
            is_active=False,
        )

        # Act
        result = portfolio_repository.update(portfolio_id, updated_portfolio)

        # Assert
        assert result is True

        # Verify changes
        retrieved = portfolio_repository.get_by_id(portfolio_id)
        assert retrieved.name == "Updated Portfolio Name"
        assert retrieved.description == "Updated description"
        assert retrieved.is_active is False

    def test_update_nonexistent_portfolio(self, portfolio_repository):
        """Should return False when updating non-existent portfolio."""
        # Arrange
        portfolio = PortfolioEntity(name="Non-existent")

        # Act
        result = portfolio_repository.update(999, portfolio)

        # Assert
        assert result is False

    def test_partial_update_portfolio(self, portfolio_repository, sample_portfolio):
        """Should update only specified fields."""
        # Arrange
        portfolio_id = portfolio_repository.create(sample_portfolio)
        partial_update = PortfolioEntity(
            name="Partially Updated",
            description=sample_portfolio.description,  # Keep original
            is_active=sample_portfolio.is_active,  # Keep original
        )

        # Act
        portfolio_repository.update(portfolio_id, partial_update)

        # Assert
        retrieved = portfolio_repository.get_by_id(portfolio_id)
        assert retrieved.name == "Partially Updated"
        assert retrieved.description == sample_portfolio.description
        assert retrieved.is_active == sample_portfolio.is_active


class TestPortfolioRepositoryDeactivate:
    """Test portfolio deactivation (soft delete) operations."""

    def test_deactivate_existing_portfolio(
        self, portfolio_repository, sample_portfolio
    ):
        """Should deactivate existing portfolio."""
        # Arrange
        portfolio_id = portfolio_repository.create(sample_portfolio)

        # Act
        result = portfolio_repository.deactivate(portfolio_id)

        # Assert
        assert result is True

        # Verify deactivation
        retrieved = portfolio_repository.get_by_id(portfolio_id)
        assert retrieved.is_active is False

    def test_deactivate_nonexistent_portfolio(self, portfolio_repository):
        """Should return False when deactivating non-existent portfolio."""
        # Act
        result = portfolio_repository.deactivate(999)

        # Assert
        assert result is False

    def test_deactivate_already_inactive_portfolio(self, portfolio_repository):
        """Should handle deactivating already inactive portfolio."""
        # Arrange
        inactive_portfolio = PortfolioEntity(name="Already Inactive", is_active=False)
        portfolio_id = portfolio_repository.create(inactive_portfolio)

        # Act
        result = portfolio_repository.deactivate(portfolio_id)

        # Assert
        assert result is True  # Operation succeeds even if already inactive

        # Verify still inactive
        retrieved = portfolio_repository.get_by_id(portfolio_id)
        assert retrieved.is_active is False


class TestPortfolioRepositoryIntegration:
    """Integration tests for portfolio repository operations."""

    def test_full_portfolio_lifecycle(self, portfolio_repository):
        """Test complete CRUD operations in sequence."""
        # Create
        portfolio = PortfolioEntity(
            name="Lifecycle Test Portfolio",
            description="Testing full lifecycle",
            is_active=True,
        )
        portfolio_id = portfolio_repository.create(portfolio)
        assert portfolio_id is not None

        # Read
        retrieved = portfolio_repository.get_by_id(portfolio_id)
        assert retrieved.name == "Lifecycle Test Portfolio"

        # Update
        updated_portfolio = PortfolioEntity(
            name="Updated Lifecycle Portfolio",
            description="Updated description",
            is_active=True,
        )
        update_result = portfolio_repository.update(portfolio_id, updated_portfolio)
        assert update_result is True

        # Verify update
        updated_retrieved = portfolio_repository.get_by_id(portfolio_id)
        assert updated_retrieved.name == "Updated Lifecycle Portfolio"

        # Deactivate
        deactivate_result = portfolio_repository.deactivate(portfolio_id)
        assert deactivate_result is True

        # Verify deactivation
        final_retrieved = portfolio_repository.get_by_id(portfolio_id)
        assert final_retrieved.is_active is False

    def test_multiple_portfolios_active_filter(self, portfolio_repository):
        """Test filtering behavior with multiple portfolios."""
        # Create multiple portfolios
        portfolios = [
            PortfolioEntity(name="Active 1", is_active=True),
            PortfolioEntity(name="Active 2", is_active=True),
            PortfolioEntity(name="Inactive 1", is_active=False),
            PortfolioEntity(name="Inactive 2", is_active=False),
        ]

        for portfolio in portfolios:
            portfolio_repository.create(portfolio)

        # Test get_all_active
        active_portfolios = portfolio_repository.get_all_active()
        assert len(active_portfolios) == 2
        active_names = [p.name for p in active_portfolios]
        assert "Active 1" in active_names
        assert "Active 2" in active_names

        # Test get_all
        all_portfolios = portfolio_repository.get_all()
        assert len(all_portfolios) == 4


class TestPortfolioRepositoryErrorHandling:
    """Test error handling and edge cases."""

    def test_create_portfolio_with_invalid_entity(self, portfolio_repository):
        """Should raise validation error for invalid portfolio entity."""
        # This test will pass once PortfolioEntity validation is implemented
        with pytest.raises(ValueError):
            invalid_portfolio = PortfolioEntity(name="")  # Empty name should fail
            portfolio_repository.create(invalid_portfolio)

    def test_database_connection_handling(self, portfolio_repository):
        """Should handle database connection properly."""
        # Create a portfolio to ensure connection works
        portfolio = PortfolioEntity(name="Connection Test")
        portfolio_id = portfolio_repository.create(portfolio)

        # Verify we can retrieve it
        retrieved = portfolio_repository.get_by_id(portfolio_id)
        assert retrieved is not None
        assert retrieved.name == "Connection Test"
