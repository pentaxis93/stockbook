"""
Tests for JournalEntryEntity domain entity.

Following TDD approach with focus on value object purity and business logic.
Tests define expected behavior before implementation.
"""

from datetime import date

import pytest

from src.domain.entities.journal_entry_entity import JournalEntryEntity


class TestJournalEntryEntity:
    """Test JournalEntryEntity domain entity with value objects and business logic."""

    def test_create_journal_entry_with_value_objects(self):
        """Test creating a journal entry with all value objects."""
        from src.domain.value_objects import JournalContent

        entry = JournalEntryEntity(
            entry_date=date(2024, 1, 15),
            content=JournalContent(
                "This is an important market observation about the current trends."
            ),
            portfolio_id=1,
            stock_id=2,
            transaction_id=3,
        )

        assert entry.entry_date == date(2024, 1, 15)
        assert (
            entry.content.value
            == "This is an important market observation about the current trends."
        )
        assert entry.portfolio_id == 1
        assert entry.stock_id == 2
        assert entry.transaction_id == 3

    def test_create_journal_entry_with_minimal_data(self):
        """Test creating journal entry with only required fields."""
        from src.domain.value_objects import JournalContent

        entry = JournalEntryEntity(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Simple entry content."),
        )

        assert entry.entry_date == date(2024, 1, 15)
        assert entry.content.value == "Simple entry content."
        assert entry.portfolio_id is None
        assert entry.stock_id is None
        assert entry.transaction_id is None

    def test_create_journal_entry_with_invalid_portfolio_id_raises_error(self):
        """Should raise error for invalid portfolio ID."""
        from src.domain.value_objects import JournalContent

        with pytest.raises(ValueError, match="Portfolio ID must be positive"):
            JournalEntryEntity(
                entry_date=date(2024, 1, 15),
                content=JournalContent("Test content."),
                portfolio_id=0,  # Invalid
            )

    def test_create_journal_entry_with_invalid_stock_id_raises_error(self):
        """Should raise error for invalid stock ID."""
        from src.domain.value_objects import JournalContent

        with pytest.raises(ValueError, match="Stock ID must be positive"):
            JournalEntryEntity(
                entry_date=date(2024, 1, 15),
                content=JournalContent("Test content."),
                stock_id=-1,  # Invalid
            )

    def test_create_journal_entry_with_invalid_transaction_id_raises_error(self):
        """Should raise error for invalid transaction ID."""
        from src.domain.value_objects import JournalContent

        with pytest.raises(ValueError, match="Transaction ID must be positive"):
            JournalEntryEntity(
                entry_date=date(2024, 1, 15),
                content=JournalContent("Test content."),
                transaction_id=0,  # Invalid
            )

    def test_create_journal_entry_with_invalid_content_raises_error(self):
        """Should raise error for invalid content through JournalContent value object."""
        from src.domain.value_objects import JournalContent

        with pytest.raises(ValueError, match="Journal content cannot be empty"):
            JournalContent("")  # Error happens at JournalContent construction

    def test_journal_entry_equality(self):
        """Should compare journal entries based on business identity (entry_date, content hash)."""
        from src.domain.value_objects import JournalContent

        entry1 = JournalEntryEntity(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Market observation about trends."),
        )

        entry2 = JournalEntryEntity(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Market observation about trends."),
            portfolio_id=1,  # Different metadata
        )

        entry3 = JournalEntryEntity(
            entry_date=date(2024, 1, 16),  # Different date
            content=JournalContent("Market observation about trends."),
        )

        assert entry1 == entry2  # Same date and content
        assert entry1 != entry3  # Different date

    def test_journal_entry_hash(self):
        """Should hash consistently based on business identity."""
        from src.domain.value_objects import JournalContent

        entry1 = JournalEntryEntity(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Market observation."),
        )

        entry2 = JournalEntryEntity(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Market observation."),
            portfolio_id=1,  # Different metadata
        )

        assert hash(entry1) == hash(entry2)  # Same date and content

    def test_journal_entry_string_representation(self):
        """Should have informative string representation."""
        from src.domain.value_objects import JournalContent

        entry = JournalEntryEntity(
            entry_date=date(2024, 1, 15),
            content=JournalContent(
                "This is a longer journal entry with significant market observations and analysis."
            ),
        )

        str_repr = str(entry)
        assert "2024-01-15" in str_repr
        assert "This is a longer journal entry with significant" in str_repr

    def test_journal_entry_repr(self):
        """Should have detailed repr representation."""
        from src.domain.value_objects import JournalContent

        entry = JournalEntryEntity(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Test content."),
        )

        expected = "JournalEntryEntity(date=2024-01-15)"
        assert repr(entry) == expected

    # Business behavior tests
    def test_journal_entry_is_related_to_portfolio(self):
        """Should check if entry is related to a portfolio."""
        from src.domain.value_objects import JournalContent

        portfolio_entry = JournalEntryEntity(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Portfolio analysis."),
            portfolio_id=1,
        )

        general_entry = JournalEntryEntity(
            entry_date=date(2024, 1, 15),
            content=JournalContent("General market thoughts."),
        )

        assert portfolio_entry.is_related_to_portfolio() is True
        assert general_entry.is_related_to_portfolio() is False

    def test_journal_entry_is_related_to_stock(self):
        """Should check if entry is related to a stock."""
        from src.domain.value_objects import JournalContent

        stock_entry = JournalEntryEntity(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Stock analysis."),
            stock_id=1,
        )

        general_entry = JournalEntryEntity(
            entry_date=date(2024, 1, 15),
            content=JournalContent("General market thoughts."),
        )

        assert stock_entry.is_related_to_stock() is True
        assert general_entry.is_related_to_stock() is False

    def test_journal_entry_is_related_to_transaction(self):
        """Should check if entry is related to a transaction."""
        from src.domain.value_objects import JournalContent

        transaction_entry = JournalEntryEntity(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Transaction analysis."),
            transaction_id=1,
        )

        general_entry = JournalEntryEntity(
            entry_date=date(2024, 1, 15),
            content=JournalContent("General market thoughts."),
        )

        assert transaction_entry.is_related_to_transaction() is True
        assert general_entry.is_related_to_transaction() is False

    def test_journal_entry_get_content_preview(self):
        """Should provide content preview for display."""
        from src.domain.value_objects import JournalContent

        short_entry = JournalEntryEntity(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Short content."),
        )

        long_entry = JournalEntryEntity(
            entry_date=date(2024, 1, 15),
            content=JournalContent(
                "This is a very long journal entry that contains extensive market analysis and observations that should be truncated for preview purposes."
            ),
        )

        assert short_entry.get_content_preview() == "Short content."
        long_preview = long_entry.get_content_preview(50)
        assert len(long_preview) <= 53  # 50 + "..."
        assert long_preview.endswith("...")

    def test_journal_entry_update_content(self):
        """Should be able to update entry content."""
        from src.domain.value_objects import JournalContent

        entry = JournalEntryEntity(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Original content."),
        )

        # Update with JournalContent value object
        entry.update_content(JournalContent("Updated content."))
        assert entry.content.value == "Updated content."

        # Update with string (should be converted to JournalContent)
        entry.update_content("String content.")
        assert entry.content.value == "String content."

    def test_journal_entry_set_id(self):
        """Should allow setting entry ID."""
        from src.domain.value_objects import JournalContent

        entry = JournalEntryEntity(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Test content."),
        )

        entry.set_id(123)
        assert entry.id == 123

    def test_journal_entry_set_id_with_invalid_id_raises_error(self):
        """Should raise error when setting invalid ID."""
        from src.domain.value_objects import JournalContent

        entry = JournalEntryEntity(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Test content."),
        )

        with pytest.raises(ValueError, match="ID must be a positive integer"):
            entry.set_id(0)

    def test_journal_entry_set_id_when_already_set_raises_error(self):
        """Should raise error when trying to change existing ID."""
        from src.domain.value_objects import JournalContent

        entry = JournalEntryEntity(
            entry_date=date(2024, 1, 15),
            content=JournalContent("Test content."),
            entry_id=123,
        )

        with pytest.raises(ValueError, match="ID is already set and cannot be changed"):
            entry.set_id(456)


class TestJournalContent:
    """Test JournalContent value object validation."""

    def test_valid_journal_content_accepted(self):
        """Test that valid journal content is accepted."""
        from src.domain.value_objects import JournalContent

        valid_contents = [
            "Short entry.",
            "This is a longer journal entry with more detailed analysis.",
            "A" * 5000,  # Long but valid content
        ]
        for content in valid_contents:
            journal_content = JournalContent(content)
            assert journal_content.value == content

    def test_journal_content_strips_whitespace(self):
        """Test that journal content strips leading/trailing whitespace."""
        from src.domain.value_objects import JournalContent

        content = JournalContent("  Market analysis with spaces  ")
        assert content.value == "Market analysis with spaces"

    def test_empty_journal_content_rejected(self):
        """Test that empty journal content is rejected."""
        from src.domain.value_objects import JournalContent

        empty_contents = ["", "   ", "\t", "\n"]
        for empty_content in empty_contents:
            with pytest.raises(ValueError, match="Journal content cannot be empty"):
                JournalContent(empty_content)

    def test_too_long_journal_content_rejected(self):
        """Test that excessively long journal content is rejected."""
        from src.domain.value_objects import JournalContent

        long_content = "A" * 10001  # Max is 10000 characters
        with pytest.raises(
            ValueError, match="Journal content cannot exceed 10000 characters"
        ):
            JournalContent(long_content)

    def test_max_length_journal_content_accepted(self):
        """Test that journal content at max length is accepted."""
        from src.domain.value_objects import JournalContent

        max_length_content = "A" * 10000  # Exactly 10000 characters
        journal_content = JournalContent(max_length_content)
        assert journal_content.value == max_length_content
        assert len(journal_content.value) == 10000
