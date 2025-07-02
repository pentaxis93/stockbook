"""
Stock domain entity with rich business behavior.

Represents a stock/security in the trading system with business logic
and validation rules encapsulated within the entity.
"""

from typing import Any, Dict, Optional

from src.domain.entities.base import BaseEntity
from src.domain.value_objects import (
    CompanyName,
    Grade,
    IndustryGroup,
    Money,
    Notes,
    Quantity,
    Sector,
    StockSymbol,
)


class StockEntity(BaseEntity):
    """
    Rich domain entity representing a stock/security.

    Encapsulates business logic for stock operations including
    validation, calculations, and state management.
    """

    # Type annotations for instance variables
    _symbol: StockSymbol
    _company_name: CompanyName
    _sector: Optional[Sector]
    _industry_group: Optional[IndustryGroup]
    _grade: Optional[Grade]
    _notes: Notes

    def __init__(
        self,
        symbol: StockSymbol,
        company_name: CompanyName,
        sector: Optional[Sector] = None,
        industry_group: Optional[IndustryGroup] = None,
        grade: Optional[Grade] = None,
        notes: Optional[Notes] = None,
        id: Optional[str] = None,
    ):
        """
        Initialize Stock entity with value objects.

        Args:
            symbol: Stock symbol (value object)
            company_name: Company name value object
            sector: Sector classification value object
            industry_group: Industry classification value object (must belong to sector if provided)
            grade: Stock grade value object (A/B/C/D/F or None)
            notes: Additional notes value object
            id: Entity ID (string)

        Raises:
            ValueError: If any validation fails
        """
        # Initialize sector industry service for validation (import here to avoid circular imports)
        from src.domain.services.sector_industry_service import SectorIndustryService

        self._sector_industry_service = SectorIndustryService()

        # Store value objects directly (they're already validated)
        super().__init__(id=id)
        self._symbol = symbol
        self._company_name = company_name
        self._sector = sector
        self._industry_group = industry_group
        self._grade = grade
        self._notes = notes if notes is not None else Notes("")

        # Validate domain business rules (sector-industry relationship)
        sector_str = sector.value if sector else None
        industry_group_str = industry_group.value if industry_group else None
        self._validate_sector_industry_combination(sector_str, industry_group_str)

    @property
    def symbol(self) -> StockSymbol:
        """Get the stock symbol."""
        return self._symbol

    @property
    def company_name(self) -> CompanyName:
        """Get the company name value object."""
        return self._company_name

    @property
    def sector(self) -> Optional[Sector]:
        """Get the sector value object."""
        return self._sector

    @property
    def industry_group(self) -> Optional[IndustryGroup]:
        """Get the industry group value object."""
        return self._industry_group

    @property
    def grade(self) -> Optional[Grade]:
        """Get the grade value object."""
        return self._grade

    @property
    def notes(self) -> Notes:
        """Get the notes value object."""
        return self._notes

    def __eq__(self, other: Any) -> bool:
        """
        Check equality based on business key (symbol).

        Two stocks are considered equal if they have the same symbol,
        regardless of other attributes or database ID.
        """
        if not isinstance(other, StockEntity):
            return False
        return self.symbol == other.symbol

    def __hash__(self) -> int:
        """Hash based on business key (symbol)."""
        return hash(self.symbol)

    def __str__(self) -> str:
        """String representation for display."""
        return f"{self.symbol} - {self.company_name.value}"

    def __repr__(self) -> str:
        """Developer representation."""
        return (
            f"StockEntity(symbol={self.symbol!r}, company_name={self.company_name!r}, "
            f"grade={self.grade!r})"
        )

    def calculate_position_value(self, quantity: Quantity, price: Money) -> Money:
        """
        Calculate total value of a position in this stock.

        Args:
            quantity: Number of shares
            price: Price per share

        Returns:
            Total position value
        """
        return price * quantity.value

    def has_notes(self) -> bool:
        """
        Check if stock has notes.

        Returns:
            True if notes are present and not empty
        """
        return self._notes.has_content()

    def update_fields(self, **kwargs: Any) -> None:
        """
        Update multiple fields at once.

        Args:
            **kwargs: Field names and values to update.
                     Supported fields: name, sector, industry_group, grade, notes

        Raises:
            ValueError: If any field is invalid
        """
        # Create temporary value objects for validation first (atomic operation)
        temp_values = self._create_temp_value_objects(kwargs)

        # Handle sector-industry domain logic and validation
        self._validate_and_adjust_sector_industry(kwargs, temp_values)

        # All validation passed, now update the actual fields
        self._apply_field_updates(temp_values)

    def _create_temp_value_objects(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Create temporary value objects for validation."""
        temp_values: Dict[str, Any] = {}

        # Create value objects in separate methods to reduce complexity
        self._create_company_name_vo(kwargs, temp_values)
        self._create_sector_vo(kwargs, temp_values)
        self._create_industry_group_vo(kwargs, temp_values)
        self._create_grade_vo(kwargs, temp_values)
        self._create_notes_vo(kwargs, temp_values)

        return temp_values

    def _create_company_name_vo(
        self, kwargs: Dict[str, Any], temp_values: Dict[str, Any]
    ) -> None:
        """Create company name value object if present."""
        if "name" in kwargs:
            temp_values["company_name"] = CompanyName(kwargs["name"])

    def _create_sector_vo(
        self, kwargs: Dict[str, Any], temp_values: Dict[str, Any]
    ) -> None:
        """Create sector value object if present."""
        if "sector" in kwargs:
            sector = kwargs["sector"]
            temp_values["sector"] = Sector(sector) if sector is not None else None

    def _create_industry_group_vo(
        self, kwargs: Dict[str, Any], temp_values: Dict[str, Any]
    ) -> None:
        """Create industry group value object if present."""
        if "industry_group" in kwargs:
            industry_group = kwargs["industry_group"]
            temp_values["industry_group"] = (
                IndustryGroup(industry_group) if industry_group else None
            )

    def _create_grade_vo(
        self, kwargs: Dict[str, Any], temp_values: Dict[str, Any]
    ) -> None:
        """Create grade value object if present."""
        if "grade" in kwargs:
            grade_value = kwargs["grade"]
            temp_values["grade"] = (
                Grade(grade_value) if grade_value is not None else None
            )

    def _create_notes_vo(
        self, kwargs: Dict[str, Any], temp_values: Dict[str, Any]
    ) -> None:
        """Create notes value object if present."""
        if "notes" in kwargs:
            temp_values["notes"] = Notes(kwargs["notes"])

    def _validate_and_adjust_sector_industry(
        self, kwargs: Dict[str, Any], temp_values: Dict[str, Any]
    ) -> None:
        """Validate sector-industry combination and adjust if needed."""
        new_sector = kwargs.get("sector", self.sector.value if self.sector else None)
        new_industry_group = kwargs.get(
            "industry_group", self.industry_group.value if self.industry_group else None
        )

        # Special logic: if changing sector, check if current industry_group is compatible
        if (
            "sector" in kwargs
            and "industry_group" not in kwargs
            and self._should_clear_industry_group_for_new_sector(new_sector)
        ):
            new_industry_group = None
            temp_values["industry_group"] = None

        # Validate the final sector-industry combination
        self._validate_sector_industry_combination(new_sector, new_industry_group)

    def _should_clear_industry_group_for_new_sector(
        self, new_sector: Optional[str]
    ) -> bool:
        """Check if current industry group should be cleared for new sector."""
        return (
            self.industry_group is not None
            and new_sector is not None
            and not self._sector_industry_service.validate_sector_industry_combination(
                new_sector, self.industry_group.value
            )
        )

    def _apply_field_updates(self, temp_values: Dict[str, Any]) -> None:
        """Apply validated field updates to the entity."""
        if "company_name" in temp_values:
            self._company_name = temp_values["company_name"]
        if "sector" in temp_values:
            self._sector = temp_values["sector"]
        if "industry_group" in temp_values:
            self._industry_group = temp_values["industry_group"]
        if "grade" in temp_values:
            self._grade = temp_values["grade"]
        if "notes" in temp_values:
            self._notes = temp_values["notes"]

    def _validate_sector_industry_combination(
        self, sector: Optional[str], industry_group: Optional[str]
    ) -> None:
        """
        Validate that sector and industry_group combination is valid.

        Args:
            sector: Sector name
            industry_group: Industry group name

        Raises:
            ValueError: If combination is invalid
        """
        # If no industry group, sector can be anything (or None)
        if industry_group is None:
            return

        # If industry group is provided, sector must also be provided
        if sector is None:
            raise ValueError("Sector must be provided when industry_group is specified")

        # Validate the combination using domain service
        self._sector_industry_service.validate_sector_industry_combination_strict(
            sector, industry_group
        )
