"""Stock domain entity with rich business behavior.

Represents a stock/security in the trading system with business logic
and validation rules encapsulated within the entity.
"""

from __future__ import annotations

from typing import Any, Self

from src.domain.entities.entity import Entity
from src.domain.value_objects import (
    CompanyName,
    Grade,
    IndustryGroup,
    Notes,
    Sector,
    StockSymbol,
)


class Stock(Entity):
    """Rich domain entity representing a stock/security.

    Encapsulates business logic for stock operations including
    validation, calculations, and state management.
    """

    # Type annotations for instance variables
    _symbol: StockSymbol
    _company_name: CompanyName | None
    _sector: Sector | None
    _industry_group: IndustryGroup | None
    _grade: Grade | None
    _notes: Notes

    class Builder:
        """Builder for Stock to manage multiple parameters elegantly."""

        def __init__(self) -> None:
            """Initialize builder with default values."""
            self.symbol: StockSymbol | None = None
            self.company_name: CompanyName | None = None
            self.sector: Sector | None = None
            self.industry_group: IndustryGroup | None = None
            self.grade: Grade | None = None
            self.notes: Notes | None = None
            self.entity_id: str | None = None

        def with_symbol(self, symbol: StockSymbol) -> Self:
            """Set the stock symbol."""
            self.symbol = symbol
            return self

        def with_company_name(self, company_name: CompanyName | None) -> Self:
            """Set the company name."""
            self.company_name = company_name
            return self

        def with_sector(self, sector: Sector | None) -> Self:
            """Set the sector."""
            self.sector = sector
            return self

        def with_industry_group(self, industry_group: IndustryGroup | None) -> Self:
            """Set the industry group."""
            self.industry_group = industry_group
            return self

        def with_grade(self, grade: Grade | None) -> Self:
            """Set the grade."""
            self.grade = grade
            return self

        def with_notes(self, notes: Notes | None) -> Self:
            """Set the notes."""
            self.notes = notes
            return self

        def with_id(self, entity_id: str | None) -> Self:
            """Set the entity ID."""
            self.entity_id = entity_id
            return self

        def build(self) -> Stock:
            """Build and return the Stock instance."""
            return Stock(_builder_instance=self)

    def __init__(self, *, _builder_instance: Stock.Builder | None = None):
        """Initialize Stock entity through builder pattern."""
        if _builder_instance is None:
            raise ValueError("Stock must be created through Builder")

        # Extract values from builder
        symbol = _builder_instance.symbol
        company_name = _builder_instance.company_name
        sector = _builder_instance.sector
        industry_group = _builder_instance.industry_group
        grade = _builder_instance.grade
        notes = _builder_instance.notes
        entity_id = _builder_instance.entity_id

        # Validate required fields
        if symbol is None:
            raise ValueError("Symbol is required")

        # Initialize sector industry service for validation (import here to avoid circular imports)
        from src.domain.services.sector_industry_service import (  # pylint: disable=import-outside-toplevel; Rationale: This import must be inside the method to prevent circular dependencies; between domain entities and domain services. The Stock entity needs SectorIndustryService; for validation, but the service may also reference Stock, creating a circular import.
            SectorIndustryService,
        )

        self._sector_industry_service = SectorIndustryService()

        # Initialize parent
        super().__init__(id=entity_id)

        # Store value objects directly (they're already validated)
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
    def company_name(self) -> CompanyName | None:
        """Get the company name value object."""
        return self._company_name

    @property
    def sector(self) -> Sector | None:
        """Get the sector value object."""
        return self._sector

    @property
    def industry_group(self) -> IndustryGroup | None:
        """Get the industry group value object."""
        return self._industry_group

    @property
    def grade(self) -> Grade | None:
        """Get the grade value object."""
        return self._grade

    @property
    def notes(self) -> Notes:
        """Get the notes value object."""
        return self._notes

    def __str__(self) -> str:
        """String representation for display."""
        if self.company_name:
            return f"{self.symbol} - {self.company_name.value}"
        return str(self.symbol)

    def __repr__(self) -> str:
        """Developer representation."""
        company_repr = repr(self.company_name) if self.company_name else None
        return (
            f"Stock(symbol={self.symbol!r}, company_name={company_repr}, "
            f"grade={self.grade!r})"
        )

    def has_notes(self) -> bool:
        """Check if stock has notes.

        Returns:
            True if notes are present and not empty
        """
        return self._notes.has_content()

    def update_fields(self, **kwargs: Any) -> None:
        """Update multiple fields at once.

        Args:
            **kwargs: Field names and values to update.
                     Supported fields: symbol, name, sector, industry_group, grade, notes

        Raises:
            ValueError: If any field is invalid
        """
        # Create temporary value objects for validation first (atomic operation)
        temp_values = self._create_temp_value_objects(kwargs)

        # Handle sector-industry domain logic and validation
        self._validate_and_adjust_sector_industry(kwargs, temp_values)

        # All validation passed, now update the actual fields
        self._apply_field_updates(temp_values)

    def _create_temp_value_objects(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Create temporary value objects for validation."""
        temp_values: dict[str, Any] = {}

        # Create value objects in separate methods to reduce complexity
        self._create_symbol(kwargs, temp_values)
        self._create_company_name(kwargs, temp_values)
        self._create_sector(kwargs, temp_values)
        self._create_industry_group(kwargs, temp_values)
        self._create_grade(kwargs, temp_values)
        self._create_notes(kwargs, temp_values)

        return temp_values

    def _create_symbol(
        self, kwargs: dict[str, Any], temp_values: dict[str, Any]
    ) -> None:
        """Create symbol value object if present."""
        if "symbol" in kwargs:
            symbol = kwargs["symbol"]
            temp_values["symbol"] = StockSymbol(symbol)

    def _create_company_name(
        self, kwargs: dict[str, Any], temp_values: dict[str, Any]
    ) -> None:
        """Create company name value object if present."""
        if "name" in kwargs:
            name = kwargs["name"]
            temp_values["company_name"] = CompanyName(name) if name else None

    def _create_sector(
        self, kwargs: dict[str, Any], temp_values: dict[str, Any]
    ) -> None:
        """Create sector value object if present."""
        if "sector" in kwargs:
            sector = kwargs["sector"]
            temp_values["sector"] = Sector(sector) if sector is not None else None

    def _create_industry_group(
        self, kwargs: dict[str, Any], temp_values: dict[str, Any]
    ) -> None:
        """Create industry group value object if present."""
        if "industry_group" in kwargs:
            industry_group = kwargs["industry_group"]
            temp_values["industry_group"] = (
                IndustryGroup(industry_group) if industry_group else None
            )

    def _create_grade(
        self, kwargs: dict[str, Any], temp_values: dict[str, Any]
    ) -> None:
        """Create grade value object if present."""
        if "grade" in kwargs:
            grade_value = kwargs["grade"]
            temp_values["grade"] = (
                Grade(grade_value) if grade_value is not None else None
            )

    def _create_notes(
        self, kwargs: dict[str, Any], temp_values: dict[str, Any]
    ) -> None:
        """Create notes value object if present."""
        if "notes" in kwargs:
            temp_values["notes"] = Notes(kwargs["notes"])

    def _validate_and_adjust_sector_industry(
        self, kwargs: dict[str, Any], temp_values: dict[str, Any]
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
        self, new_sector: str | None
    ) -> bool:
        """Check if current industry group should be cleared for new sector."""
        return (
            self.industry_group is not None
            and new_sector is not None
            and not self._sector_industry_service.validate_sector_industry_combination(
                new_sector, self.industry_group.value
            )
        )

    def _apply_field_updates(self, temp_values: dict[str, Any]) -> None:
        """Apply validated field updates to the entity."""
        # Map of field names to their corresponding attributes
        field_mapping = {
            "symbol": "_symbol",
            "company_name": "_company_name",
            "sector": "_sector",
            "industry_group": "_industry_group",
            "grade": "_grade",
            "notes": "_notes",
        }

        # Apply updates for fields that are present
        for field, attr in field_mapping.items():
            if field in temp_values:
                setattr(self, attr, temp_values[field])

    def _validate_sector_industry_combination(
        self, sector: str | None, industry_group: str | None
    ) -> None:
        """Validate that sector and industry_group combination is valid.

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
