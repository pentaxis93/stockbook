"""
Stock domain entity with rich business behavior.

Represents a stock/security in the trading system with business logic
and validation rules encapsulated within the entity.
"""

from typing import Optional
from domain.value_objects.stock_symbol import StockSymbol
from domain.value_objects.money import Money
from domain.value_objects.quantity import Quantity


class StockEntity:
    """
    Rich domain entity representing a stock/security.

    Encapsulates business logic for stock operations including
    validation, calculations, and state management.
    """

    # Valid grade options
    VALID_GRADES = {"A", "B", "C"}

    # Constraints
    MAX_NAME_LENGTH = 200
    MAX_INDUSTRY_LENGTH = 100
    MAX_NOTES_LENGTH = 1000

    def __init__(
        self,
        symbol: StockSymbol,
        name: str,
        industry_group: Optional[str] = None,
        grade: Optional[str] = None,
        notes: str = "",
        stock_id: Optional[int] = None,
    ):
        """
        Initialize Stock entity with validation.

        Args:
            symbol: Stock symbol (value object)
            name: Company name
            industry_group: Industry classification
            grade: Stock grade (A/B/C or None)
            notes: Additional notes
            stock_id: Database ID (for persistence)

        Raises:
            ValueError: If any validation fails
        """
        # Validate inputs
        self._validate_name(name)
        self._validate_industry_group(industry_group)
        self._validate_grade(grade)
        self._validate_notes(notes)

        # Set attributes
        self._symbol = symbol
        self._name = name.strip()
        self._industry_group = industry_group.strip() if industry_group else None
        self._grade = grade
        self._notes = notes.strip()
        self._id = stock_id

    @property
    def symbol(self) -> StockSymbol:
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
        return f"{self.symbol} - {self.name}"

    def __repr__(self) -> str:
        """Developer representation."""
        return (
            f"StockEntity(symbol={self.symbol!r}, name={self.name!r}, "
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

    def is_high_grade(self) -> bool:
        """
        Check if this is a high-grade stock.

        Returns:
            True if grade is 'A', False otherwise
        """
        return self.grade == "A"

    def has_notes(self) -> bool:
        """
        Check if stock has notes.

        Returns:
            True if notes are present and not empty
        """
        return bool(self.notes and self.notes.strip())

    def update_grade(self, new_grade: Optional[str]) -> None:
        """
        Update the stock grade.

        Args:
            new_grade: New grade value (A/B/C or None)

        Raises:
            ValueError: If grade is invalid
        """
        self._validate_grade(new_grade)
        self._grade = new_grade

    def update_notes(self, new_notes: str) -> None:
        """
        Update the stock notes.

        Args:
            new_notes: New notes content

        Raises:
            ValueError: If notes are too long
        """
        self._validate_notes(new_notes)
        self._notes = new_notes.strip()

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

    @classmethod
    def _validate_name(cls, name: str) -> None:
        """Validate company name."""
        if not name or not name.strip():
            raise ValueError("Company name cannot be empty")

        if len(name) > cls.MAX_NAME_LENGTH:
            raise ValueError(
                f"Company name cannot exceed {cls.MAX_NAME_LENGTH} characters"
            )

    @classmethod
    def _validate_industry_group(cls, industry_group: Optional[str]) -> None:
        """Validate industry group."""
        if industry_group is not None and len(industry_group) > cls.MAX_INDUSTRY_LENGTH:
            raise ValueError(
                f"Industry group cannot exceed {cls.MAX_INDUSTRY_LENGTH} characters"
            )

    @classmethod
    def _validate_grade(cls, grade: Optional[str]) -> None:
        """Validate stock grade."""
        if grade is not None and grade not in cls.VALID_GRADES:
            raise ValueError(f"Grade must be one of {cls.VALID_GRADES} or None")

    @classmethod
    def _validate_notes(cls, notes: str) -> None:
        """Validate notes."""
        if len(notes) > cls.MAX_NOTES_LENGTH:
            raise ValueError(f"Notes cannot exceed {cls.MAX_NOTES_LENGTH} characters")
