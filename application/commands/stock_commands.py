"""
Stock-related command objects.

Commands encapsulate user intentions to modify stock-related state
and contain all necessary data for the operation.
"""

from typing import Optional
from domain.value_objects.stock_symbol import StockSymbol


class CreateStockCommand:
    """
    Command to create a new stock in the system.

    Encapsulates all data needed to create a stock, with validation
    to ensure the command is well-formed before execution.
    """

    # Private attributes for type checking
    _symbol: str
    _name: str
    _industry_group: Optional[str]
    _grade: Optional[str]
    _notes: str

    def __init__(
        self,
        symbol: str,
        name: str,
        industry_group: Optional[str] = None,
        grade: Optional[str] = None,
        notes: str = "",
    ):
        """
        Initialize CreateStockCommand with validation.

        Args:
            symbol: Stock symbol (will be normalized)
            name: Company name
            industry_group: Industry classification
            grade: Stock grade (A/B/C or None)
            notes: Additional notes

        Raises:
            ValueError: If validation fails
        """
        # Normalize and validate inputs
        symbol = self._normalize_symbol(symbol)
        name = self._normalize_name(name)
        industry_group = self._normalize_industry_group(industry_group)
        notes = self._normalize_notes(notes)

        # Validate inputs
        self._validate_symbol(symbol)
        self._validate_name(name)
        self._validate_grade(grade)

        # Use object.__setattr__ to bypass immutability during initialization
        object.__setattr__(self, "_symbol", symbol)
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_industry_group", industry_group)
        object.__setattr__(self, "_grade", grade)
        object.__setattr__(self, "_notes", notes)

    @property
    def symbol(self) -> str:
        """Get the stock symbol."""
        return self._symbol

    @property
    def name(self) -> str:
        """Get the company name."""
        return self._name

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

    def __setattr__(self, name, value):
        """Prevent modification after initialization (immutability)."""
        if hasattr(self, "_symbol"):  # Object is already initialized
            raise AttributeError(f"Cannot modify immutable CreateStockCommand")
        super().__setattr__(name, value)

    def __eq__(self, other) -> bool:
        """Check equality based on all properties."""
        if not isinstance(other, CreateStockCommand):
            return False

        return (
            self.symbol == other.symbol
            and self.name == other.name
            and self.industry_group == other.industry_group
            and self.grade == other.grade
            and self.notes == other.notes
        )

    def __hash__(self) -> int:
        """Hash based on all properties."""
        return hash(
            (self.symbol, self.name, self.industry_group, self.grade, self.notes)
        )

    def __str__(self) -> str:
        """String representation for display."""
        return f"CreateStockCommand(symbol='{self.symbol}', name='{self.name}')"

    def __repr__(self) -> str:
        """Developer representation."""
        return (
            f"CreateStockCommand(symbol='{self.symbol}', name='{self.name}', "
            f"industry_group={self.industry_group!r}, grade={self.grade!r}, "
            f"notes='{self.notes}')"
        )

    @staticmethod
    def _normalize_symbol(symbol: str) -> str:
        """Normalize symbol format."""
        if not isinstance(symbol, str):
            raise ValueError("Symbol must be a string")
        return symbol.strip().upper()

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normalize company name."""
        if not isinstance(name, str):
            raise ValueError("Name must be a string")
        return name.strip()

    @staticmethod
    def _normalize_industry_group(industry_group: Optional[str]) -> Optional[str]:
        """Normalize industry group."""
        if industry_group is None:
            return None
        if not isinstance(industry_group, str):
            raise ValueError("Industry group must be a string or None")
        normalized = industry_group.strip()
        return normalized if normalized else None

    @staticmethod
    def _normalize_notes(notes: str) -> str:
        """Normalize notes."""
        if not isinstance(notes, str):
            raise ValueError("Notes must be a string")
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
    def _validate_name(name: str) -> None:
        """Validate company name."""
        if not name:
            raise ValueError("Name cannot be empty")

    @staticmethod
    def _validate_grade(grade: Optional[str]) -> None:
        """Validate stock grade."""
        if grade is not None:
            valid_grades = {"A", "B", "C"}
            if grade not in valid_grades:
                raise ValueError(
                    f"Invalid grade. Must be one of {valid_grades} or None"
                )
