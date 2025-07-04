"""
Tests for JournalEntry domain entity.

Following TDD approach with focus on value object purity and business logic.
Tests define expected behavior before implementation.
"""

from datetime import date

import pytest

from src.domain.entities.journal_entry import JournalEntry
from src.domain.value_objects import JournalContent


class TestJournalEntry:
    """Test JournalEntry domain entity with value objects and business logic."""

    def test_create_journal_entry_with_value_objects(self) -> None:
        """Test creating a journal entry with all value objects."""
        entry = JournalEntry(
            entry_date=date(2024, 1, 15),
            content=JournalContent(
                "This is an important market observation about the current trends."
            ),
            portfolio_id="portfolio-id-1",
            stock_id="stock-id-2",
            transaction_id="transaction-id-3",
        )

        assert entry.entry_date == date(2024, 1, 15)
        assert (
            entry.content.value
            == "This is an important market observation about the current trends."
        )
        assert entry.portfolio_id == "portfolio-id-1"
        assert entry.stock_id == "stock-id-2"
        assert entry.transaction_id == "transaction-id-3"

    def test_create_journal_entry_with_minimal_data(self) -> None:
        """Test creating journal entry with only required fields."""
        entry = JournalEntry(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Simple entry content."),
        )

        assert entry.entry_date == date(2024, 1, 15)
        assert entry.content.value == "Simple entry content."
        assert entry.portfolio_id is None
        assert entry.stock_id is None
        assert entry.transaction_id is None

    def test_create_journal_entry_with_invalid_portfolio_id_raises_error(self) -> None:
        """Should raise error for invalid portfolio ID."""
        with pytest.raises(ValueError, match="Portfolio ID must be a non-empty string"):
            _ = JournalEntry(
                entry_date=date(2024, 1, 15),
                content=JournalContent("Test content."),
                portfolio_id="",  # Invalid empty string
            )

    def test_create_journal_entry_with_invalid_stock_id_raises_error(self) -> None:
        """Should raise error for invalid stock ID."""
        with pytest.raises(ValueError, match="Stock ID must be a non-empty string"):
            _ = JournalEntry(
                entry_date=date(2024, 1, 15),
                content=JournalContent("Test content."),
                stock_id="",  # Invalid empty string
            )

    def test_create_journal_entry_with_invalid_transaction_id_raises_error(
        self,
    ) -> None:
        """Should raise error for invalid transaction ID."""
        with pytest.raises(
            ValueError, match="Transaction ID must be a non-empty string"
        ):
            _ = JournalEntry(
                entry_date=date(2024, 1, 15),
                content=JournalContent("Test content."),
                transaction_id="",  # Invalid empty string
            )

    def test_create_journal_entry_with_invalid_content_raises_error(self) -> None:
        """Should raise error for invalid content through JournalContent value object."""
        with pytest.raises(ValueError, match="Journal content cannot be empty"):
            _ = JournalContent("")  # Error happens at JournalContent construction

    def test_journal_entry_equality(self) -> None:
        """Should compare journal entries based on ID."""
        entry1 = JournalEntry(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Market observation about trends."),
        )

        entry2 = JournalEntry(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Market observation about trends."),
            portfolio_id="portfolio-id-1",  # Different metadata
        )

        entry3 = JournalEntry(
            entry_date=date(2024, 1, 16),  # Different date
            content=JournalContent("Market observation about trends."),
        )

        # Different instances with same attributes but different IDs are NOT equal
        assert entry1 != entry2  # Different IDs
        assert entry1 != entry3  # Different IDs

        # Same ID means equal
        entry4 = JournalEntry(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Market observation about trends."),
            id="same-id",
        )
        entry5 = JournalEntry(
            entry_date=date(2024, 2, 20),  # Different date
            content=JournalContent("Completely different content."),
            portfolio_id="portfolio-id-2",
            stock_id="stock-id-2",
            id="same-id",
        )
        assert entry4 == entry5  # Same ID, even with different attributes

    def test_journal_entry_hash(self) -> None:
        """Should hash consistently based on ID."""
        entry1 = JournalEntry(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Market observation."),
        )

        entry2 = JournalEntry(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Market observation."),
            portfolio_id="portfolio-id-1",  # Different metadata
        )

        # Different IDs should have different hashes (likely but not guaranteed)
        assert hash(entry1) != hash(entry2)  # Different IDs

        # Same ID should have same hash
        entry3 = JournalEntry(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Market observation."),
            id="same-id",
        )
        entry4 = JournalEntry(
            entry_date=date(2024, 2, 20),
            content=JournalContent("Different content."),
            portfolio_id="portfolio-id-2",
            id="same-id",
        )
        assert hash(entry3) == hash(entry4)  # Same ID, same hash

    def test_journal_entry_string_representation(self) -> None:
        """Should have informative string representation."""
        entry = JournalEntry(
            entry_date=date(2024, 1, 15),
            content=JournalContent(
                "This is a longer journal entry with significant market observations and analysis."
            ),
        )

        str_repr = str(entry)
        assert "2024-01-15" in str_repr
        assert "This is a longer journal entry with significant" in str_repr

    def test_journal_entry_repr(self) -> None:
        """Should have detailed repr representation."""
        entry = JournalEntry(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Test content."),
        )

        expected = "JournalEntry(date=2024-01-15)"
        assert repr(entry) == expected

    # Business behavior tests
    def test_journal_entry_is_related_to_portfolio(self) -> None:
        """Should check if entry is related to a portfolio."""
        portfolio_entry = JournalEntry(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Portfolio analysis."),
            portfolio_id="portfolio-id-1",
        )

        general_entry = JournalEntry(
            entry_date=date(2024, 1, 15),
            content=JournalContent("General market thoughts."),
        )

        assert portfolio_entry.is_related_to_portfolio() is True
        assert general_entry.is_related_to_portfolio() is False

    def test_journal_entry_is_related_to_stock(self) -> None:
        """Should check if entry is related to a stock."""
        stock_entry = JournalEntry(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Stock analysis."),
            stock_id="stock-id-1",
        )

        general_entry = JournalEntry(
            entry_date=date(2024, 1, 15),
            content=JournalContent("General market thoughts."),
        )

        assert stock_entry.is_related_to_stock() is True
        assert general_entry.is_related_to_stock() is False

    def test_journal_entry_is_related_to_transaction(self) -> None:
        """Should check if entry is related to a transaction."""
        transaction_entry = JournalEntry(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Transaction analysis."),
            transaction_id="transaction-id-1",
        )

        general_entry = JournalEntry(
            entry_date=date(2024, 1, 15),
            content=JournalContent("General market thoughts."),
        )

        assert transaction_entry.is_related_to_transaction() is True
        assert general_entry.is_related_to_transaction() is False

    def test_journal_entry_get_content_preview(self) -> None:
        """Should provide content preview for display."""
        short_entry = JournalEntry(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Short content."),
        )

        long_entry = JournalEntry(
            entry_date=date(2024, 1, 15),
            content=JournalContent(
                "This is a very long journal entry that contains extensive market analysis and observations that should be truncated for preview purposes."
            ),
        )

        assert short_entry.get_content_preview() == "Short content."
        long_preview = long_entry.get_content_preview(50)
        assert len(long_preview) <= 53  # 50 + "..."
        assert long_preview.endswith("...")

    def test_journal_entry_update_content(self) -> None:
        """Should be able to update entry content."""
        entry = JournalEntry(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Original content."),
        )

        # Update with JournalContent value object
        entry.update_content(JournalContent("Updated content."))
        assert entry.content.value == "Updated content."

        # Update with string (should be converted to JournalContent)
        entry.update_content("String content.")
        assert entry.content.value == "String content."

    def test_journal_entry_create_with_id(self) -> None:
        """Should create journal entry with provided ID."""
        test_id = "journal-entry-id-123"
        entry = JournalEntry(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Test content."),
            id=test_id,
        )

        assert entry.id == test_id

    def test_journal_entry_id_immutability(self) -> None:
        """Should not be able to change ID after creation."""
        entry = JournalEntry(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Test content."),
            id="test-id-1",
        )

        # ID property should not have a setter
        with pytest.raises(AttributeError):
            entry.id = "different-id"  # type: ignore[misc]

    def test_journal_entry_from_persistence(self) -> None:
        """Should create journal entry from persistence with existing ID."""
        test_id = "persistence-id-456"
        entry = JournalEntry.from_persistence(
            test_id,
            entry_date=date(2024, 1, 15),
            content=JournalContent("Test content from database."),
            portfolio_id="portfolio-id-1",
        )

        assert entry.id == test_id
        assert entry.portfolio_id == "portfolio-id-1"


class TestJournalContent:
    """Test JournalContent value object validation."""

    def test_valid_journal_content_accepted(self) -> None:
        """Test that valid journal content is accepted."""
        valid_contents = [
            "Short entry.",
            "This is a longer journal entry with more detailed analysis.",
            "A" * 5000,  # Long but valid content
        ]
        for content in valid_contents:
            journal_content = JournalContent(content)
            assert journal_content.value == content

    def test_journal_content_strips_whitespace(self) -> None:
        """Test that journal content strips leading/trailing whitespace."""
        content = JournalContent("  Market analysis with spaces  ")
        assert content.value == "Market analysis with spaces"

    def test_empty_journal_content_rejected(self) -> None:
        """Test that empty journal content is rejected."""
        empty_contents = ["", "   ", "\t", "\n"]
        for empty_content in empty_contents:
            with pytest.raises(ValueError, match="Journal content cannot be empty"):
                _ = JournalContent(empty_content)

    def test_too_long_journal_content_rejected(self) -> None:
        """Test that excessively long journal content is rejected."""
        long_content = "A" * 10001  # Max is 10000 characters
        with pytest.raises(
            ValueError, match="Journal content cannot exceed 10000 characters"
        ):
            _ = JournalContent(long_content)

    def test_max_length_journal_content_accepted(self) -> None:
        """Test that journal content at max length is accepted."""
        max_length_content = "A" * 10000  # Exactly 10000 characters
        journal_content = JournalContent(max_length_content)
        assert journal_content.value == max_length_content
        assert len(journal_content.value) == 10000

    def test_journal_entry_equality_with_non_journal_entry_object(self) -> None:
        """Test that journal entry equality returns False for non-JournalEntry objects."""
        entry = JournalEntry(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Test content"),
            portfolio_id="portfolio-1",
            stock_id="stock-1",
        )

        # Test equality with different types - should return False (covers line 103)
        assert entry != "not a journal entry"
        assert entry != 123
        assert entry is not None
        assert entry != {"entry_date": date(2024, 1, 15), "content": "Test content"}
