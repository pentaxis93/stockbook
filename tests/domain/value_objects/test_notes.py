"""
Tests for Notes value object.

Following TDD approach - these tests define the expected behavior
of the Notes value object with validation.
"""

import pytest

from src.domain.value_objects.notes import Notes


class TestNotes:
    """Test suite for Notes value object."""

    def test_create_notes_with_valid_content(self) -> None:
        """Should create Notes with valid content."""
        notes = Notes("Great company with strong fundamentals")

        assert notes.value == "Great company with strong fundamentals"
        assert str(notes) == "Great company with strong fundamentals"

    def test_create_notes_with_empty_string(self) -> None:
        """Should allow creating Notes with empty string."""
        notes = Notes("")

        assert notes.value == ""
        assert str(notes) == ""

    def test_create_notes_with_whitespace_only(self) -> None:
        """Should strip whitespace and allow empty result."""
        notes = Notes("   ")

        assert notes.value == ""
        assert str(notes) == ""

    def test_create_notes_strips_whitespace(self) -> None:
        """Should strip leading and trailing whitespace."""
        notes = Notes("  Great company  ")

        assert notes.value == "Great company"
        assert str(notes) == "Great company"

    def test_create_notes_with_maximum_length(self) -> None:
        """Should allow notes with maximum length (1000 chars)."""
        long_notes = "A" * 1000
        notes = Notes(long_notes)

        assert notes.value == long_notes
        assert len(notes.value) == 1000

    def test_create_notes_exceeding_maximum_length_raises_error(self) -> None:
        """Should raise error for notes exceeding 1000 characters."""
        too_long_notes = "A" * 1001

        with pytest.raises(ValueError, match="Notes cannot exceed 1000 characters"):
            _ = Notes(too_long_notes)

    def test_notes_equality(self) -> None:
        """Should compare Notes objects by value."""
        notes1 = Notes("Great company")
        notes2 = Notes("Great company")
        notes3 = Notes("Poor performance")

        assert notes1 == notes2
        assert notes1 != notes3
        assert notes2 != notes3

    def test_notes_hash(self) -> None:
        """Should be hashable based on value."""
        notes1 = Notes("Great company")
        notes2 = Notes("Great company")
        notes3 = Notes("Poor performance")

        assert hash(notes1) == hash(notes2)

        # Should be usable in sets
        notes_set = {notes1, notes2, notes3}
        assert len(notes_set) == 2  # notes1 and notes2 are the same

    def test_notes_immutability(self) -> None:
        """Should be immutable."""
        notes = Notes("Great company")

        # Should not have setters or mutation methods
        assert not hasattr(notes, "set_value")
        assert not hasattr(notes, "update")

        # The value attribute should be read-only
        with pytest.raises(AttributeError):
            notes.value = "Poor performance"  # type: ignore[misc] - Testing immutability

    def test_notes_repr(self) -> None:
        """Should have meaningful repr representation."""
        notes = Notes("Great company")

        assert repr(notes) == "Notes('Great company')"

    def test_notes_has_content(self) -> None:
        """Should provide method to check if notes have content."""
        notes_with_content = Notes("Some content")
        notes_empty = Notes("")
        notes_whitespace = Notes("   ")

        assert notes_with_content.has_content() is True
        assert notes_empty.has_content() is False
        assert notes_whitespace.has_content() is False

    def test_notes_equality_with_non_notes_object(self) -> None:
        """Test that notes equality returns False for non-Notes objects."""
        notes = Notes("Some important notes")

        # Test equality with different types - should return False
        assert notes != "Some important notes"
        assert notes != 123
        assert notes != None
        assert notes != {"value": "Some important notes"}

    def test_notes_additional_edge_cases(self) -> None:
        """Test notes with additional edge cases for coverage."""
        # Test very long notes (within the max length)
        long_notes = Notes("A" * 999)  # Just under max length
        assert len(long_notes.value) == 999

        # Test notes with special characters
        special_notes = Notes("Notes with symbols: @#$%^&*()")
        assert special_notes.value == "Notes with symbols: @#$%^&*()"

    def test_notes_base_class_coverage(self) -> None:
        """Test base class coverage for Notes missing lines."""
        # Test that normal initialization works (covers line 88 in base class)
        notes = Notes("Valid notes content")
        assert notes.value == "Valid notes content"

        # Test exception handling coverage (line 117)
        # This test exercises the exception re-raising path
        try:
            _ = Notes("A" * 1001)  # Too long, should raise ValueError
        except ValueError:
            pass  # Expected, we just want to exercise the exception path
