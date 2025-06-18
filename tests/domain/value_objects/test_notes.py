"""
Tests for Notes value object.

Following TDD approach - these tests define the expected behavior
of the Notes value object with validation.
"""

import pytest

from domain.value_objects.notes import Notes


class TestNotes:
    """Test suite for Notes value object."""

    def test_create_notes_with_valid_content(self):
        """Should create Notes with valid content."""
        notes = Notes("Great company with strong fundamentals")

        assert notes.value == "Great company with strong fundamentals"
        assert str(notes) == "Great company with strong fundamentals"

    def test_create_notes_with_empty_string(self):
        """Should allow creating Notes with empty string."""
        notes = Notes("")

        assert notes.value == ""
        assert str(notes) == ""

    def test_create_notes_with_whitespace_only(self):
        """Should strip whitespace and allow empty result."""
        notes = Notes("   ")

        assert notes.value == ""
        assert str(notes) == ""

    def test_create_notes_strips_whitespace(self):
        """Should strip leading and trailing whitespace."""
        notes = Notes("  Great company  ")

        assert notes.value == "Great company"
        assert str(notes) == "Great company"

    def test_create_notes_with_maximum_length(self):
        """Should allow notes with maximum length (1000 chars)."""
        long_notes = "A" * 1000
        notes = Notes(long_notes)

        assert notes.value == long_notes
        assert len(notes.value) == 1000

    def test_create_notes_exceeding_maximum_length_raises_error(self):
        """Should raise error for notes exceeding 1000 characters."""
        too_long_notes = "A" * 1001

        with pytest.raises(ValueError, match="Notes cannot exceed 1000 characters"):
            Notes(too_long_notes)

    def test_notes_equality(self):
        """Should compare Notes objects by value."""
        notes1 = Notes("Great company")
        notes2 = Notes("Great company")
        notes3 = Notes("Poor performance")

        assert notes1 == notes2
        assert notes1 != notes3
        assert notes2 != notes3

    def test_notes_hash(self):
        """Should be hashable based on value."""
        notes1 = Notes("Great company")
        notes2 = Notes("Great company")
        notes3 = Notes("Poor performance")

        assert hash(notes1) == hash(notes2)

        # Should be usable in sets
        notes_set = {notes1, notes2, notes3}
        assert len(notes_set) == 2  # notes1 and notes2 are the same

    def test_notes_immutability(self):
        """Should be immutable."""
        notes = Notes("Great company")

        # Should not have setters or mutation methods
        assert not hasattr(notes, "set_value")
        assert not hasattr(notes, "update")

        # The value attribute should be read-only
        with pytest.raises(AttributeError):
            notes.value = "Poor performance"

    def test_notes_repr(self):
        """Should have meaningful repr representation."""
        notes = Notes("Great company")

        assert repr(notes) == "Notes('Great company')"

    def test_notes_has_content(self):
        """Should provide method to check if notes have content."""
        notes_with_content = Notes("Some content")
        notes_empty = Notes("")
        notes_whitespace = Notes("   ")

        assert notes_with_content.has_content() == True
        assert notes_empty.has_content() == False
        assert notes_whitespace.has_content() == False
