"""
Tests for PortfolioName value object.

This module tests the PortfolioName value object which encapsulates
portfolio name validation and business logic for portfolio management.
"""

from typing import Any

import pytest

from src.domain.value_objects.portfolio_name import PortfolioName


class TestPortfolioNameCreation:
    """Test PortfolioName creation and validation."""

    def test_create_valid_portfolio_name(self) -> None:
        """Should create valid portfolio name."""
        name = PortfolioName("My Investment Portfolio")

        assert name.value == "My Investment Portfolio"

    def test_create_with_simple_name(self) -> None:
        """Should create portfolio name with simple string."""
        simple_name = PortfolioName("Portfolio1")

        assert simple_name.value == "Portfolio1"

    def test_create_with_numbers_and_letters(self) -> None:
        """Should create portfolio name with alphanumeric characters."""
        alpha_numeric = PortfolioName("Portfolio 2023 v2")

        assert alpha_numeric.value == "Portfolio 2023 v2"

    def test_create_with_special_characters(self) -> None:
        """Should create portfolio name with special characters."""
        special_chars = PortfolioName("Growth & Income Portfolio (Conservative)")

        assert special_chars.value == "Growth & Income Portfolio (Conservative)"

    def test_create_with_whitespace_strips_whitespace(self) -> None:
        """Should strip leading and trailing whitespace."""
        name_with_whitespace = PortfolioName("  Portfolio Name  ")

        assert name_with_whitespace.value == "Portfolio Name"

    def test_create_with_tabs_and_newlines_strips_whitespace(self) -> None:
        """Should strip tabs and newlines."""
        name_with_tabs = PortfolioName("\t\nPortfolio Name\n\t")

        assert name_with_tabs.value == "Portfolio Name"

    def test_create_at_max_length_boundary(self) -> None:
        """Should accept portfolio name at exactly maximum length."""
        max_length_name = "A" * PortfolioName.MAX_LENGTH
        name = PortfolioName(max_length_name)

        assert len(name.value) == PortfolioName.MAX_LENGTH
        assert name.value == max_length_name

    def test_create_just_under_max_length(self) -> None:
        """Should accept portfolio name just under maximum length."""
        near_max_name = "A" * (PortfolioName.MAX_LENGTH - 1)
        name = PortfolioName(near_max_name)

        assert len(name.value) == PortfolioName.MAX_LENGTH - 1
        assert name.value == near_max_name

    def test_create_with_empty_string_raises_error(self) -> None:
        """Should raise ValueError for empty portfolio name."""
        with pytest.raises(ValueError, match="Portfolio name cannot be empty"):
            PortfolioName("")

    def test_create_with_whitespace_only_raises_error(self) -> None:
        """Should raise ValueError for whitespace-only portfolio name."""
        with pytest.raises(ValueError, match="Portfolio name cannot be empty"):
            PortfolioName("   \n\t  ")

    def test_create_exceeding_max_length_raises_error(self) -> None:
        """Should raise ValueError for portfolio name exceeding maximum length."""
        long_name = "A" * (PortfolioName.MAX_LENGTH + 1)

        with pytest.raises(
            ValueError, match="Portfolio name cannot exceed 100 characters"
        ):
            PortfolioName(long_name)

    def test_create_with_much_longer_name_raises_error(self) -> None:
        """Should raise ValueError for much longer portfolio name."""
        very_long_name = "A" * 200

        with pytest.raises(
            ValueError, match="Portfolio name cannot exceed 100 characters"
        ):
            PortfolioName(very_long_name)


class TestPortfolioNameEquality:
    """Test PortfolioName equality and hashing."""

    def test_equal_portfolio_names_are_equal(self) -> None:
        """Should be equal if portfolio names have same value."""
        name1 = PortfolioName("Same Portfolio Name")
        name2 = PortfolioName("Same Portfolio Name")

        assert name1 == name2

    def test_equal_after_whitespace_normalization(self) -> None:
        """Should be equal after whitespace normalization."""
        name1 = PortfolioName("Portfolio Name")
        name2 = PortfolioName("  Portfolio Name  ")

        assert name1 == name2

    def test_different_portfolio_names_are_not_equal(self) -> None:
        """Should not be equal if portfolio names have different values."""
        name1 = PortfolioName("Growth Portfolio")
        name2 = PortfolioName("Income Portfolio")

        assert name1 != name2

    def test_case_sensitive_comparison(self) -> None:
        """Should be case sensitive in comparison."""
        name1 = PortfolioName("Portfolio Name")
        name2 = PortfolioName("portfolio name")

        assert name1 != name2

    def test_portfolio_name_not_equal_to_other_types(self) -> None:
        """Should not be equal to non-PortfolioName objects."""
        name = PortfolioName("Portfolio Name")

        assert name != "Portfolio Name"
        assert name != 1
        assert name != None
        assert name != []

    def test_portfolio_name_hashable(self) -> None:
        """Should be hashable for use in collections."""
        name1 = PortfolioName("Same Name")
        name2 = PortfolioName("Same Name")
        name3 = PortfolioName("Different Name")

        # Should be able to use in set
        name_set = {name1, name2, name3}
        assert len(name_set) == 2  # name1 and name2 should be same hash

        # Should be able to use as dict key
        name_dict = {name1: "first", name3: "second"}
        assert len(name_dict) == 2
        assert name_dict[name2] == "first"  # Should find name1's value


class TestPortfolioNameImmutability:
    """Test PortfolioName immutability."""

    def test_value_property_is_readonly(self) -> None:
        """Should not be able to modify value after creation."""
        name = PortfolioName("Original Name")

        with pytest.raises(AttributeError):
            name.value = "Modified Name"  # type: ignore[misc]

    def test_cannot_set_attributes_after_creation(self) -> None:
        """Should not be able to set new attributes after creation."""
        name = PortfolioName("Portfolio Name")

        with pytest.raises(AttributeError, match="PortfolioName is immutable"):
            name.new_attribute = "value"  # type: ignore[attr-defined]

    def test_cannot_modify_private_value_attribute(self) -> None:
        """Should not be able to modify private _value attribute."""
        name = PortfolioName("Portfolio Name")

        with pytest.raises(AttributeError, match="PortfolioName is immutable"):
            name._value = "Modified Name"  # type: ignore[misc]


class TestPortfolioNameStringRepresentation:
    """Test PortfolioName string representations."""

    def test_str_returns_name_value(self) -> None:
        """Should return portfolio name value as string."""
        name = PortfolioName("Growth & Income Portfolio")

        assert str(name) == "Growth & Income Portfolio"

    def test_repr_returns_developer_representation(self) -> None:
        """Should return developer-friendly representation."""
        name = PortfolioName("My Portfolio")

        assert repr(name) == "PortfolioName('My Portfolio')"

    def test_repr_handles_quotes_in_name(self) -> None:
        """Should handle quotes in portfolio name in repr."""
        name_with_quotes = PortfolioName("My 'Special' Portfolio")

        # Should escape quotes properly
        assert "My 'Special' Portfolio" in repr(name_with_quotes)


class TestPortfolioNameConstants:
    """Test PortfolioName constants."""

    def test_max_length_constant(self) -> None:
        """Should have correct maximum length constant."""
        assert PortfolioName.MAX_LENGTH == 100

    def test_max_length_constant_is_enforced(self) -> None:
        """Should enforce the maximum length constant."""
        # This should work
        valid_name = PortfolioName("A" * PortfolioName.MAX_LENGTH)
        assert len(valid_name.value) == PortfolioName.MAX_LENGTH

        # This should fail
        with pytest.raises(ValueError):
            PortfolioName("A" * (PortfolioName.MAX_LENGTH + 1))


class TestPortfolioNameBusinessLogic:
    """Test PortfolioName business logic and common use cases."""

    def test_typical_portfolio_names(self) -> None:
        """Should handle typical portfolio naming patterns."""
        typical_names = [
            "Retirement Portfolio",
            "Emergency Fund",
            "Growth Stocks 2023",
            "Conservative Mix",
            "Tech Heavy",
            "Dividend Income",
            "401k Rollover",
            "Roth IRA",
            "Taxable Account",
        ]

        for name_str in typical_names:
            name = PortfolioName(name_str)
            assert name.value == name_str

    def test_portfolio_names_with_dates(self) -> None:
        """Should handle portfolio names with dates."""
        date_names = [
            "Portfolio 2023",
            "Q1 2023 Growth",
            "Dec 2022 Rebalance",
            "2023-Q4 Conservative",
        ]

        for name_str in date_names:
            name = PortfolioName(name_str)
            assert name.value == name_str

    def test_portfolio_names_with_percentages(self) -> None:
        """Should handle portfolio names with percentage symbols."""
        percentage_names = [
            "70% Stocks 30% Bonds",
            "100% Equity Portfolio",
            "50/50 Split",
        ]

        for name_str in percentage_names:
            name = PortfolioName(name_str)
            assert name.value == name_str

    def test_portfolio_names_with_currency_symbols(self) -> None:
        """Should handle portfolio names with currency symbols."""
        currency_names = [
            "$100K Goal Portfolio",
            "€ European Stocks",
            "¥ Japanese Market",
        ]

        for name_str in currency_names:
            name = PortfolioName(name_str)
            assert name.value == name_str


class TestPortfolioNameEdgeCases:
    """Test PortfolioName edge cases and boundary conditions."""

    def test_create_with_unicode_characters(self) -> None:
        """Should handle unicode characters correctly."""
        unicode_names = [
            "Açõês Brasileiras",  # Portuguese
            "中国股票",  # Chinese
            "Портфель",  # Russian
            "Portfolio émergent",  # French
            "Ñoño's Portfolio",  # Spanish with special chars
        ]

        for name_str in unicode_names:
            name = PortfolioName(name_str)
            assert name.value == name_str

    def test_create_with_emoji_characters(self) -> None:
        """Should handle emoji characters correctly."""
        emoji_names = [
            "🚀 Growth Portfolio",
            "💰 Income Focus 💎",
            "📈 Trending Stocks",
        ]

        for name_str in emoji_names:
            name = PortfolioName(name_str)
            assert name.value == name_str

    def test_create_with_mathematical_symbols(self) -> None:
        """Should handle mathematical symbols correctly."""
        math_names = ["α Beta Strategy", "Σ Diversified", "π × Returns"]

        for name_str in math_names:
            name = PortfolioName(name_str)
            assert name.value == name_str

    def test_create_single_character_name(self) -> None:
        """Should handle single character portfolio names."""
        single_char_names = ["A", "1", "€", "π"]

        for name_str in single_char_names:
            name = PortfolioName(name_str)
            assert name.value == name_str

    def test_whitespace_preservation_within_name(self) -> None:
        """Should preserve internal whitespace while stripping external."""
        names_with_internal_whitespace = [
            "  Portfolio   with   spaces  ",
            "\tTab\tSeparated\tWords\t",
            "  Multi\n\nLine\n\nName  ",
        ]

        expected_results = [
            "Portfolio   with   spaces",
            "Tab\tSeparated\tWords",
            "Multi\n\nLine\n\nName",
        ]

        for name_str, expected in zip(names_with_internal_whitespace, expected_results):
            name = PortfolioName(name_str)
            assert name.value == expected

    def test_create_with_very_long_unicode_name(self) -> None:
        """Should handle length validation with unicode characters correctly."""
        # Unicode characters might have different byte lengths
        unicode_char = "€"  # Euro symbol
        max_unicode_name = unicode_char * PortfolioName.MAX_LENGTH
        too_long_unicode_name = unicode_char * (PortfolioName.MAX_LENGTH + 1)

        # Should work at exactly max length
        name = PortfolioName(max_unicode_name)
        assert len(name.value) == PortfolioName.MAX_LENGTH

        # Should fail when exceeding max length
        with pytest.raises(
            ValueError, match="Portfolio name cannot exceed 100 characters"
        ):
            PortfolioName(too_long_unicode_name)
