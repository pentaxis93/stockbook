"""
Stock-related command objects.

Commands encapsulate user intentions to modify stock-related state
and contain all necessary data for the operation.
"""

from typing import Any, Dict, Optional

from src.domain.value_objects.stock_symbol import StockSymbol


class CreateStockCommand:
    """
    Command to create a new stock in the system.

    Encapsulates all data needed to create a stock, with validation
    to ensure the command is well-formed before execution.
    """

    # Private attributes for type checking
    _symbol: str
    _name: Optional[str]
    _sector: Optional[str]
    _industry_group: Optional[str]
    _grade: Optional[str]
    _notes: str

    def __init__(
        self,
        symbol: str,
        name: Optional[str] = None,
        sector: Optional[str] = None,
        industry_group: Optional[str] = None,
        grade: Optional[str] = None,
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
    def name(self) -> Optional[str]:
        """Get the company name."""
        return self._name

    @property
    def sector(self) -> Optional[str]:
        """Get the sector."""
        return self._sector

    @property
    def industry_group(self) -> Optional[str]:
        """Get the industry group."""
        return self._industry_group

    @property
    def grade(self) -> Optional[str]:
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
        name: Optional[str],
        sector: Optional[str],
        industry_group: Optional[str],
        grade: Optional[str],
        notes: str,
    ) -> Dict[str, Any]:
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

    def _set_attributes(self, normalized_inputs: Dict[str, Any]) -> None:
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
    def _normalize_name(name: Optional[str]) -> Optional[str]:
        """Normalize company name."""
        if name is None:
            return None
        # Type checking is handled by type annotations
        return name.strip() if name.strip() else None

    @staticmethod
    def _normalize_sector(sector: Optional[str]) -> Optional[str]:
        """Normalize sector."""
        if sector is None:
            return None
        # Type checking is handled by type annotations
        normalized = sector.strip()
        return normalized if normalized else None

    @staticmethod
    def _normalize_industry_group(industry_group: Optional[str]) -> Optional[str]:
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
    def _validate_name(name: Optional[str]) -> None:
        """Validate company name."""
        # Name is now optional, so no validation needed
        pass

    @staticmethod
    def _validate_grade(grade: Optional[str]) -> None:
        """Validate stock grade."""
        if grade is not None:
            valid_grades = {"A", "B", "C"}
            if grade not in valid_grades:
                raise ValueError(
                    f"Invalid grade. Must be one of {valid_grades} or None"
                )

    @staticmethod
    def _validate_sector_industry_combination(
        sector: Optional[str], industry_group: Optional[str]
    ) -> None:
        """Validate sector-industry combination."""
        # Import here to avoid circular imports
        from src.domain.services.sector_industry_service import SectorIndustryService

        # If no industry group, sector can be anything (or None)
        if industry_group is None:
            return

        # If industry group is provided, sector must also be provided
        if sector is None:
            raise ValueError("Sector must be provided when industry_group is specified")

        # Validate the combination using domain service
        service = SectorIndustryService()
        service.validate_sector_industry_combination_strict(sector, industry_group)


class UpdateStockCommand:
    """
    Command to update an existing stock in the system.

    Encapsulates all data needed to update a stock, with validation
    to ensure the command is well-formed before execution.
    """

    # Private attributes for type checking
    _stock_id: str
    _symbol: Optional[str]
    _name: Optional[str]
    _sector: Optional[str]
    _industry_group: Optional[str]
    _grade: Optional[str]
    _notes: Optional[str]

    def __init__(
        self,
        stock_id: str,
        symbol: Optional[str] = None,
        name: Optional[str] = None,
        sector: Optional[str] = None,
        industry_group: Optional[str] = None,
        grade: Optional[str] = None,
        notes: Optional[str] = None,
    ):
        """
        Initialize UpdateStockCommand with validation.

        Args:
            stock_id: ID of the stock to update
            symbol: New stock symbol (None to keep unchanged)
            name: New company name (None to keep unchanged)
            sector: New sector classification (None to keep unchanged)
            industry_group: New industry classification (None to keep unchanged)
            grade: New stock grade (A/B/C or None)
            notes: New notes (None to keep unchanged)

        Raises:
            ValueError: If validation fails
        """
        # Validate and normalize all inputs
        normalized_inputs = self._validate_and_normalize_inputs(
            stock_id, symbol, name, sector, industry_group, grade, notes
        )

        # Set all attributes using the normalized values
        self._set_attributes(normalized_inputs)

    @property
    def stock_id(self) -> str:
        """Get the stock ID."""
        return self._stock_id

    @property
    def symbol(self) -> Optional[str]:
        """Get the stock symbol."""
        return self._symbol

    @property
    def name(self) -> Optional[str]:
        """Get the company name."""
        return self._name

    @property
    def sector(self) -> Optional[str]:
        """Get the sector."""
        return self._sector

    @property
    def industry_group(self) -> Optional[str]:
        """Get the industry group."""
        return self._industry_group

    @property
    def grade(self) -> Optional[str]:
        """Get the stock grade."""
        return self._grade

    @property
    def notes(self) -> Optional[str]:
        """Get the notes."""
        return self._notes

    def has_updates(self) -> bool:
        """
        Check if any fields are being updated.

        Returns:
            True if at least one field is being updated
        """
        return any(
            [
                self._symbol is not None,
                self._name is not None,
                self._sector is not None,
                self._industry_group is not None,
                self._grade is not None,
                self._notes is not None,
            ]
        )

    def get_update_fields(self) -> Dict[str, Any]:
        """
        Get dictionary of fields that are being updated.

        Returns:
            Dictionary with field names as keys and values as values
        """
        fields: Dict[str, Any] = {}
        if self._symbol is not None:
            fields["symbol"] = self._symbol
        if self._name is not None:
            fields["name"] = self._name
        if self._sector is not None:
            fields["sector"] = self._sector
        if self._industry_group is not None:
            fields["industry_group"] = self._industry_group
        if self._grade is not None:
            fields["grade"] = self._grade
        if self._notes is not None:
            fields["notes"] = self._notes
        return fields

    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent modification after initialization (immutability)."""
        if hasattr(self, "_stock_id"):  # Object is already initialized
            raise AttributeError("Cannot modify immutable UpdateStockCommand")
        super().__setattr__(name, value)

    def __eq__(self, other: Any) -> bool:
        """Check equality based on all properties."""
        if not isinstance(other, UpdateStockCommand):
            return False

        return (
            self.stock_id == other.stock_id
            and self.symbol == other.symbol
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
                self.stock_id,
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
        update_fields = list(self.get_update_fields().keys())
        return f"UpdateStockCommand(stock_id={self.stock_id}, updating={update_fields})"

    def __repr__(self) -> str:
        """Developer representation."""
        return (
            f"UpdateStockCommand(stock_id={self.stock_id}, symbol={self.symbol!r}, name={self.name!r}, "
            f"sector={self.sector!r}, industry_group={self.industry_group!r}, grade={self.grade!r}, "
            f"notes={self.notes!r})"
        )

    def _validate_and_normalize_inputs(
        self,
        stock_id: str,
        symbol: Optional[str],
        name: Optional[str],
        sector: Optional[str],
        industry_group: Optional[str],
        grade: Optional[str],
        notes: Optional[str],
    ) -> Dict[str, Any]:
        """Validate and normalize all inputs, returning normalized values."""
        # Validate stock_id
        self._validate_stock_id(stock_id)

        # Normalize and validate symbol
        if symbol is not None:
            symbol = self._normalize_symbol(symbol)
            self._validate_symbol(symbol)

        # Normalize and validate inputs
        if name is not None:
            name = self._normalize_name(name)
            self._validate_name(name)

        if sector is not None:
            sector = self._normalize_sector(sector)

        if industry_group is not None:
            industry_group = self._normalize_industry_group(industry_group)

        if notes is not None:
            notes = self._normalize_notes(notes)

        # Validate grade
        self._validate_grade(grade)

        return {
            "stock_id": stock_id,
            "symbol": symbol,
            "name": name,
            "sector": sector,
            "industry_group": industry_group,
            "grade": grade,
            "notes": notes,
        }

    def _set_attributes(self, normalized_inputs: Dict[str, Any]) -> None:
        """Set all attributes using normalized inputs."""
        object.__setattr__(self, "_stock_id", normalized_inputs["stock_id"])
        object.__setattr__(self, "_symbol", normalized_inputs["symbol"])
        object.__setattr__(self, "_name", normalized_inputs["name"])
        object.__setattr__(self, "_sector", normalized_inputs["sector"])
        object.__setattr__(self, "_industry_group", normalized_inputs["industry_group"])
        object.__setattr__(self, "_grade", normalized_inputs["grade"])
        object.__setattr__(self, "_notes", normalized_inputs["notes"])

    @staticmethod
    def _validate_stock_id(stock_id: str) -> None:
        """Validate stock ID."""
        if not stock_id.strip():
            raise ValueError("Stock ID must be a non-empty string")

    @staticmethod
    def _normalize_symbol(symbol: str) -> str:
        """Normalize symbol format."""
        # Type checking is handled by type annotations
        return symbol.strip().upper()

    @staticmethod
    def _validate_symbol(symbol: str) -> None:
        """Validate symbol format."""
        if not symbol:
            raise ValueError("Symbol cannot be empty")

        # Use StockSymbol validation
        if not StockSymbol.is_valid(symbol):
            raise ValueError("Invalid symbol format")

    @staticmethod
    def _normalize_name(name: Optional[str]) -> Optional[str]:
        """Normalize company name."""
        if name is None:
            return None  # pragma: no cover
        # Type checking is handled by type annotations
        return name.strip() if name.strip() else None

    @staticmethod
    def _normalize_sector(sector: Optional[str]) -> Optional[str]:
        """Normalize sector."""
        if sector is None:
            return None  # pragma: no cover
        # Type checking is handled by type annotations
        normalized = sector.strip()
        return normalized if normalized else None

    @staticmethod
    def _normalize_industry_group(industry_group: str) -> Optional[str]:
        """Normalize industry group."""
        # Type checking is handled by type annotations
        normalized = industry_group.strip()
        return normalized if normalized else None

    @staticmethod
    def _normalize_notes(notes: str) -> str:
        """Normalize notes."""
        # Type checking is handled by type annotations
        return notes.strip()

    @staticmethod
    def _validate_name(name: Optional[str]) -> None:
        """Validate company name."""
        # Name is now optional, so no validation needed
        pass

    @staticmethod
    def _validate_grade(grade: Optional[str]) -> None:
        """Validate stock grade."""
        if grade is not None:
            valid_grades = {"A", "B", "C"}
            if grade not in valid_grades:
                raise ValueError(
                    f"Invalid grade. Must be one of {valid_grades} or None"
                )
