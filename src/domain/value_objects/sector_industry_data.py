"""Shared sector-industry mapping data for the StockBook domain.

This module contains the fixed domain knowledge about which industry groups
belong to which sectors. This data is used by both Sector and IndustryGroup
value objects to ensure consistency and enable self-validation.
"""

# Configuration of sector -> industry groups mapping
# This represents fixed domain knowledge
SECTOR_INDUSTRY_MAPPING: dict[str, list[str]] = {
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


def get_sector_for_industry(industry_group: str) -> str | None:
    """Get the sector that contains the given industry group.

    Args:
        industry_group: The industry group to look up

    Returns:
        The sector name if found, None otherwise
    """
    for sector, industries in SECTOR_INDUSTRY_MAPPING.items():
        if industry_group in industries:
            return sector
    return None


def get_all_valid_sectors() -> list[str]:
    """Get a list of all valid sectors.

    Returns:
        List of valid sector names
    """
    return list(SECTOR_INDUSTRY_MAPPING.keys())


def get_all_valid_industry_groups() -> list[str]:
    """Get a list of all valid industry groups across all sectors.

    Returns:
        List of valid industry group names
    """
    all_industries: list[str] = []
    for industries in SECTOR_INDUSTRY_MAPPING.values():
        all_industries.extend(industries)
    return sorted(all_industries)
