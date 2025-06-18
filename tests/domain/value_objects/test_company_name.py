"""
Tests for CompanyName value object.

Following TDD approach - these tests define the expected behavior
of the CompanyName value object with validation.
"""

import pytest

from domain.value_objects.company_name import CompanyName


class TestCompanyName:
    """Test suite for CompanyName value object."""

    def test_create_company_name_with_valid_name(self):
        """Should create CompanyName with valid name."""
        name = CompanyName("Apple Inc.")

        assert name.value == "Apple Inc."
        assert str(name) == "Apple Inc."

    def test_create_company_name_with_empty_string(self):
        """Should allow creating CompanyName with empty string."""
        name = CompanyName("")

        assert name.value == ""
        assert str(name) == ""

    def test_create_company_name_with_whitespace_only(self):
        """Should strip whitespace and allow empty result."""
        name = CompanyName("   ")

        assert name.value == ""
        assert str(name) == ""

    def test_create_company_name_strips_whitespace(self):
        """Should strip leading and trailing whitespace."""
        name = CompanyName("  Apple Inc.  ")

        assert name.value == "Apple Inc."
        assert str(name) == "Apple Inc."

    def test_create_company_name_with_maximum_length(self):
        """Should allow company name with maximum length (200 chars)."""
        long_name = "A" * 200
        name = CompanyName(long_name)

        assert name.value == long_name
        assert len(name.value) == 200

    def test_create_company_name_exceeding_maximum_length_raises_error(self):
        """Should raise error for company name exceeding 200 characters."""
        too_long_name = "A" * 201

        with pytest.raises(
            ValueError, match="Company name cannot exceed 200 characters"
        ):
            CompanyName(too_long_name)

    def test_company_name_equality(self):
        """Should compare CompanyName objects by value."""
        name1 = CompanyName("Apple Inc.")
        name2 = CompanyName("Apple Inc.")
        name3 = CompanyName("Microsoft Corp.")

        assert name1 == name2
        assert name1 != name3
        assert name2 != name3

    def test_company_name_hash(self):
        """Should be hashable based on value."""
        name1 = CompanyName("Apple Inc.")
        name2 = CompanyName("Apple Inc.")
        name3 = CompanyName("Microsoft Corp.")

        assert hash(name1) == hash(name2)

        # Should be usable in sets
        name_set = {name1, name2, name3}
        assert len(name_set) == 2  # name1 and name2 are the same

    def test_company_name_immutability(self):
        """Should be immutable."""
        name = CompanyName("Apple Inc.")

        # Should not have setters or mutation methods
        assert not hasattr(name, "set_value")
        assert not hasattr(name, "update")

        # The value attribute should be read-only
        with pytest.raises(AttributeError):
            name.value = "Microsoft Corp."

    def test_company_name_repr(self):
        """Should have meaningful repr representation."""
        name = CompanyName("Apple Inc.")

        assert repr(name) == "CompanyName('Apple Inc.')"
