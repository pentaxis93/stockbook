"""
Test suite for SectorIndustryService domain service.
"""

import pytest

from src.domain.services.sector_industry_service import SectorIndustryService


class TestSectorIndustryService:
    """Test cases for SectorIndustryService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = SectorIndustryService()

    def test_get_available_sectors(self):
        """Test getting list of available sectors."""
        sectors = self.service.get_available_sectors()

        assert isinstance(sectors, list)
        assert len(sectors) > 0
        assert "Technology" in sectors
        assert "Healthcare" in sectors
        assert "Financial Services" in sectors

    def test_get_industry_groups_for_valid_sector(self):
        """Test getting industry groups for valid sector."""
        tech_industries = self.service.get_industry_groups_for_sector("Technology")

        assert isinstance(tech_industries, list)
        assert len(tech_industries) > 0
        assert "Software" in tech_industries
        assert "Hardware" in tech_industries

    def test_get_industry_groups_for_invalid_sector_raises_error(self):
        """Test getting industry groups for invalid sector raises ValueError."""
        with pytest.raises(ValueError, match="Invalid sector 'InvalidSector'"):
            self.service.get_industry_groups_for_sector("InvalidSector")

    def test_validate_sector_industry_combination_valid(self):
        """Test validating valid sector-industry combination."""
        assert self.service.validate_sector_industry_combination(
            "Technology", "Software"
        )
        assert self.service.validate_sector_industry_combination(
            "Healthcare", "Pharmaceuticals"
        )

    def test_validate_sector_industry_combination_invalid_industry(self):
        """Test validating invalid industry for valid sector."""
        assert not self.service.validate_sector_industry_combination(
            "Technology", "Pharmaceuticals"
        )
        assert not self.service.validate_sector_industry_combination(
            "Healthcare", "Software"
        )

    def test_validate_sector_industry_combination_invalid_sector(self):
        """Test validating combination with invalid sector."""
        assert not self.service.validate_sector_industry_combination(
            "InvalidSector", "Software"
        )

    def test_validate_sector_industry_combination_strict_valid(self):
        """Test strict validation with valid combination."""
        # Should not raise exception
        self.service.validate_sector_industry_combination_strict(
            "Technology", "Software"
        )
        self.service.validate_sector_industry_combination_strict(
            "Healthcare", "Pharmaceuticals"
        )

    def test_validate_sector_industry_combination_strict_invalid_industry(self):
        """Test strict validation with invalid industry raises ValueError."""
        with pytest.raises(
            ValueError,
            match="Industry group 'Pharmaceuticals' is not valid for sector 'Technology'",
        ):
            self.service.validate_sector_industry_combination_strict(
                "Technology", "Pharmaceuticals"
            )

    def test_validate_sector_industry_combination_strict_invalid_sector(self):
        """Test strict validation with invalid sector raises ValueError."""
        with pytest.raises(ValueError, match="Invalid sector 'InvalidSector'"):
            self.service.validate_sector_industry_combination_strict(
                "InvalidSector", "Software"
            )

    def test_get_sector_for_industry_group_valid(self):
        """Test getting sector for valid industry group."""
        assert self.service.get_sector_for_industry_group("Software") == "Technology"
        assert (
            self.service.get_sector_for_industry_group("Pharmaceuticals")
            == "Healthcare"
        )
        assert (
            self.service.get_sector_for_industry_group("Banks") == "Financial Services"
        )

    def test_get_sector_for_industry_group_invalid(self):
        """Test getting sector for invalid industry group raises ValueError."""
        with pytest.raises(
            ValueError, match="Industry group 'InvalidIndustry' not found in any sector"
        ):
            self.service.get_sector_for_industry_group("InvalidIndustry")

    def test_sector_industry_mapping_completeness(self):
        """Test that sector-industry mapping is properly configured."""
        mapping = self.service.SECTOR_INDUSTRY_MAPPING

        # Check that we have sectors
        assert len(mapping) > 0

        # Check that each sector has industry groups
        for sector, industries in mapping.items():
            assert isinstance(sector, str)
            assert len(sector) > 0
            assert isinstance(industries, list)
            assert len(industries) > 0

            # Check that all industry groups are strings
            for industry in industries:
                assert isinstance(industry, str)
                assert len(industry) > 0

    def test_no_duplicate_industry_groups_across_sectors(self):
        """Test that no industry group appears in multiple sectors."""
        all_industries = []
        mapping = self.service.SECTOR_INDUSTRY_MAPPING

        for industries in mapping.values():
            all_industries.extend(industries)

        # Check for duplicates
        unique_industries = set(all_industries)
        assert len(all_industries) == len(
            unique_industries
        ), "Found duplicate industry groups across sectors"
