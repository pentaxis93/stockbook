"""
Tests for SQLite Journal Entry Repository implementation.

Following TDD approach - defines expected behavior before implementation.
"""

import os
import tempfile
from datetime import date
from pathlib import Path
from typing import Iterator

import pytest

from src.domain.entities.journal_entry_entity import JournalEntryEntity

# IJournalRepository import removed - unused
from src.domain.value_objects import JournalContent
from src.infrastructure.persistence.database_connection import DatabaseConnection
from src.infrastructure.repositories.sqlite_journal_repository import (
    SqliteJournalRepository,
)


@pytest.fixture
def db_connection() -> Iterator[DatabaseConnection]:
    """Create temporary database for testing."""
    # Create temporary database file
    temp_fd, temp_path = tempfile.mkstemp(suffix=".db")
    os.close(temp_fd)

    connection = DatabaseConnection(temp_path)
    connection.initialize_schema()

    # Create test data
    with connection.transaction() as conn:
        _ = conn.execute(
            """
            INSERT INTO portfolio (id, name, description, max_positions, max_risk_per_trade, is_active)
            VALUES ('portfolio-id-1', 'Test Portfolio', 'Test portfolio for journals', 50, 0.02, 1)
        """
        )
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
def journal_repository(db_connection: DatabaseConnection) -> SqliteJournalRepository:
    """Create journal repository with test database."""
    return SqliteJournalRepository(db_connection)


@pytest.fixture
def sample_entry() -> JournalEntryEntity:
    """Create sample journal entry for testing."""
    return JournalEntryEntity(
        portfolio_id="portfolio-id-1",
        stock_id="stock-id-1",
        entry_date=date(2024, 1, 15),
        content=JournalContent(
            "This is a test journal entry about Apple stock analysis."
        ),
    )


class TestJournalRepositoryBasic:
    """Test basic journal repository operations."""

    def test_create_entry_returns_id(
        self,
        journal_repository: SqliteJournalRepository,
        sample_entry: JournalEntryEntity,
    ) -> None:
        """Should create journal entry and return database ID."""
        # Act
        entry_id = journal_repository.create(sample_entry)

        # Assert
        assert isinstance(entry_id, str)
        assert entry_id

    def test_get_by_id(
        self,
        journal_repository: SqliteJournalRepository,
        sample_entry: JournalEntryEntity,
    ) -> None:
        """Should retrieve journal entry by ID."""
        # Arrange
        entry_id = journal_repository.create(sample_entry)

        # Act
        retrieved = journal_repository.get_by_id(entry_id)

        # Assert
        assert retrieved is not None
        assert retrieved.id == entry_id
        assert retrieved.content.value == sample_entry.content.value
        assert retrieved.portfolio_id == sample_entry.portfolio_id

    def test_get_recent(self, journal_repository: SqliteJournalRepository) -> None:
        """Should retrieve recent entries ordered by date."""
        # Arrange
        entries = [
            JournalEntryEntity(
                portfolio_id="portfolio-id-1",
                entry_date=date(2024, 1, 1),
                content=JournalContent("First entry"),
            ),
            JournalEntryEntity(
                portfolio_id="portfolio-id-1",
                entry_date=date(2024, 1, 15),
                content=JournalContent("Latest entry"),
            ),
        ]

        for entry in entries:
            _ = journal_repository.create(entry)

        # Act
        recent = journal_repository.get_recent(limit=5)

        # Assert
        assert len(recent) == 2
        # Should be ordered by date (newest first)
        assert recent[0].entry_date > recent[1].entry_date
        assert recent[0].content.value == "Latest entry"

    def test_get_by_portfolio(
        self,
        journal_repository: SqliteJournalRepository,
        sample_entry: JournalEntryEntity,
    ) -> None:
        """Should retrieve entries for specific portfolio."""
        # Arrange
        entry_id = journal_repository.create(sample_entry)

        # Act
        portfolio_entries = journal_repository.get_by_portfolio("portfolio-id-1")

        # Assert
        assert len(portfolio_entries) == 1
        assert portfolio_entries[0].id == entry_id

    def test_update_entry(
        self,
        journal_repository: SqliteJournalRepository,
        sample_entry: JournalEntryEntity,
    ) -> None:
        """Should update existing journal entry."""
        # Arrange
        entry_id = journal_repository.create(sample_entry)
        updated_entry = JournalEntryEntity(
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-1",
            entry_date=date(2024, 1, 15),
            content=JournalContent("Updated journal entry content."),
        )

        # Act
        result = journal_repository.update(entry_id, updated_entry)

        # Assert
        assert result is True

        # Verify update
        retrieved = journal_repository.get_by_id(entry_id)
        assert retrieved is not None
        assert retrieved.content.value == "Updated journal entry content."

    def test_delete_entry(
        self,
        journal_repository: SqliteJournalRepository,
        sample_entry: JournalEntryEntity,
    ) -> None:
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


class TestJournalRepositoryStockOperations:
    """Test journal repository operations filtered by stock."""

    def test_get_by_stock_returns_entries_for_stock(
        self, journal_repository: SqliteJournalRepository
    ) -> None:
        """Should return all entries for specified stock ordered by date."""
        # Arrange - Use existing stock-id-1 from fixture
        stock_entries = [
            JournalEntryEntity(
                portfolio_id="portfolio-id-1",
                stock_id="stock-id-1",
                entry_date=date(2024, 1, 1),
                content=JournalContent("First Apple entry"),
            ),
            JournalEntryEntity(
                portfolio_id="portfolio-id-1",
                stock_id="stock-id-1",
                entry_date=date(2024, 1, 15),
                content=JournalContent("Second Apple entry"),
            ),
        ]

        for entry in stock_entries:
            _ = journal_repository.create(entry)

        # Act
        apple_entries = journal_repository.get_by_stock("stock-id-1")

        # Assert
        assert len(apple_entries) == 2
        # Should be ordered by date (newest first)
        assert apple_entries[0].entry_date > apple_entries[1].entry_date
        assert apple_entries[0].content.value == "Second Apple entry"
        assert apple_entries[1].content.value == "First Apple entry"
        # Should only contain entries for the specified stock
        for entry in apple_entries:
            assert entry.stock_id == "stock-id-1"

    def test_get_by_stock_with_limit(
        self, journal_repository: SqliteJournalRepository
    ) -> None:
        """Should respect limit parameter when specified."""
        # Arrange - Create multiple entries for the same stock
        entries = [
            JournalEntryEntity(
                portfolio_id="portfolio-id-1",
                stock_id="stock-id-1",
                entry_date=date(2024, 1, i),
                content=JournalContent(f"Entry {i}"),
            )
            for i in range(1, 6)  # Create 5 entries
        ]

        for entry in entries:
            _ = journal_repository.create(entry)

        # Act
        limited_entries = journal_repository.get_by_stock("stock-id-1", limit=3)

        # Assert
        assert len(limited_entries) == 3
        # Should be newest entries first
        assert limited_entries[0].entry_date == date(2024, 1, 5)

    def test_get_by_stock_returns_empty_list_for_nonexistent_stock(
        self, journal_repository: SqliteJournalRepository
    ) -> None:
        """Should return empty list when no entries exist for stock."""
        # Act
        entries = journal_repository.get_by_stock("NONEXISTENT")

        # Assert
        assert entries == []

    def test_get_by_stock_with_none_limit(
        self, journal_repository: SqliteJournalRepository
    ) -> None:
        """Should return all entries when limit is None."""
        # Arrange
        entries = [
            JournalEntryEntity(
                portfolio_id="portfolio-id-1",
                stock_id="stock-id-1",
                entry_date=date(2024, 1, i),
                content=JournalContent(f"Entry {i}"),
            )
            for i in range(1, 4)
        ]

        for entry in entries:
            _ = journal_repository.create(entry)

        # Act
        all_entries = journal_repository.get_by_stock("stock-id-1", limit=None)

        # Assert
        assert len(all_entries) == 3


class TestJournalRepositoryTransactionOperations:
    """Test journal repository operations filtered by transaction."""

    def test_get_by_transaction_returns_entries_for_transaction(
        self, journal_repository: SqliteJournalRepository
    ) -> None:
        """Should return all entries for specified transaction ordered by date."""
        # This test focuses on the filtering and ordering logic
        # We'll disable foreign key constraints temporarily for this test

        # Arrange - Disable foreign key constraints
        conn = journal_repository.db_connection.get_connection()
        with conn:
            _ = conn.execute("PRAGMA foreign_keys = OFF")

            # Create entries with transaction IDs directly
            _ = conn.execute(
                """
                    INSERT INTO journal_entry (id, portfolio_id, transaction_id, entry_date, content, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                """,
                (
                    "entry-1",
                    "portfolio-id-1",
                    "txn-123",
                    "2024-01-01",
                    "First transaction note",
                ),
            )

            _ = conn.execute(
                """
                    INSERT INTO journal_entry (id, portfolio_id, transaction_id, entry_date, content, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                """,
                (
                    "entry-2",
                    "portfolio-id-1",
                    "txn-123",
                    "2024-01-15",
                    "Follow-up transaction note",
                ),
            )

            _ = conn.execute(
                """
                    INSERT INTO journal_entry (id, portfolio_id, transaction_id, entry_date, content, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                """,
                (
                    "entry-3",
                    "portfolio-id-1",
                    "txn-456",
                    "2024-01-10",
                    "Different transaction note",
                ),
            )

            # Re-enable foreign key constraints
            _ = conn.execute("PRAGMA foreign_keys = ON")

        # Act
        txn_entries = journal_repository.get_by_transaction("txn-123")

        # Assert
        assert len(txn_entries) == 2
        # Should be ordered by date (newest first)
        assert txn_entries[0].entry_date > txn_entries[1].entry_date
        assert txn_entries[0].content.value == "Follow-up transaction note"
        assert txn_entries[1].content.value == "First transaction note"
        # Should only contain entries for specified transaction
        for entry in txn_entries:
            assert entry.transaction_id == "txn-123"

    def test_get_by_transaction_returns_empty_list_for_nonexistent_transaction(
        self, journal_repository: SqliteJournalRepository
    ) -> None:
        """Should return empty list when no entries exist for transaction."""
        # Act
        entries = journal_repository.get_by_transaction("nonexistent-txn")

        # Assert
        assert entries == []


class TestJournalRepositoryDateRangeOperations:
    """Test journal repository operations filtered by date range."""

    def test_get_by_date_range_returns_entries_in_range(
        self, journal_repository: SqliteJournalRepository
    ) -> None:
        """Should return entries within specified date range ordered by date."""
        # Arrange - Use existing portfolio-id-1 from fixture
        entries = [
            JournalEntryEntity(
                portfolio_id="portfolio-id-1",
                entry_date=date(2024, 1, 5),
                content=JournalContent("Before range"),
            ),
            JournalEntryEntity(
                portfolio_id="portfolio-id-1",
                entry_date=date(2024, 1, 10),
                content=JournalContent("In range - first"),
            ),
            JournalEntryEntity(
                portfolio_id="portfolio-id-1",
                entry_date=date(2024, 1, 15),
                content=JournalContent("In range - second"),
            ),
            JournalEntryEntity(
                portfolio_id="portfolio-id-1",
                entry_date=date(2024, 1, 20),
                content=JournalContent("In range - third"),
            ),
            JournalEntryEntity(
                portfolio_id="portfolio-id-1",
                entry_date=date(2024, 1, 25),
                content=JournalContent("After range"),
            ),
        ]

        for entry in entries:
            _ = journal_repository.create(entry)

        # Act
        range_entries = journal_repository.get_by_date_range(
            start_date=date(2024, 1, 10), end_date=date(2024, 1, 20)
        )

        # Assert
        assert len(range_entries) == 3
        # Should be ordered by date (newest first)
        assert range_entries[0].entry_date == date(2024, 1, 20)
        assert range_entries[1].entry_date == date(2024, 1, 15)
        assert range_entries[2].entry_date == date(2024, 1, 10)
        # Verify content matches expected entries
        assert range_entries[0].content.value == "In range - third"
        assert range_entries[1].content.value == "In range - second"
        assert range_entries[2].content.value == "In range - first"

    def test_get_by_date_range_excludes_entries_outside_range(
        self, journal_repository: SqliteJournalRepository
    ) -> None:
        """Should exclude entries outside the specified date range."""
        # Arrange
        entries = [
            JournalEntryEntity(
                portfolio_id="portfolio-id-1",
                entry_date=date(2024, 1, 1),  # Before range
                content=JournalContent("Too early"),
            ),
            JournalEntryEntity(
                portfolio_id="portfolio-id-1",
                entry_date=date(2024, 1, 15),  # In range
                content=JournalContent("Perfect timing"),
            ),
            JournalEntryEntity(
                portfolio_id="portfolio-id-1",
                entry_date=date(2024, 2, 1),  # After range
                content=JournalContent("Too late"),
            ),
        ]

        for entry in entries:
            _ = journal_repository.create(entry)

        # Act
        range_entries = journal_repository.get_by_date_range(
            start_date=date(2024, 1, 10), end_date=date(2024, 1, 20)
        )

        # Assert
        assert len(range_entries) == 1
        assert range_entries[0].content.value == "Perfect timing"
        assert range_entries[0].entry_date == date(2024, 1, 15)

    def test_get_by_date_range_returns_empty_list_for_no_matches(
        self, journal_repository: SqliteJournalRepository
    ) -> None:
        """Should return empty list when no entries match date range."""
        # Arrange
        entry = JournalEntryEntity(
            portfolio_id="portfolio-id-1",
            entry_date=date(2024, 1, 1),
            content=JournalContent("Outside range"),
        )
        _ = journal_repository.create(entry)

        # Act
        range_entries = journal_repository.get_by_date_range(
            start_date=date(2024, 2, 1), end_date=date(2024, 2, 28)
        )

        # Assert
        assert range_entries == []

    def test_get_by_date_range_inclusive_boundaries(
        self, journal_repository: SqliteJournalRepository
    ) -> None:
        """Should include entries on the exact start and end dates."""
        # Arrange
        entries = [
            JournalEntryEntity(
                portfolio_id="portfolio-id-1",
                entry_date=date(2024, 1, 10),  # Exact start date
                content=JournalContent("Start boundary"),
            ),
            JournalEntryEntity(
                portfolio_id="portfolio-id-1",
                entry_date=date(2024, 1, 20),  # Exact end date
                content=JournalContent("End boundary"),
            ),
        ]

        for entry in entries:
            _ = journal_repository.create(entry)

        # Act
        range_entries = journal_repository.get_by_date_range(
            start_date=date(2024, 1, 10), end_date=date(2024, 1, 20)
        )

        # Assert
        assert len(range_entries) == 2
        entry_contents = [entry.content.value for entry in range_entries]
        assert "Start boundary" in entry_contents
        assert "End boundary" in entry_contents


class TestJournalRepositoryAdvancedOperations:
    """Test advanced journal repository operations and edge cases."""

    def test_get_by_portfolio_with_limit_parameter(
        self, journal_repository: SqliteJournalRepository
    ) -> None:
        """Should respect limit parameter in get_by_portfolio method."""
        # Arrange - Use existing portfolio-id-1 from fixture
        entries = [
            JournalEntryEntity(
                portfolio_id="portfolio-id-1",
                entry_date=date(2024, 1, i),
                content=JournalContent(f"Portfolio entry {i}"),
            )
            for i in range(1, 6)  # Create 5 entries
        ]

        for entry in entries:
            _ = journal_repository.create(entry)

        # Act
        limited_entries = journal_repository.get_by_portfolio("portfolio-id-1", limit=3)

        # Assert
        assert len(limited_entries) == 3
        # Should return most recent entries first
        assert limited_entries[0].entry_date == date(2024, 1, 5)


class TestJournalRepositoryConnectionManagement:
    """Test connection management for non-transactional contexts."""

    def test_connection_properties_exist(self) -> None:
        """Should have db_connection property available."""
        # This is a simple test to verify the connection exists
        # The actual connection cleanup coverage is achieved through other tests

        db_conn = DatabaseConnection(":memory:")
        repository = SqliteJournalRepository(db_conn)

        # Assert
        assert repository.db_connection is not None
        assert hasattr(repository.db_connection, "get_connection")


class TestJournalRepositoryDateParsing:
    """Test date parsing edge cases in _row_to_entity method."""

    def test_row_to_entity_handles_invalid_date_format(
        self, journal_repository: SqliteJournalRepository
    ) -> None:
        """Should use today's date when entry_date parsing fails."""
        from unittest.mock import patch

        # Arrange
        # Create a mock row with invalid date format that would cause parsing to fail
        mock_row = {
            "id": "test-id",
            "entry_date": "invalid-date-format",  # This will cause parsing to fail
            "content": "Test content",
            "stock_id": "AAPL",
            "portfolio_id": "portfolio-1",
            "transaction_id": None,
            "created_at": "2024-01-01 12:00:00",
            "updated_at": "2024-01-01 12:00:00",
        }

        # Mock date.today() to return a predictable date
        expected_date = date(2024, 6, 23)
        with patch(
            "src.infrastructure.repositories.sqlite_journal_repository.date"
        ) as mock_date:
            mock_date.today.return_value = expected_date
            mock_date.fromisoformat.side_effect = ValueError("Invalid date format")

            # Act
            entity = journal_repository._row_to_entity(mock_row)  # type: ignore[attr-defined,arg-type]

            # Assert
            assert entity.entry_date == expected_date
            mock_date.today.assert_called_once()
