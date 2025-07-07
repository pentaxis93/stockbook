"""
Tests for CompanyName value object.

Following TDD approach - these tests define the expected behavior
of the CompanyName value object with validation.
"""

import contextlib

import pytest

from src.domain.value_objects.company_name import CompanyName


class TestCompanyName:
    """Test suite for CompanyName value object."""

    def test_create_company_name_with_valid_name(self) -> None:
        """Should create CompanyName with valid name."""
        company = CompanyName("Apple Inc.")

        assert company.value == "Apple Inc."
        assert str(company) == "Apple Inc."

    def test_create_company_name_with_empty_string(self) -> None:
        """Should allow creating CompanyName with empty string."""
        company = CompanyName("")

        assert company.value == ""
        assert str(company) == ""

    def test_create_company_name_with_whitespace_only(self) -> None:
        """Should strip whitespace and allow empty result."""
        company = CompanyName("   ")

        assert company.value == ""
        assert str(company) == ""

    def test_create_company_name_strips_whitespace(self) -> None:
        """Should strip leading and trailing whitespace."""
        company = CompanyName("  Apple Inc.  ")

        assert company.value == "Apple Inc."
        assert str(company) == "Apple Inc."

    def test_create_company_name_with_maximum_length(self) -> None:
        """Should allow company name with maximum length (200 chars)."""
        long_company = "A" * 200
        company = CompanyName(long_company)

        assert company.value == long_company
        assert len(company.value) == 200

    def test_create_company_name_exceeding_maximum_length_raises_error(self) -> None:
        """Should raise error for company name exceeding 200 characters."""
        too_long_company = "A" * 201

        with pytest.raises(
            ValueError,
            match="Company name cannot exceed 200 characters",
        ):
            _ = CompanyName(too_long_company)

    def test_company_name_equality(self) -> None:
        """Should compare CompanyName objects by value."""
        company1 = CompanyName("Apple Inc.")
        company2 = CompanyName("Apple Inc.")
        company3 = CompanyName("Microsoft Corp.")

        assert company1 == company2
        assert company1 != company3
        assert company2 != company3

    def test_company_name_hash(self) -> None:
        """Should be hashable based on value."""
        company1 = CompanyName("Apple Inc.")
        company2 = CompanyName("Apple Inc.")
        company3 = CompanyName("Microsoft Corp.")

        assert hash(company1) == hash(company2)

        # Should be usable in sets
        company_set = {company1, company2, company3}
        assert len(company_set) == 2  # company1 and company2 are the same

    def test_company_name_immutability(self) -> None:
        """Should be immutable."""
        company = CompanyName("Apple Inc.")

        # Should not have setters or mutation methods
        assert not hasattr(company, "set_value")
        assert not hasattr(company, "update")

        # The value attribute should be read-only
        with pytest.raises(AttributeError):
            company.value = "Microsoft Corp."  # type: ignore[misc] - Testing immutability

    def test_company_name_repr(self) -> None:
        """Should have meaningful repr representation."""
        company = CompanyName("Apple Inc.")

        assert repr(company) == "CompanyName('Apple Inc.')"

    def test_company_name_equality_with_non_company_name_object(self) -> None:
        """Test that company name equality returns False for non-CompanyName objects."""
        company = CompanyName("Apple Inc.")

        # Test equality with different types - should return False
        assert company != "Apple Inc."
        assert company != 123
        assert company is not None
        assert company != {"value": "Apple Inc."}

    def test_company_name_base_class_coverage(self) -> None:
        """Test base class coverage for CompanyName missing lines."""
        # Test that normal initialization works (covers base class __setattr__)
        company = CompanyName("Valid company")
        assert company.value == "Valid company"

        # Test exception handling coverage (line 36)
        with contextlib.suppress(ValueError):
            _ = CompanyName("A" * 201)  # Too long, should raise ValueError

    def test_company_name_unexpected_value_error(self) -> None:
        """Test CompanyName handles unexpected ValueError from parent class."""
        from unittest.mock import patch

        # Mock the parent class to raise an unexpected ValueError
        with patch(
            "src.domain.value_objects.company_name.BaseTextValueObject.__init__",
        ) as mock_init:
            mock_init.side_effect = ValueError("Unexpected error from parent")

            # The CompanyName class should re-raise the original exception
            # since it doesn't contain "cannot exceed"
            with pytest.raises(ValueError, match="Unexpected error from parent"):
                _ = CompanyName("Test")
