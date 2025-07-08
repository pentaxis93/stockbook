"""
Test suite for Sector value object.
"""

import pytest

from src.domain.value_objects.sector import Sector


class TestSectorValueObject:
    """Test cases for Sector value object."""

    def test_sector_creation_with_valid_value(self) -> None:
        """Test creating sector with valid string."""
        sector = Sector("Technology")
        assert sector.value == "Technology"
        assert str(sector) == "Technology"

    def test_sector_creation_strips_whitespace(self) -> None:
        """Test sector creation strips leading/trailing whitespace."""
        sector = Sector("  Technology  ")
        assert sector.value == "Technology"

    def test_sector_creation_with_empty_string_raises_error(self) -> None:
        """Test sector creation with empty string raises ValueError."""
        with pytest.raises(ValueError, match="Sector cannot be empty"):
            _ = Sector("")

    def test_sector_creation_with_whitespace_only_raises_error(self) -> None:
        """Test sector creation with whitespace-only string raises ValueError."""
        with pytest.raises(ValueError, match="Sector cannot be empty"):
            _ = Sector("   ")

    def test_sector_creation_with_too_long_value_raises_error(self) -> None:
        """Test sector creation with string exceeding max length raises ValueError."""
        long_sector = "a" * 101
        with pytest.raises(ValueError, match="Sector cannot exceed 100 characters"):
            _ = Sector(long_sector)

    def test_sector_creation_with_arbitrary_value_raises_error(self) -> None:
        """Test sector creation with arbitrary values raises error."""
        # Only valid sectors from our mapping are allowed
        invalid_sector = "InvalidSectorName"
        with pytest.raises(ValueError, match="Invalid sector"):
            _ = Sector(invalid_sector)

    def test_sector_equality(self) -> None:
        """Test sector equality comparison."""
        sector1 = Sector("Technology")
        sector2 = Sector("Technology")
        sector3 = Sector("Healthcare")

        assert sector1 == sector2
        assert sector1 != sector3
        assert sector2 != sector3

    def test_sector_equality_with_different_types(self) -> None:
        """Test sector equality with non-Sector objects."""
        sector = Sector("Technology")
        assert sector != "Technology"
        assert sector != 123
        assert sector is not None
        assert sector != {"value": "Technology"}

    def test_sector_base_class_coverage(self) -> None:
        """Test base class coverage for Sector missing lines."""
        # Test that normal initialization works (covers base class __setattr__)
        sector = Sector("Technology")
        assert sector.value == "Technology"

    def test_sector_setattr_during_initialization(self) -> None:
        """Test that __setattr__ allows setting attributes during initialization."""
        # Create a partially initialized object
        sector = object.__new__(Sector)

        # This exercises the super().__setattr__ branch (line 71)
        sector.test_attr = "test_value"

        # Now properly initialize the object
        Sector.__init__(sector, "Technology")
        assert sector.value == "Technology"

    def test_sector_hash(self) -> None:
        """Test sector can be used as dictionary key."""
        sector1 = Sector("Technology")
        sector2 = Sector("Technology")
        sector3 = Sector("Healthcare")

        # Same value should have same hash
        assert hash(sector1) == hash(sector2)

        # Can be used in set
        sector_set = {sector1, sector2, sector3}
        assert len(sector_set) == 2  # sector1 and sector2 are duplicates

    def test_sector_repr(self) -> None:
        """Test sector developer representation."""
        sector = Sector("Technology")
        assert repr(sector) == "Sector('Technology')"

    def test_sector_immutability(self) -> None:
        """Test sector cannot be modified after creation."""
        sector = Sector("Technology")

        with pytest.raises(AttributeError, match="Sector is immutable"):
            sector.value = "Healthcare"  # type: ignore[misc] - Testing immutability

        # Note: Internal state protection verified through public interface above

    def test_sector_knows_valid_industry_groups(self) -> None:
        """Test that sectors can validate their industry groups."""
        tech_sector = Sector("Technology")
        assert tech_sector.is_valid_industry_group("Software")
        assert tech_sector.is_valid_industry_group("Hardware")
        assert not tech_sector.is_valid_industry_group("Pharmaceuticals")

        healthcare_sector = Sector("Healthcare")
        assert healthcare_sector.is_valid_industry_group("Pharmaceuticals")
        assert healthcare_sector.is_valid_industry_group("Biotechnology")
        assert not healthcare_sector.is_valid_industry_group("Software")

    def test_sector_can_list_industry_groups(self) -> None:
        """Test that sectors can list their valid industry groups."""
        tech_sector = Sector("Technology")
        industries = tech_sector.get_industry_groups()
        assert "Software" in industries
        assert "Hardware" in industries
        assert "Semiconductors" in industries
        assert "Pharmaceuticals" not in industries

        healthcare_sector = Sector("Healthcare")
        healthcare_industries = healthcare_sector.get_industry_groups()
        assert "Pharmaceuticals" in healthcare_industries
        assert "Biotechnology" in healthcare_industries
        assert "Software" not in healthcare_industries

    def test_invalid_sector_raises_error(self) -> None:
        """Test that invalid sectors raise an error."""
        with pytest.raises(ValueError, match="Invalid sector 'InvalidSector'"):
            _ = Sector("InvalidSector")

    def test_sector_with_valid_mapping(self) -> None:
        """Test various valid sectors from the mapping."""
        valid_sectors = [
            "Technology",
            "Healthcare",
            "Financial Services",
            "Consumer Goods",
            "Energy",
            "Industrial",
        ]

        for sector_name in valid_sectors:
            sector = Sector(sector_name)
            assert sector.value == sector_name
            # Should have industry groups
            assert len(sector.get_industry_groups()) > 0
