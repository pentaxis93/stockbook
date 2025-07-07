"""Domain service for managing sector-industry group relationships.

Provides validation and lookup capabilities for the sector-industry group hierarchy.
"""

from typing import ClassVar


class SectorIndustryService:
    """Domain service for sector-industry group relationship management.

    Maintains the configuration of which industry groups belong to which sectors
    and provides validation methods.
    """

    # Configuration of sector -> industry groups mapping
    # This would typically be loaded from configuration file or database
    SECTOR_INDUSTRY_MAPPING: ClassVar[dict[str, list[str]]] = {
        "Technology": [
            "Software",
            "Hardware",
            "Semiconductors",
            "Internet Services",
            "Telecommunications",
        ],
        "Healthcare": [
            "Pharmaceuticals",
            "Biotechnology",
            "Medical Devices",
            "Healthcare Services",
            "Medical Diagnostics",
        ],
        "Financial Services": [
            "Banks",
            "Insurance",
            "Investment Services",
            "Real Estate",
            "Financial Technology",
        ],
        "Consumer Goods": [
            "Consumer Electronics",
            "Apparel & Textiles",
            "Food & Beverages",
            "Household Products",
            "Automotive",
        ],
        "Energy": [
            "Oil & Gas",
            "Renewable Energy",
            "Utilities",
            "Energy Equipment",
            "Coal",
        ],
        "Industrial": [
            "Manufacturing",
            "Transportation",
            "Construction",
            "Aerospace & Defense",
            "Industrial Equipment",
        ],
    }

    def get_available_sectors(self) -> list[str]:
        """Get list of all available sectors.

        Returns:
            List of sector names
        """
        return list(self.SECTOR_INDUSTRY_MAPPING.keys())

    def get_industry_groups_for_sector(self, sector: str) -> list[str]:
        """Get list of industry groups available for a given sector.

        Args:
            sector: Sector name

        Returns:
            List of industry group names for the sector

        Raises:
            ValueError: If sector is not valid
        """
        if sector not in self.SECTOR_INDUSTRY_MAPPING:
            available_sectors = ", ".join(self.get_available_sectors())
            msg = f"Invalid sector {sector!r}. Available sectors: {available_sectors}"
            raise ValueError(msg)

        return self.SECTOR_INDUSTRY_MAPPING[sector]

    def validate_sector_industry_combination(
        self,
        sector: str,
        industry_group: str,
    ) -> bool:
        """Validate that an industry group belongs to the specified sector.

        Args:
            sector: Sector name
            industry_group: Industry group name

        Returns:
            True if valid combination, False otherwise
        """
        try:
            valid_industries = self.get_industry_groups_for_sector(sector)
        except ValueError:
            return False
        else:
            return industry_group in valid_industries

    def validate_sector_industry_combination_strict(
        self,
        sector: str,
        industry_group: str,
    ) -> None:
        """Validate sector-industry combination with exceptions.

        Args:
            sector: Sector name
            industry_group: Industry group name

        Raises:
            ValueError: If combination is invalid
        """
        if not self.validate_sector_industry_combination(sector, industry_group):
            valid_industries = self.get_industry_groups_for_sector(sector)
            valid_industries_str = ", ".join(valid_industries)
            raise ValueError(
                f"Industry group {industry_group!r} is not valid for sector "
                + f"{sector!r}. Valid industry groups for this sector: "
                + f"{valid_industries_str}",
            )

    def get_sector_for_industry_group(self, industry_group: str) -> str:
        """Find which sector contains the given industry group.

        Args:
            industry_group: Industry group name

        Returns:
            Sector name that contains the industry group

        Raises:
            ValueError: If industry group is not found in any sector
        """
        for sector, industries in self.SECTOR_INDUSTRY_MAPPING.items():
            if industry_group in industries:
                return sector

        # Collect all available industry groups for error message
        all_industries: list[str] = []
        for industries in self.SECTOR_INDUSTRY_MAPPING.values():
            all_industries.extend(industries)

        available_industries = ", ".join(sorted(all_industries))
        raise ValueError(
            f"Industry group {industry_group!r} not found in any sector. "
            + f"Available industry groups: {available_industries}",
        )
