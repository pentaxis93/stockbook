"""
Tests for JournalEntry domain entity.

Following TDD approach with focus on value object purity and business logic.
Tests define expected behavior before implementation.
"""

from datetime import UTC, datetime

import pytest

from src.domain.entities.journal_entry import JournalEntry
from src.domain.value_objects import JournalContent


class TestJournalEntry:
    """Test JournalEntry domain entity with value objects and business logic."""

    def test_create_journal_entry_with_value_objects(self) -> None:
        """Test creating a journal entry with all value objects."""
        entry = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(
                JournalContent(
                    "This is an important market observation about the current trends."
                )
            )
            .with_portfolio_id("portfolio-id-1")
            .with_stock_id("stock-id-2")
            .with_transaction_id("transaction-id-3")
            .build()
        )

        assert entry.entry_date == datetime(2024, 1, 15, tzinfo=UTC)
        assert (
            entry.content.value
            == "This is an important market observation about the current trends."
        )
        assert entry.portfolio_id == "portfolio-id-1"
        assert entry.stock_id == "stock-id-2"
        assert entry.transaction_id == "transaction-id-3"

    def test_create_journal_entry_with_minimal_data(self) -> None:
        """Test creating journal entry with only required fields."""
        entry = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(JournalContent("Simple entry content."))
            .build()
        )

        assert entry.entry_date == datetime(2024, 1, 15, tzinfo=UTC)
        assert entry.content.value == "Simple entry content."
        assert entry.portfolio_id is None
        assert entry.stock_id is None
        assert entry.transaction_id is None

    def test_create_journal_entry_with_invalid_portfolio_id_raises_error(self) -> None:
        """Should raise error for invalid portfolio ID."""
        with pytest.raises(ValueError, match="Portfolio ID must be a non-empty string"):
            _ = (
                JournalEntry.Builder()
                .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
                .with_content(JournalContent("Test content."))
                .with_portfolio_id("")  # Invalid empty string
                .build()
            )

    def test_create_journal_entry_with_invalid_stock_id_raises_error(self) -> None:
        """Should raise error for invalid stock ID."""
        with pytest.raises(ValueError, match="Stock ID must be a non-empty string"):
            _ = (
                JournalEntry.Builder()
                .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
                .with_content(JournalContent("Test content."))
                .with_stock_id("")  # Invalid empty string
                .build()
            )

    def test_create_journal_entry_with_invalid_transaction_id_raises_error(
        self,
    ) -> None:
        """Should raise error for invalid transaction ID."""
        with pytest.raises(
            ValueError, match="Transaction ID must be a non-empty string"
        ):
            _ = (
                JournalEntry.Builder()
                .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
                .with_content(JournalContent("Test content."))
                .with_transaction_id("")  # Invalid empty string
                .build()
            )

    def test_create_journal_entry_with_invalid_content_raises_error(self) -> None:
        """Should raise error for invalid content through JournalContent value
        object."""
        with pytest.raises(ValueError, match="Journal content cannot be empty"):
            _ = JournalContent("")  # Error happens at JournalContent construction

    def test_journal_entry_equality(self) -> None:
        """Should compare journal entries based on ID."""
        entry1 = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(JournalContent("Market observation about trends."))
            .build()
        )

        entry2 = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(JournalContent("Market observation about trends."))
            .with_portfolio_id("portfolio-id-1")  # Different metadata
            .build()
        )

        entry3 = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 16, tzinfo=UTC))  # Different date
            .with_content(JournalContent("Market observation about trends."))
            .build()
        )

        # Different instances with same attributes but different IDs are NOT equal
        assert entry1 != entry2  # Different IDs
        assert entry1 != entry3  # Different IDs

        # Same ID means equal
        entry4 = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(JournalContent("Market observation about trends."))
            .with_id("same-id")
            .build()
        )
        entry5 = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 2, 20, tzinfo=UTC))  # Different date
            .with_content(JournalContent("Completely different content."))
            .with_portfolio_id("portfolio-id-2")
            .with_stock_id("stock-id-2")
            .with_id("same-id")
            .build()
        )
        assert entry4 == entry5  # Same ID, even with different attributes

    def test_journal_entry_hash(self) -> None:
        """Should hash consistently based on ID."""
        entry1 = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(JournalContent("Market observation."))
            .build()
        )

        entry2 = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(JournalContent("Market observation."))
            .with_portfolio_id("portfolio-id-1")  # Different metadata
            .build()
        )

        # Different IDs should have different hashes (likely but not guaranteed)
        assert hash(entry1) != hash(entry2)  # Different IDs

        # Same ID should have same hash
        entry3 = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(JournalContent("Market observation."))
            .with_id("same-id")
            .build()
        )
        entry4 = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 2, 20, tzinfo=UTC))
            .with_content(JournalContent("Different content."))
            .with_portfolio_id("portfolio-id-2")
            .with_id("same-id")
            .build()
        )
        assert hash(entry3) == hash(entry4)  # Same ID, same hash

    def test_journal_entry_string_representation(self) -> None:
        """Should have informative string representation."""
        entry = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(
                JournalContent(
                    "This is a longer journal entry with significant market "
                    + "observations and analysis."
                )
            )
            .build()
        )

        str_repr = str(entry)
        assert "2024-01-15" in str_repr
        assert "This is a longer journal entry with significant" in str_repr

    def test_journal_entry_repr(self) -> None:
        """Should have detailed repr representation."""
        entry = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(JournalContent("Test content."))
            .build()
        )

        expected = "JournalEntry(date=2024-01-15 00:00:00+00:00)"
        assert repr(entry) == expected

    # Business behavior tests
    def test_journal_entry_is_related_to_portfolio(self) -> None:
        """Should check if entry is related to a portfolio."""
        portfolio_entry = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(JournalContent("Portfolio analysis."))
            .with_portfolio_id("portfolio-id-1")
            .build()
        )

        general_entry = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(JournalContent("General market thoughts."))
            .build()
        )

        assert portfolio_entry.is_related_to_portfolio() is True
        assert general_entry.is_related_to_portfolio() is False

    def test_journal_entry_is_related_to_stock(self) -> None:
        """Should check if entry is related to a stock."""
        stock_entry = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(JournalContent("Stock analysis."))
            .with_stock_id("stock-id-1")
            .build()
        )

        general_entry = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(JournalContent("General market thoughts."))
            .build()
        )

        assert stock_entry.is_related_to_stock() is True
        assert general_entry.is_related_to_stock() is False

    def test_journal_entry_is_related_to_transaction(self) -> None:
        """Should check if entry is related to a transaction."""
        transaction_entry = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(JournalContent("Transaction analysis."))
            .with_transaction_id("transaction-id-1")
            .build()
        )

        general_entry = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(JournalContent("General market thoughts."))
            .build()
        )

        assert transaction_entry.is_related_to_transaction() is True
        assert general_entry.is_related_to_transaction() is False

    def test_journal_entry_get_content_preview(self) -> None:
        """Should provide content preview for display."""
        short_entry = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(JournalContent("Short content."))
            .build()
        )

        long_entry = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(
                JournalContent(
                    "This is a very long journal entry that contains extensive "
                    + "market analysis and observations that should be truncated for "
                    + "preview purposes."
                )
            )
            .build()
        )

        assert short_entry.get_content_preview() == "Short content."
        long_preview = long_entry.get_content_preview(50)
        assert len(long_preview) <= 53  # 50 + "..."
        assert long_preview.endswith("...")

    def test_journal_entry_update_content(self) -> None:
        """Should be able to update entry content."""
        entry = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(JournalContent("Original content."))
            .build()
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
        entry = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(JournalContent("Test content."))
            .with_id(test_id)
            .build()
        )

        assert entry.id == test_id

    def test_journal_entry_id_immutability(self) -> None:
        """Should not be able to change ID after creation."""
        entry = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(JournalContent("Test content."))
            .with_id("test-id-1")
            .build()
        )

        # ID property should not have a setter
        with pytest.raises(AttributeError):
            entry.id = "different-id"  # type: ignore[misc]

    def test_journal_entry_from_persistence(self) -> None:
        """Should create journal entry from persistence with existing ID."""
        test_id = "persistence-id-456"
        entry = (
            JournalEntry.Builder()
            .with_id(test_id)
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(JournalContent("Test content from database."))
            .with_portfolio_id("portfolio-id-1")
            .build()
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
        """Test that journal entry equality returns False for non-JournalEntry
        objects."""
        entry = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(JournalContent("Test content"))
            .with_portfolio_id("portfolio-1")
            .with_stock_id("stock-1")
            .build()
        )

        # Test equality with different types - should return False (covers line 103)
        assert entry != "not a journal entry"
        assert entry != 123
        assert entry is not None
        assert entry != {
            "entry_date": datetime(2024, 1, 15, tzinfo=UTC),
            "content": "Test content",
        }


class TestJournalEntryBuilder:
    """Test cases for JournalEntry.Builder pattern."""

    def test_builder_creates_journal_entry_with_all_fields(self) -> None:
        """Test that Builder can create a journal entry with all fields."""
        entry = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(JournalContent("Test observation"))
            .with_portfolio_id("portfolio-1")
            .with_stock_id("stock-2")
            .with_transaction_id("transaction-3")
            .with_id("entry-id")
            .build()
        )

        assert entry.entry_date == datetime(2024, 1, 15, tzinfo=UTC)
        assert entry.content.value == "Test observation"
        assert entry.portfolio_id == "portfolio-1"
        assert entry.stock_id == "stock-2"
        assert entry.transaction_id == "transaction-3"
        assert entry.id == "entry-id"

    def test_builder_creates_journal_entry_with_minimal_fields(self) -> None:
        """Test that Builder can create a journal entry with only required fields."""
        entry = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(JournalContent("Minimal entry"))
            .build()
        )

        assert entry.entry_date == datetime(2024, 1, 15, tzinfo=UTC)
        assert entry.content.value == "Minimal entry"
        assert entry.portfolio_id is None
        assert entry.stock_id is None
        assert entry.transaction_id is None

    def test_builder_raises_error_when_required_fields_missing(self) -> None:
        """Test that Builder raises error when required fields are missing."""
        # Missing entry_date
        with pytest.raises(ValueError, match="Entry date is required"):
            _ = JournalEntry.Builder().with_content(JournalContent("Test")).build()

        # Missing content
        with pytest.raises(ValueError, match="Content is required"):
            _ = (
                JournalEntry.Builder()
                .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
                .build()
            )

    def test_builder_validates_portfolio_id(self) -> None:
        """Test that Builder validates portfolio_id."""
        builder = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(JournalContent("Test"))
        )

        # Empty string should raise error
        with pytest.raises(ValueError, match="Portfolio ID must be a non-empty string"):
            _ = builder.with_portfolio_id("").build()

    def test_builder_validates_stock_id(self) -> None:
        """Test that Builder validates stock_id."""
        builder = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(JournalContent("Test"))
        )

        # Empty string should raise error
        with pytest.raises(ValueError, match="Stock ID must be a non-empty string"):
            _ = builder.with_stock_id("").build()

    def test_builder_validates_transaction_id(self) -> None:
        """Test that Builder validates transaction_id."""
        builder = (
            JournalEntry.Builder()
            .with_entry_date(datetime(2024, 1, 15, tzinfo=UTC))
            .with_content(JournalContent("Test"))
        )

        # Empty string should raise error
        with pytest.raises(
            ValueError, match="Transaction ID must be a non-empty string"
        ):
            _ = builder.with_transaction_id("").build()

    def test_builder_method_chaining(self) -> None:
        """Test that all builder methods return self for chaining."""
        builder = JournalEntry.Builder()

        assert builder.with_entry_date(datetime(2024, 1, 15, tzinfo=UTC)) is builder
        assert builder.with_content(JournalContent("Test")) is builder
        assert builder.with_portfolio_id("p1") is builder
        assert builder.with_stock_id("s1") is builder
        assert builder.with_transaction_id("t1") is builder
        assert builder.with_id("id1") is builder
