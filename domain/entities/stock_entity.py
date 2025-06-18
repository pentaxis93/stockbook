"""
Stock domain entity with rich business behavior.

Represents a stock/security in the trading system with business logic
and validation rules encapsulated within the entity.
"""

from typing import Optional

from domain.value_objects import CompanyName, IndustryGroup, Notes
from domain.value_objects.stock_symbol import StockSymbol
from shared_kernel.value_objects import Money, Quantity


class StockEntity:
    """
    Rich domain entity representing a stock/security.

    Encapsulates business logic for stock operations including
    validation, calculations, and state management.
    """

    # Valid grade options
    VALID_GRADES = {"A", "B", "C"}

    def __init__(
        self,
        symbol: StockSymbol,
        name: str = "",
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
        # Create value objects (validation delegated to them)
        self._symbol = symbol
        self._company_name = CompanyName(name)
        self._industry_group_vo = (
            IndustryGroup(industry_group) if industry_group else None
        )
        self._notes_vo = Notes(notes)

        # Validate grade (still entity's responsibility as it's domain-specific)
        self._validate_grade(grade)
        self._grade = grade
        self._id = stock_id

    @property
    def symbol(self) -> StockSymbol:
        """Get the stock symbol."""
        return self._symbol

    @property
    def company_name(self) -> CompanyName:
        """Get the company name value object."""
        return self._company_name

    @property
    def name(self) -> str:
        """Get the company name as string (backward compatibility)."""
        return self._company_name.value

    @property
    def industry_group_vo(self) -> Optional[IndustryGroup]:
        """Get the industry group value object."""
        return self._industry_group_vo

    @property
    def industry_group(self) -> Optional[str]:
        """Get the industry group as string (backward compatibility)."""
        return self._industry_group_vo.value if self._industry_group_vo else None

    @property
    def grade(self) -> Optional[str]:
        """Get the stock grade."""
        return self._grade

    @property
    def notes_vo(self) -> Notes:
        """Get the notes value object."""
        return self._notes_vo

    @property
    def notes(self) -> str:
        """Get the notes as string (backward compatibility)."""
        return self._notes_vo.value

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
                     Supported fields: name, industry_group, grade, notes

        Raises:
            ValueError: If any field is invalid
        """
        # Create temporary value objects for validation (atomic operation)
        temp_values = {}

        if "name" in kwargs:
            temp_values["company_name"] = CompanyName(kwargs["name"])
        if "industry_group" in kwargs:
            industry_group = kwargs["industry_group"]
            temp_values["industry_group_vo"] = (
                IndustryGroup(industry_group) if industry_group else None
            )
        if "grade" in kwargs:
            self._validate_grade(kwargs["grade"])
            temp_values["grade"] = kwargs["grade"]
        if "notes" in kwargs:
            temp_values["notes_vo"] = Notes(kwargs["notes"])

        # All validation passed, now update the actual fields
        if "company_name" in temp_values:
            self._company_name = temp_values["company_name"]
        if "industry_group_vo" in temp_values:
            self._industry_group_vo = temp_values["industry_group_vo"]
        if "grade" in temp_values:
            self._grade = temp_values["grade"]
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

    @classmethod
    def _validate_grade(cls, grade: Optional[str]) -> None:
        """Validate stock grade."""
        if grade is not None and grade not in cls.VALID_GRADES:
            raise ValueError(f"Grade must be one of {cls.VALID_GRADES} or None")
