"""
Create stock command.

Command object encapsulating the intention to create a new stock
with all necessary validation and normalization.
"""

from typing import Any

from src.domain.services.sector_industry_service import SectorIndustryService
from src.domain.value_objects.stock_symbol import StockSymbol


class CreateStockCommand:
    """
    Command to create a new stock in the system.

    Encapsulates all data needed to create a stock, with validation
    to ensure the command is well-formed before execution.
    """

    # Private attributes for type checking
    _symbol: str
    _name: str | None
    _sector: str | None
    _industry_group: str | None
    _grade: str | None
    _notes: str

    def __init__(
        # Rationale: Command objects legitimately need all parameters to capture user intent.
        # These are not domain entities but DTOs that transfer complete information.
        self,
        symbol: str,
        name: str | None = None,
        sector: str | None = None,
        industry_group: str | None = None,
        grade: str | None = None,
        notes: str = "",
    ):
        """
        Initialize CreateStockCommand with validation.

        Args:
            symbol: Stock symbol (will be normalized)
            name: Company name (optional)
            sector: Sector classification
            industry_group: Industry classification (must belong to sector if provided)
            grade: Stock grade (A/B/C or None)
            notes: Additional notes

        Raises:
            ValueError: If validation fails
        """
        # Normalize and validate all inputs
        normalized_inputs = self._normalize_and_validate_inputs(
            symbol, name, sector, industry_group, grade, notes
        )

        # Set all attributes using the normalized values
        self._set_attributes(normalized_inputs)

    @property
    def symbol(self) -> str:
        """Get the stock symbol."""
        return self._symbol

    @property
    def name(self) -> str | None:
        """Get the company name."""
        return self._name

    @property
    def sector(self) -> str | None:
        """Get the sector."""
        return self._sector

    @property
    def industry_group(self) -> str | None:
        """Get the industry group."""
        return self._industry_group

    @property
    def grade(self) -> str | None:
        """Get the stock grade."""
        return self._grade

    @property
    def notes(self) -> str:
        """Get the notes."""
        return self._notes

    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent modification after initialization (immutability)."""
        if hasattr(self, "_symbol"):  # Object is already initialized
            raise AttributeError("Cannot modify immutable CreateStockCommand")
        super().__setattr__(name, value)

    def __eq__(self, other: Any) -> bool:
        """Check equality based on all properties."""
        if not isinstance(other, CreateStockCommand):
            return False

        return (
            self.symbol == other.symbol
            and self.name == other.name
            and self.sector == other.sector
            and self.industry_group == other.industry_group
            and self.grade == other.grade
            and self.notes == other.notes
        )

    def __hash__(self) -> int:
        """Hash based on all properties."""
        return hash(
            (
                self.symbol,
                self.name,
                self.sector,
                self.industry_group,
                self.grade,
                self.notes,
            )
        )

    def __str__(self) -> str:
        """String representation for display."""
        return f"CreateStockCommand(symbol={self.symbol!r}, name={self.name!r})"

    def __repr__(self) -> str:
        """Developer representation."""
        return (
            f"CreateStockCommand(symbol={self.symbol!r}, name={self.name!r}, "
            f"sector={self.sector!r}, industry_group={self.industry_group!r}, grade={self.grade!r}, "
            f"notes={self.notes!r})"
        )

    def _normalize_and_validate_inputs(
        self,
        symbol: str,
        name: str | None,
        sector: str | None,
        industry_group: str | None,
        grade: str | None,
        notes: str,
    ) -> dict[str, Any]:
        """Normalize and validate all inputs, returning normalized values."""
        # Normalize inputs
        symbol = self._normalize_symbol(symbol)
        name = self._normalize_name(name)
        sector = self._normalize_sector(sector)
        industry_group = self._normalize_industry_group(industry_group)
        notes = self._normalize_notes(notes)

        # Validate inputs
        self._validate_symbol(symbol)
        self._validate_name(name)
        self._validate_grade(grade)
        self._validate_sector_industry_combination(sector, industry_group)

        return {
            "symbol": symbol,
            "name": name,
            "sector": sector,
            "industry_group": industry_group,
            "grade": grade,
            "notes": notes,
        }

    def _set_attributes(self, normalized_inputs: dict[str, Any]) -> None:
        """Set all attributes using normalized inputs."""
        object.__setattr__(self, "_symbol", normalized_inputs["symbol"])
        object.__setattr__(self, "_name", normalized_inputs["name"])
        object.__setattr__(self, "_sector", normalized_inputs["sector"])
        object.__setattr__(self, "_industry_group", normalized_inputs["industry_group"])
        object.__setattr__(self, "_grade", normalized_inputs["grade"])
        object.__setattr__(self, "_notes", normalized_inputs["notes"])

    @staticmethod
    def _normalize_symbol(symbol: str) -> str:
        """Normalize symbol format."""
        # Type checking is handled by type annotations
        return symbol.strip().upper()

    @staticmethod
    def _normalize_name(name: str | None) -> str | None:
        """Normalize company name."""
        if name is None:
            return None
        # Type checking is handled by type annotations
        return name.strip() if name.strip() else None

    @staticmethod
    def _normalize_sector(sector: str | None) -> str | None:
        """Normalize sector."""
        if sector is None:
            return None
        # Type checking is handled by type annotations
        normalized = sector.strip()
        return normalized if normalized else None

    @staticmethod
    def _normalize_industry_group(industry_group: str | None) -> str | None:
        """Normalize industry group."""
        if industry_group is None:
            return None
        normalized = industry_group.strip()
        return normalized if normalized else None

    @staticmethod
    def _normalize_notes(notes: str) -> str:
        """Normalize notes."""
        # Type checking is handled by type annotations
        return notes.strip()

    @staticmethod
    def _validate_symbol(symbol: str) -> None:
        """Validate symbol format."""
        if not symbol:
            raise ValueError("Symbol cannot be empty")

        # Use StockSymbol validation
        if not StockSymbol.is_valid(symbol):
            raise ValueError("Invalid symbol format")

    @staticmethod
    def _validate_name(name: str | None) -> None:
        """Validate company name."""
        # Name is now optional, so no validation needed
        pass

    @staticmethod
    def _validate_grade(grade: str | None) -> None:
        """Validate stock grade."""
        if grade is not None:
            valid_grades = {"A", "B", "C"}
            if grade not in valid_grades:
                raise ValueError(
                    f"Invalid grade. Must be one of {valid_grades} or None"
                )

    @staticmethod
    def _validate_sector_industry_combination(
        sector: str | None, industry_group: str | None
    ) -> None:
        """Validate sector-industry combination."""
        # If no industry group, sector can be anything (or None)
        if industry_group is None:
            return

        # If industry group is provided, sector must also be provided
        if sector is None:
            raise ValueError("Sector must be provided when industry_group is specified")

        # Validate the combination using domain service
        service = SectorIndustryService()
        service.validate_sector_industry_combination_strict(sector, industry_group)
