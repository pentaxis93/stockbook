"""
Tests for SQLite Journal Entry Repository implementation.

Following TDD approach - defines expected behavior before implementation.
"""

import pytest
from datetime import date
from pathlib import Path
import tempfile
import os

from domain.entities.journal_entry_entity import JournalEntryEntity
from domain.repositories.interfaces import IJournalRepository
from infrastructure.persistence.database_connection import DatabaseConnection
from infrastructure.repositories.sqlite_journal_repository import SqliteJournalRepository


@pytest.fixture
def db_connection():
    """Create temporary database for testing."""
    # Create temporary database file
    temp_fd, temp_path = tempfile.mkstemp(suffix='.db')
    os.close(temp_fd)
    
    connection = DatabaseConnection(temp_path)
    connection.initialize_schema()
    
    # Create test data
    with connection.transaction() as conn:
        conn.execute("""
            INSERT INTO portfolio (id, name, description, max_positions, max_risk_per_trade, is_active)
            VALUES (1, 'Test Portfolio', 'Test portfolio for journals', 50, 0.02, 1)
        """)
        conn.execute("""
            INSERT INTO stock (id, symbol, name, industry_group, grade, notes)
            VALUES (1, 'AAPL', 'Apple Inc.', 'Technology', 'A', 'Test stock')
        """)
    
    yield connection
    
    # Cleanup
    connection.close()
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def journal_repository(db_connection):
    """Create journal repository with test database."""
    return SqliteJournalRepository(db_connection)


@pytest.fixture
def sample_entry():
    """Create sample journal entry for testing."""
    return JournalEntryEntity(
        portfolio_id=1,
        stock_id=1,
        entry_date=date(2024, 1, 15),
        content="This is a test journal entry about Apple stock analysis."
    )


class TestJournalRepositoryBasic:
    """Test basic journal repository operations."""
    
    def test_create_entry_returns_id(self, journal_repository, sample_entry):
        """Should create journal entry and return database ID."""
        # Act
        entry_id = journal_repository.create(sample_entry)
        
        # Assert
        assert isinstance(entry_id, int)
        assert entry_id > 0
    
    def test_get_by_id(self, journal_repository, sample_entry):
        """Should retrieve journal entry by ID."""
        # Arrange
        entry_id = journal_repository.create(sample_entry)
        
        # Act
        retrieved = journal_repository.get_by_id(entry_id)
        
        # Assert
        assert retrieved is not None
        assert retrieved.id == entry_id
        assert retrieved.content == sample_entry.content
        assert retrieved.portfolio_id == sample_entry.portfolio_id
    
    def test_get_recent(self, journal_repository):
        """Should retrieve recent entries ordered by date."""
        # Arrange
        entries = [
            JournalEntryEntity(
                portfolio_id=1, entry_date=date(2024, 1, 1),
                content="First entry"
            ),
            JournalEntryEntity(
                portfolio_id=1, entry_date=date(2024, 1, 15),
                content="Latest entry"
            ),
        ]
        
        for entry in entries:
            journal_repository.create(entry)
        
        # Act
        recent = journal_repository.get_recent(limit=5)
        
        # Assert
        assert len(recent) == 2
        # Should be ordered by date (newest first)
        assert recent[0].entry_date > recent[1].entry_date
        assert recent[0].content == "Latest entry"
    
    def test_get_by_portfolio(self, journal_repository, sample_entry):
        """Should retrieve entries for specific portfolio."""
        # Arrange
        entry_id = journal_repository.create(sample_entry)
        
        # Act
        portfolio_entries = journal_repository.get_by_portfolio(1)
        
        # Assert
        assert len(portfolio_entries) == 1
        assert portfolio_entries[0].id == entry_id
    
    def test_update_entry(self, journal_repository, sample_entry):
        """Should update existing journal entry."""
        # Arrange
        entry_id = journal_repository.create(sample_entry)
        updated_entry = JournalEntryEntity(
            portfolio_id=1,
            stock_id=1,
            entry_date=date(2024, 1, 15),
            content="Updated journal entry content."
        )
        
        # Act
        result = journal_repository.update(entry_id, updated_entry)
        
        # Assert
        assert result is True
        
        # Verify update
        retrieved = journal_repository.get_by_id(entry_id)
        assert retrieved.content == "Updated journal entry content."
    
    def test_delete_entry(self, journal_repository, sample_entry):
        """Should delete journal entry."""
        # Arrange
        entry_id = journal_repository.create(sample_entry)
        
        # Act
        result = journal_repository.delete(entry_id)
        
        # Assert
        assert result is True
        
        # Verify deletion
        retrieved = journal_repository.get_by_id(entry_id)
        assert retrieved is None