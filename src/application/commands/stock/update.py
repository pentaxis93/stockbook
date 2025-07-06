"""Update stock command.

Command object encapsulating the intention to update an existing stock
with all necessary validation and normalization.
"""

from dataclasses import dataclass
from typing import Any

from src.domain.value_objects.stock_symbol import StockSymbol


@dataclass(frozen=True)
class UpdateStockInputs:
    """Input data for updating a stock."""

    stock_id: str
    symbol: str | None = None
    name: str | None = None
    sector: str | None = None
    industry_group: str | None = None
    grade: str | None = None
    notes: str | None = None


class UpdateStockCommand:
    """Command to update an existing stock in the system.

    Encapsulates all data needed to update a stock, with validation
    to ensure the command is well-formed before execution.
    """

    # Private attributes for type checking
    _stock_id: str
    _symbol: str | None
    _name: str | None
    _sector: str | None
    _industry_group: str | None
    _grade: str | None
    _notes: str | None

    def __init__(self, inputs: UpdateStockInputs) -> None:
        """Initialize UpdateStockCommand with validation.

        Args:
            inputs: Input data for updating a stock

        Raises:
            ValueError: If validation fails
        """
        # Validate and normalize all inputs
        normalized_inputs = self._validate_and_normalize_inputs(inputs)

        # Set all attributes using the normalized values
        self._set_attributes(normalized_inputs)

    @property
    def stock_id(self) -> str:
        """Get the stock ID."""
        return self._stock_id

    @property
    def symbol(self) -> str | None:
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
    def notes(self) -> str | None:
        """Get the notes."""
        return self._notes

    def has_updates(self) -> bool:
        """Check if any fields are being updated.

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

    def get_update_fields(self) -> dict[str, Any]:
        """Get dictionary of fields that are being updated.

        Returns:
            Dictionary with field names as keys and values as values
        """
        field_mapping = {
            "symbol": self._symbol,
            "name": self._name,
            "sector": self._sector,
            "industry_group": self._industry_group,
            "grade": self._grade,
            "notes": self._notes,
        }
        return {k: v for k, v in field_mapping.items() if v is not None}

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
            f"UpdateStockCommand(stock_id={self.stock_id!r}, symbol={self.symbol!r}, "
            f"name={self.name!r}, sector={self.sector!r}, "
            f"industry_group={self.industry_group!r}, grade={self.grade!r}, "
            f"notes={self.notes!r})"
        )

    def _validate_and_normalize_inputs(
        self, inputs: UpdateStockInputs
    ) -> dict[str, Any]:
        """Validate and normalize all inputs, returning normalized values."""
        # Validate stock_id
        self._validate_stock_id(inputs.stock_id)

        # Normalize and validate symbol
        symbol = inputs.symbol
        if symbol is not None:
            symbol = self._normalize_symbol(symbol)
            self._validate_symbol(symbol)

        # Normalize and validate inputs
        name = inputs.name
        if name is not None:
            name = self._normalize_name(name)
            self._validate_name(name)

        sector = inputs.sector
        if sector is not None:
            sector = self._normalize_sector(sector)

        industry_group = inputs.industry_group
        if industry_group is not None:
            industry_group = self._normalize_industry_group(industry_group)

        notes = inputs.notes
        if notes is not None:
            notes = self._normalize_notes(notes)

        # Validate grade
        self._validate_grade(inputs.grade)

        return {
            "stock_id": inputs.stock_id,
            "symbol": symbol,
            "name": name,
            "sector": sector,
            "industry_group": industry_group,
            "grade": inputs.grade,
            "notes": notes,
        }

    def _set_attributes(self, normalized_inputs: dict[str, Any]) -> None:
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
    def _normalize_name(name: str | None) -> str | None:
        """Normalize company name."""
        if name is None:
            return None  # pragma: no cover
        # Type checking is handled by type annotations
        return name.strip() if name.strip() else None

    @staticmethod
    def _normalize_sector(sector: str | None) -> str | None:
        """Normalize sector."""
        if sector is None:
            return None  # pragma: no cover
        # Type checking is handled by type annotations
        normalized = sector.strip()
        return normalized if normalized else None

    @staticmethod
    def _normalize_industry_group(industry_group: str) -> str | None:
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
