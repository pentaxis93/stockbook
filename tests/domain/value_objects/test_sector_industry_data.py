"""
Tests for sector_industry_data module.
"""

from src.domain.value_objects.sector_industry_data import (
    get_sector_for_industry,
)


class TestSectorIndustryData:
    """Test suite for sector_industry_data module."""

    def test_get_sector_for_industry_returns_none_for_unknown_industry(self) -> None:
        """Test that get_sector_for_industry returns None for unknown industry."""
        # Test an industry that doesn't exist in any sector
        result = get_sector_for_industry("UnknownIndustryGroup")
        assert result is None
