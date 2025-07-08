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
        industry = IndustryGroup("Software")

        assert industry.value == "Software"
        assert str(industry) == "Software"

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
        industry = IndustryGroup("  Software  ")

        assert industry.value == "Software"
        assert str(industry) == "Software"

    def test_create_industry_group_with_arbitrary_value_raises_error(self) -> None:
        """Should raise error for arbitrary values that aren't in mapping."""
        # Invalid industry groups are not allowed
        arbitrary_value = "Some Custom Industry"
        with pytest.raises(
            ValueError,
            match="Invalid industry group 'Some Custom Industry'",
        ):
            _ = IndustryGroup(arbitrary_value)

    def test_create_industry_group_exceeding_maximum_length_raises_error(self) -> None:
        """Should raise error for industry group exceeding 100 characters."""
        too_long_industry = "A" * 101

        with pytest.raises(
            ValueError,
            match="Industry group cannot exceed 100 characters",
        ):
            _ = IndustryGroup(too_long_industry)

    def test_industry_group_equality(self) -> None:
        """Should compare IndustryGroup objects by value."""
        industry1 = IndustryGroup("Software")
        industry2 = IndustryGroup("Software")
        industry3 = IndustryGroup("Pharmaceuticals")

        assert industry1 == industry2
        assert industry1 != industry3
        assert industry2 != industry3

    def test_industry_group_hash(self) -> None:
        """Should be hashable based on value."""
        industry1 = IndustryGroup("Software")
        industry2 = IndustryGroup("Software")
        industry3 = IndustryGroup("Pharmaceuticals")

        assert hash(industry1) == hash(industry2)

        # Should be usable in sets
        industry_set = {industry1, industry2, industry3}
        assert len(industry_set) == 2  # industry1 and industry2 are the same

    def test_industry_group_immutability(self) -> None:
        """Should be immutable."""
        industry = IndustryGroup("Software")

        # Should not have setters or mutation methods
        assert not hasattr(industry, "set_value")
        assert not hasattr(industry, "update")

        # The value attribute should be read-only
        with pytest.raises(AttributeError):
            industry.value = "Pharmaceuticals"  # type: ignore[misc] - Testing immutability

    def test_industry_group_repr(self) -> None:
        """Should have meaningful repr representation."""
        industry = IndustryGroup("Software")

        assert repr(industry) == "IndustryGroup('Software')"

    def test_industry_group_equality_with_non_industry_group_object(self) -> None:
        """Test that industry group equality returns False for non-IndustryGroup
        objects."""
        industry = IndustryGroup("Software")

        # Test equality with different types - should return False
        assert industry != "Software"
        assert industry != 123
        assert industry is not None
        assert industry != {"value": "Software"}

    def test_industry_group_base_class_coverage(self) -> None:
        """Test base class coverage for IndustryGroup missing lines."""
        # Test that normal initialization works (covers line 69 - super().__setattr__)
        industry = IndustryGroup("Software")
        assert industry.value == "Software"

        # The __setattr__ is called during initialization to set _value
        # This test ensures the initialization path is covered

    def test_industry_group_setattr_during_initialization(self) -> None:
        """Test that __setattr__ allows setting attributes during initialization."""
        # Create a partially initialized object
        industry = object.__new__(IndustryGroup)

        # This exercises the super().__setattr__ branch (line 69)
        industry.test_attr = "test_value"

        # Now properly initialize the object
        IndustryGroup.__init__(industry, "Software")
        assert industry.value == "Software"

    def test_industry_group_knows_its_sector(self) -> None:
        """Test that each industry group knows which sector it belongs to."""
        # Software belongs to Technology
        software = IndustryGroup("Software")
        assert software.sector == "Technology"

        # Pharmaceuticals belongs to Healthcare
        pharma = IndustryGroup("Pharmaceuticals")
        assert pharma.sector == "Healthcare"

        # Banks belongs to Financial Services
        banks = IndustryGroup("Banks")
        assert banks.sector == "Financial Services"

    def test_industry_group_validates_with_sector(self) -> None:
        """Test validation when sector is provided."""
        # Valid combination
        software = IndustryGroup("Software", sector="Technology")
        assert software.value == "Software"
        assert software.sector == "Technology"

        # Invalid combination should raise error
        with pytest.raises(
            ValueError,
            match=(
                "Industry Group 'Software' belongs to sector 'Technology', "
                "not 'Healthcare'"
            ),
        ):
            _ = IndustryGroup("Software", sector="Healthcare")

    def test_invalid_industry_group_raises_error(self) -> None:
        """Test that invalid industry groups raise an error."""
        # Invalid industry group should always raise error
        with pytest.raises(
            ValueError,
            match="Invalid industry group 'InvalidIndustry'",
        ):
            _ = IndustryGroup("InvalidIndustry")

        # Should also fail when sector is provided
        with pytest.raises(
            ValueError,
            match="Invalid industry group 'InvalidIndustry'",
        ):
            _ = IndustryGroup("InvalidIndustry", sector="Technology")

    def test_industry_group_with_valid_sector_creates_successfully(self) -> None:
        """Test that valid sector-industry combinations work."""
        # Test various valid combinations
        valid_combinations = [
            ("Software", "Technology"),
            ("Pharmaceuticals", "Healthcare"),
            ("Banks", "Financial Services"),
            ("Consumer Electronics", "Consumer Goods"),
            ("Oil & Gas", "Energy"),
            ("Manufacturing", "Industrial"),
        ]

        for industry_name, sector_name in valid_combinations:
            industry = IndustryGroup(industry_name, sector=sector_name)
            assert industry.value == industry_name
            assert industry.sector == sector_name
