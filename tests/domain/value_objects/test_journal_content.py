"""
Tests for JournalContent value object.

This module tests the JournalContent value object which encapsulates
journal entry content validation and business logic for journal management.
"""

import pytest

from src.domain.value_objects.journal_content import JournalContent


class TestJournalContentCreation:
    """Test JournalContent creation and validation."""

    def test_create_valid_journal_content(self) -> None:
        """Should create valid journal content."""
        content = JournalContent(
            "This is a valid journal entry about my trading strategy."
        )

        assert (
            content.value == "This is a valid journal entry about my trading strategy."
        )
        assert content.has_content() is True

    def test_create_with_whitespace_strips_whitespace(self) -> None:
        """Should strip leading and trailing whitespace."""
        content_with_whitespace = JournalContent(
            "  Journal entry with whitespace  \n\t"
        )

        assert content_with_whitespace.value == "Journal entry with whitespace"

    def test_create_with_multiline_content(self) -> None:
        """Should handle multiline journal content."""
        multiline_text = """This is a multiline journal entry.

        Today I learned about portfolio diversification.
        Key points:
        1. Don't put all eggs in one basket
        2. Consider different sectors
        3. Monitor risk levels"""

        content = JournalContent(multiline_text)

        expected = """This is a multiline journal entry.

        Today I learned about portfolio diversification.
        Key points:
        1. Don't put all eggs in one basket
        2. Consider different sectors
        3. Monitor risk levels"""

        assert content.value == expected
        assert content.has_content() is True

    def test_create_with_empty_string_raises_error(self) -> None:
        """Should raise ValueError for empty journal content."""
        with pytest.raises(ValueError, match="Journal content cannot be empty"):
            _ = JournalContent("")

    def test_create_with_whitespace_only_raises_error(self) -> None:
        """Should raise ValueError for whitespace-only journal content."""
        with pytest.raises(ValueError, match="Journal content cannot be empty"):
            _ = JournalContent("   \n\t  ")

    def test_create_with_content_exceeding_max_length_raises_error(self) -> None:
        """Should raise ValueError for journal content exceeding maximum length."""
        long_content = "A" * (JournalContent.MAX_LENGTH + 1)

        with pytest.raises(
            ValueError, match="Journal content cannot exceed 10000 characters"
        ):
            _ = JournalContent(long_content)

    def test_create_at_max_length_boundary(self) -> None:
        """Should accept journal content at exactly maximum length."""
        max_length_content = "A" * JournalContent.MAX_LENGTH
        content = JournalContent(max_length_content)

        assert len(content.value) == JournalContent.MAX_LENGTH
        assert content.value == max_length_content

    def test_create_just_under_max_length(self) -> None:
        """Should accept journal content just under maximum length."""
        near_max_content = "A" * (JournalContent.MAX_LENGTH - 1)
        content = JournalContent(near_max_content)

        assert len(content.value) == JournalContent.MAX_LENGTH - 1
        assert content.value == near_max_content


class TestJournalContentBusinessLogic:
    """Test JournalContent business logic methods."""

    def test_get_preview_with_short_content(self) -> None:
        """Should return full content when shorter than preview length."""
        short_content = JournalContent("Short journal entry")

        preview = short_content.get_preview(50)
        assert preview == "Short journal entry"

    def test_get_preview_with_long_content_uses_default_length(self) -> None:
        """Should truncate content to default preview length (50 chars)."""
        long_content = JournalContent(
            "This is a very long journal entry that definitely exceeds fifty "
            + "characters in length"
        )

        preview = long_content.get_preview()
        # Should truncate at 50 chars and add "..."
        assert preview.endswith("...")
        assert len(preview) == 53  # 50 + "..."
        assert preview.startswith("This is a very long journal entry that definite")

    def test_get_preview_with_custom_length(self) -> None:
        """Should truncate content to custom preview length."""
        content = JournalContent("This is a journal entry that will be truncated")

        short_preview = content.get_preview(10)
        long_preview = content.get_preview(100)

        assert short_preview == "This is a ..."
        assert (
            long_preview == "This is a journal entry that will be truncated"
        )  # Full content

    def test_get_preview_with_zero_length(self) -> None:
        """Should handle zero length preview gracefully."""
        content = JournalContent("Any content")

        preview = content.get_preview(0)
        assert preview == "..."

    def test_word_count_with_simple_content(self) -> None:
        """Should count words correctly in simple content."""
        content = JournalContent("This is five words exactly")

        assert content.word_count() == 5

    def test_word_count_with_multiple_spaces(self) -> None:
        """Should handle multiple spaces between words."""
        content = JournalContent("Words   with    multiple     spaces")

        assert content.word_count() == 4

    def test_word_count_with_single_word(self) -> None:
        """Should count single word correctly."""
        content = JournalContent("SingleWord")

        assert content.word_count() == 1

    def test_word_count_with_newlines_and_tabs(self) -> None:
        """Should count words correctly across lines and tabs."""
        content = JournalContent("First\nSecond\tThird\n\nFourth")

        assert content.word_count() == 4

    def test_word_count_with_punctuation(self) -> None:
        """Should count words with punctuation correctly."""
        content = JournalContent("Hello, world! This is a test.")

        assert content.word_count() == 6

    def test_has_content_returns_true_for_valid_content(self) -> None:
        """Should return True for content with text."""
        content = JournalContent("Valid content")

        assert content.has_content() is True


class TestJournalContentEquality:
    """Test JournalContent equality and hashing."""

    def test_equal_journal_contents_are_equal(self) -> None:
        """Should be equal if journal contents have same value."""
        content1 = JournalContent("Same journal content")
        content2 = JournalContent("Same journal content")

        assert content1 == content2

    def test_equal_after_whitespace_normalization(self) -> None:
        """Should be equal after whitespace normalization."""
        content1 = JournalContent("Journal content")
        content2 = JournalContent("  Journal content  ")

        assert content1 == content2

    def test_different_journal_contents_are_not_equal(self) -> None:
        """Should not be equal if journal contents have different values."""
        content1 = JournalContent("First journal entry")
        content2 = JournalContent("Second journal entry")

        assert content1 != content2

    def test_journal_content_not_equal_to_other_types(self) -> None:
        """Should not be equal to non-JournalContent objects."""
        content = JournalContent("Journal content")

        assert content != "Journal content"
        assert content != 1
        assert content is not None
        assert content

    def test_journal_content_hashable(self) -> None:
        """Should be hashable for use in collections."""
        content1 = JournalContent("Same content")
        content2 = JournalContent("Same content")
        content3 = JournalContent("Different content")

        # Should be able to use in set
        content_set = {content1, content2, content3}
        assert len(content_set) == 2  # content1 and content2 should be same hash

        # Should be able to use as dict key
        content_dict = {content1: "first", content3: "second"}
        assert len(content_dict) == 2
        assert content_dict[content2] == "first"  # Should find content1's value


class TestJournalContentImmutability:
    """Test JournalContent immutability."""

    def test_value_property_is_readonly(self) -> None:
        """Should not be able to modify value after creation."""
        content = JournalContent("Original content")

        with pytest.raises(AttributeError):
            content.value = "Modified content"  # type: ignore[misc]

    def test_cannot_set_attributes_after_creation(self) -> None:
        """Should not be able to set new attributes after creation."""
        content = JournalContent("Journal content")

        with pytest.raises(AttributeError, match="JournalContent is immutable"):
            content.new_attribute = "value"

    def test_cannot_modify_value_attribute(self) -> None:
        """Should not be able to modify JournalContent after creation."""
        content = JournalContent("Journal content")

        with pytest.raises(AttributeError, match="JournalContent is immutable"):
            content.value = "Modified content"  # type: ignore[misc]


class TestJournalContentStringRepresentation:
    """Test JournalContent string representations."""

    def test_str_returns_content_value(self) -> None:
        """Should return journal content value as string."""
        content = JournalContent("My journal entry about trading")

        assert str(content) == "My journal entry about trading"

    def test_repr_returns_preview_representation(self) -> None:
        """Should return representation with content preview."""
        short_content = JournalContent("Short entry")
        long_content = JournalContent(
            "This is a very long journal entry that will definitely be "
            + "truncated in the repr"
        )

        assert repr(short_content) == "JournalContent('Short entry')"

        # For long content, check that it contains preview with ellipsis
        long_repr = repr(long_content)
        assert long_repr.startswith("JournalContent('")
        assert "..." in long_repr
        assert long_repr.endswith("')")

    def test_repr_preview_length_is_30_characters(self) -> None:
        """Should use 30 character preview in repr."""
        content = JournalContent("A" * 50)  # 50 A's

        repr_str = repr(content)
        # Should contain 30 A's + "..."
        assert "A" * 30 + "..." in repr_str


class TestJournalContentConstants:
    """Test JournalContent constants."""

    def test_max_length_constant(self) -> None:
        """Should have correct maximum length constant."""
        assert JournalContent.MAX_LENGTH == 10000

    def test_max_length_constant_is_enforced(self) -> None:
        """Should enforce the maximum length constant."""
        # This should work
        valid_content = JournalContent("A" * JournalContent.MAX_LENGTH)
        assert len(valid_content.value) == JournalContent.MAX_LENGTH

        # This should fail
        with pytest.raises(ValueError, match="Journal content cannot exceed"):
            _ = JournalContent("A" * (JournalContent.MAX_LENGTH + 1))


class TestJournalContentEdgeCases:
    """Test JournalContent edge cases and boundary conditions."""

    def test_create_with_unicode_content(self) -> None:
        """Should handle unicode characters correctly."""
        unicode_content = JournalContent(
            "Journal with émojis 📈 and ünïcödé characters 中文"
        )

        assert (
            unicode_content.value
            == "Journal with émojis 📈 and ünïcödé characters 中文"
        )
        assert unicode_content.has_content() is True

    def test_create_with_special_characters(self) -> None:
        """Should handle special characters correctly."""
        special_content = JournalContent(
            "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        )

        assert special_content.value == "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"

    def test_word_count_with_unicode_words(self) -> None:
        """Should count unicode words correctly."""
        unicode_content = JournalContent("English 中文 Español 日本語")

        assert unicode_content.word_count() == 4

    def test_preview_with_unicode_characters(self) -> None:
        """Should handle unicode characters in preview correctly."""
        unicode_content = JournalContent("🚀📈💰" * 20)  # 60 emoji characters

        preview = unicode_content.get_preview(10)
        assert len(preview) <= 13  # 10 + "..." or less due to unicode

    def test_create_with_very_long_words(self) -> None:
        """Should handle content with very long words."""
        long_word = "A" * 1000
        content = JournalContent(f"Start {long_word} end")

        assert content.word_count() == 3
        assert long_word in content.value

    def test_whitespace_normalization_edge_cases(self) -> None:
        """Should handle various whitespace normalization scenarios."""
        # Mixed whitespace types
        mixed_whitespace = JournalContent("\t\n  Content with mixed whitespace  \r\n")
        assert mixed_whitespace.value == "Content with mixed whitespace"

        # Only internal whitespace preserved
        internal_whitespace = JournalContent("  Word1    Word2  ")
        assert internal_whitespace.value == "Word1    Word2"

    def test_journal_content_equality_with_non_journal_content_object(self) -> None:
        """Test that journal content equality returns False for non-JournalContent
        objects."""
        content = JournalContent("Market analysis content")

        # Test equality with different types - should return False
        assert content != "Market analysis content"
        assert content != 123
        assert content is not None
        assert content != {"value": "Market analysis content"}

    def test_journal_content_base_class_coverage(self) -> None:
        """Test base class coverage for JournalContent missing lines."""
        # Test that normal initialization works (covers base class __setattr__)
        content = JournalContent("Valid content")
        assert content.value == "Valid content"

    def test_journal_content_unexpected_value_error(self) -> None:
        """Test JournalContent handles unexpected ValueError from parent class."""
        from unittest.mock import patch

        # Mock the parent class to raise an unexpected ValueError (not "cannot be
        # empty" or "cannot exceed")
        with patch(
            "src.domain.value_objects.journal_content.BaseTextValueObject.__init__"
        ) as mock_init:
            mock_init.side_effect = ValueError("Unexpected validation error")

            with pytest.raises(ValueError, match="Unexpected validation error"):
                _ = JournalContent("Test content")
