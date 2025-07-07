"""
Unit tests for dependency lifetimes.

Tests the Lifetime enum used for dependency lifecycle management.
"""

from enum import Enum

import pytest

from dependency_injection.lifetimes import Lifetime


class TestLifetimeEnum:
    """Test the Lifetime enumeration."""

    def test_lifetime_is_enum(self) -> None:
        """Should be a proper Python enum."""
        assert issubclass(Lifetime, Enum)

    def test_lifetime_values(self) -> None:
        """Should have expected lifetime values."""
        assert Lifetime.SINGLETON.value == "singleton"
        assert Lifetime.TRANSIENT.value == "transient"
        assert Lifetime.SCOPED.value == "scoped"

    def test_lifetime_members(self) -> None:
        """Should have exactly the expected members."""
        expected_members = {"SINGLETON", "TRANSIENT", "SCOPED"}
        actual_members = {member.name for member in Lifetime}
        assert actual_members == expected_members

    def test_lifetime_comparison(self) -> None:
        """Should support enum comparison."""
        assert Lifetime.SINGLETON == Lifetime.SINGLETON
        assert Lifetime.SINGLETON != Lifetime.TRANSIENT
        assert Lifetime.TRANSIENT != Lifetime.SCOPED

    def test_lifetime_string_representation(self) -> None:
        """Should have readable string representation."""
        assert str(Lifetime.SINGLETON) == "Lifetime.SINGLETON"
        assert str(Lifetime.TRANSIENT) == "Lifetime.TRANSIENT"
        assert str(Lifetime.SCOPED) == "Lifetime.SCOPED"

    def test_lifetime_from_value(self) -> None:
        """Should be able to get lifetime from value."""
        assert Lifetime("singleton") == Lifetime.SINGLETON
        assert Lifetime("transient") == Lifetime.TRANSIENT
        assert Lifetime("scoped") == Lifetime.SCOPED

    def test_lifetime_invalid_value(self) -> None:
        """Should raise error for invalid lifetime value."""
        with pytest.raises(ValueError, match="invalid"):
            _ = Lifetime("invalid")

    def test_lifetime_iteration(self) -> None:
        """Should be iterable."""
        lifetimes = list(Lifetime)
        assert len(lifetimes) == 3
        assert Lifetime.SINGLETON in lifetimes
        assert Lifetime.TRANSIENT in lifetimes
        assert Lifetime.SCOPED in lifetimes

    def test_lifetime_hashable(self) -> None:
        """Should be hashable for use in sets/dicts."""
        lifetime_set = {Lifetime.SINGLETON, Lifetime.TRANSIENT, Lifetime.SINGLETON}
        assert len(lifetime_set) == 2

        lifetime_dict = {
            Lifetime.SINGLETON: "single instance",
            Lifetime.TRANSIENT: "new instance",
        }
        assert lifetime_dict[Lifetime.SINGLETON] == "single instance"
