"""
Stock domain entity with rich business behavior.

Represents a stock/security in the trading system with business logic
and validation rules encapsulated within the entity.
"""

from typing import Optional

from shared_kernel.value_objects import Money, Quantity
from src.domain.value_objects import CompanyName, Grade, IndustryGroup, Notes
from src.domain.value_objects.sector import Sector
from src.domain.value_objects.stock_symbol import StockSymbol


class StockEntity:
    """
    Rich domain entity representing a stock/security.

    Encapsulates business logic for stock operations including
    validation, calculations, and state management.
    """

    def __init__(
        self,
        symbol: StockSymbol,
        company_name: CompanyName,
        sector: Optional[Sector] = None,
        industry_group: Optional[IndustryGroup] = None,
        grade: Optional[Grade] = None,
        notes: Optional[Notes] = None,
        stock_id: Optional[int] = None,
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
            stock_id: Database ID (for persistence)

        Raises:
            ValueError: If any validation fails
        """
        # Initialize sector industry service for validation (import here to avoid circular imports)
        from src.domain.services.sector_industry_service import SectorIndustryService

        self._sector_industry_service = SectorIndustryService()

        # Store value objects directly (they're already validated)
        self._symbol = symbol
        self._company_name = company_name
        self._sector_vo = sector
        self._industry_group_vo = industry_group
        self._grade_vo = grade
        self._notes_vo = notes if notes is not None else Notes("")
        self._id = stock_id

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
        return self._sector_vo

    @property
    def industry_group(self) -> Optional[IndustryGroup]:
        """Get the industry group value object."""
        return self._industry_group_vo

    @property
    def grade(self) -> Optional[Grade]:
        """Get the grade value object."""
        return self._grade_vo

    @property
    def notes(self) -> Notes:
        """Get the notes value object."""
        return self._notes_vo

    @property
    def id(self) -> Optional[int]:
        """Get the database ID."""
        return self._id

    def __eq__(self, other) -> bool:
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
        return self._notes_vo.has_content()

    def update_fields(self, **kwargs) -> None:
        """
        Update multiple fields at once.

        Args:
            **kwargs: Field names and values to update.
                     Supported fields: name, sector, industry_group, grade, notes

        Raises:
            ValueError: If any field is invalid
        """
        # Create temporary value objects for validation first (atomic operation)
        temp_values = {}

        if "name" in kwargs:
            temp_values["company_name"] = CompanyName(kwargs["name"])
        if "sector" in kwargs:
            sector = kwargs["sector"]
            temp_values["sector_vo"] = Sector(sector) if sector is not None else None
        if "industry_group" in kwargs:
            industry_group = kwargs["industry_group"]
            temp_values["industry_group_vo"] = (
                IndustryGroup(industry_group) if industry_group else None
            )
        if "grade" in kwargs:
            grade_value = kwargs["grade"]
            temp_values["grade_vo"] = (
                Grade(grade_value) if grade_value is not None else None
            )
        if "notes" in kwargs:
            temp_values["notes_vo"] = Notes(kwargs["notes"])

        # Now handle sector-industry domain logic
        new_sector = kwargs.get("sector", self.sector.value if self.sector else None)
        new_industry_group = kwargs.get(
            "industry_group", self.industry_group.value if self.industry_group else None
        )

        # Special logic: if changing sector, check if current industry_group is compatible
        if "sector" in kwargs and "industry_group" not in kwargs:
            # User is only changing sector, check if current industry_group is still valid
            if (
                self.industry_group is not None
                and new_sector is not None
                and not self._sector_industry_service.validate_sector_industry_combination(
                    new_sector, self.industry_group.value
                )
            ):
                # Current industry_group is not valid for new sector, clear it
                new_industry_group = None
                temp_values["industry_group_vo"] = None

        # Validate the final sector-industry combination
        self._validate_sector_industry_combination(new_sector, new_industry_group)

        # All validation passed, now update the actual fields
        if "company_name" in temp_values:
            self._company_name = temp_values["company_name"]
        if "sector_vo" in temp_values:
            self._sector_vo = temp_values["sector_vo"]
        if "industry_group_vo" in temp_values:
            self._industry_group_vo = temp_values["industry_group_vo"]
        if "grade_vo" in temp_values:
            self._grade_vo = temp_values["grade_vo"]
        if "notes_vo" in temp_values:
            self._notes_vo = temp_values["notes_vo"]

    def set_id(self, stock_id: int) -> None:
        """
        Set the database ID (for persistence layer).

        Args:
            stock_id: Database ID

        Raises:
            ValueError: If ID is invalid or already set
        """
        if not isinstance(stock_id, int) or stock_id <= 0:
            raise ValueError("ID must be a positive integer")

        if self._id is not None:
            raise ValueError("ID is already set and cannot be changed")

        self._id = stock_id

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
