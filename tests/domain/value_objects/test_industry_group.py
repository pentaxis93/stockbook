"""
Tests for IndustryGroup value object.

Following TDD approach - these tests define the expected behavior
of the IndustryGroup value object with validation.
"""

import pytest

from src.domain.value_objects.industry_group import IndustryGroup


class TestIndustryGroup:
    """Test suite for IndustryGroup value object."""

    def test_create_industry_group_with_valid_name(self) -> None:
        """Should create IndustryGroup with valid name."""
        industry = IndustryGroup("Technology")

        assert industry.value == "Technology"
        assert str(industry) == "Technology"

    def test_create_industry_group_with_empty_string(self) -> None:
        """Should allow creating IndustryGroup with empty string."""
        industry = IndustryGroup("")

        assert industry.value == ""
        assert str(industry) == ""

    def test_create_industry_group_with_whitespace_only(self) -> None:
        """Should strip whitespace and allow empty result."""
        industry = IndustryGroup("   ")

        assert industry.value == ""
        assert str(industry) == ""

    def test_create_industry_group_strips_whitespace(self) -> None:
        """Should strip leading and trailing whitespace."""
        industry = IndustryGroup("  Technology  ")

        assert industry.value == "Technology"
        assert str(industry) == "Technology"

    def test_create_industry_group_with_maximum_length(self) -> None:
        """Should allow industry group with maximum length (100 chars)."""
        long_industry = "A" * 100
        industry = IndustryGroup(long_industry)

        assert industry.value == long_industry
        assert len(industry.value) == 100

    def test_create_industry_group_exceeding_maximum_length_raises_error(self) -> None:
        """Should raise error for industry group exceeding 100 characters."""
        too_long_industry = "A" * 101

        with pytest.raises(
            ValueError, match="Industry group cannot exceed 100 characters"
        ):
            IndustryGroup(too_long_industry)

    def test_industry_group_equality(self) -> None:
        """Should compare IndustryGroup objects by value."""
        industry1 = IndustryGroup("Technology")
        industry2 = IndustryGroup("Technology")
        industry3 = IndustryGroup("Healthcare")

        assert industry1 == industry2
        assert industry1 != industry3
        assert industry2 != industry3

    def test_industry_group_hash(self) -> None:
        """Should be hashable based on value."""
        industry1 = IndustryGroup("Technology")
        industry2 = IndustryGroup("Technology")
        industry3 = IndustryGroup("Healthcare")

        assert hash(industry1) == hash(industry2)

        # Should be usable in sets
        industry_set = {industry1, industry2, industry3}
        assert len(industry_set) == 2  # industry1 and industry2 are the same

    def test_industry_group_immutability(self) -> None:
        """Should be immutable."""
        industry = IndustryGroup("Technology")

        # Should not have setters or mutation methods
        assert not hasattr(industry, "set_value")
        assert not hasattr(industry, "update")

        # The value attribute should be read-only
        with pytest.raises(AttributeError):
            industry.value = "Healthcare"  # type: ignore[misc] - Testing immutability

    def test_industry_group_repr(self) -> None:
        """Should have meaningful repr representation."""
        industry = IndustryGroup("Technology")

        assert repr(industry) == "IndustryGroup('Technology')"
