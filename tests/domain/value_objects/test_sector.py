"""
Test suite for Sector value object.
"""

import pytest

from domain.value_objects.sector import Sector


class TestSectorValueObject:
    """Test cases for Sector value object."""

    def test_sector_creation_with_valid_value(self):
        """Test creating sector with valid string."""
        sector = Sector("Technology")
        assert sector.value == "Technology"
        assert str(sector) == "Technology"

    def test_sector_creation_strips_whitespace(self):
        """Test sector creation strips leading/trailing whitespace."""
        sector = Sector("  Technology  ")
        assert sector.value == "Technology"

    def test_sector_creation_with_empty_string_raises_error(self):
        """Test sector creation with empty string raises ValueError."""
        with pytest.raises(ValueError, match="Sector cannot be empty"):
            Sector("")

    def test_sector_creation_with_whitespace_only_raises_error(self):
        """Test sector creation with whitespace-only string raises ValueError."""
        with pytest.raises(ValueError, match="Sector cannot be empty"):
            Sector("   ")

    def test_sector_creation_with_too_long_value_raises_error(self):
        """Test sector creation with string exceeding max length raises ValueError."""
        long_sector = "a" * 101
        with pytest.raises(ValueError, match="Sector cannot exceed 100 characters"):
            Sector(long_sector)

    def test_sector_creation_with_max_length_value_succeeds(self):
        """Test sector creation with exactly max length succeeds."""
        max_length_sector = "a" * 100
        sector = Sector(max_length_sector)
        assert sector.value == max_length_sector

    def test_sector_equality(self):
        """Test sector equality comparison."""
        sector1 = Sector("Technology")
        sector2 = Sector("Technology")
        sector3 = Sector("Healthcare")

        assert sector1 == sector2
        assert sector1 != sector3
        assert sector2 != sector3

    def test_sector_equality_with_different_types(self):
        """Test sector equality with non-Sector objects."""
        sector = Sector("Technology")
        assert sector != "Technology"
        assert sector != 123
        assert sector != None

    def test_sector_hash(self):
        """Test sector can be used as dictionary key."""
        sector1 = Sector("Technology")
        sector2 = Sector("Technology")
        sector3 = Sector("Healthcare")

        # Same value should have same hash
        assert hash(sector1) == hash(sector2)

        # Can be used in set
        sector_set = {sector1, sector2, sector3}
        assert len(sector_set) == 2  # sector1 and sector2 are duplicates

    def test_sector_repr(self):
        """Test sector developer representation."""
        sector = Sector("Technology")
        assert repr(sector) == "Sector('Technology')"

    def test_sector_immutability(self):
        """Test sector cannot be modified after creation."""
        sector = Sector("Technology")

        with pytest.raises(AttributeError, match="Sector is immutable"):
            sector.value = "Healthcare"

        with pytest.raises(AttributeError, match="Sector is immutable"):
            sector._value = "Healthcare"
