"""
Stock view models for presentation layer.

Provides data transfer objects and view models for stock-related UI operations,
handling validation, transformation, and display logic.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from application.commands.stock_commands import CreateStockCommand
from application.dto.stock_dto import StockDto


@dataclass
class CreateStockRequest:
    """Request model for creating a new stock."""

    symbol: str
    name: str
    industry_group: Optional[str] = field(default=None)
    grade: Optional[str] = field(default=None)
    notes: str = field(default="")

    def validate(self) -> Dict[str, str]:
        """
        Validate the request data.

        Returns:
            Dictionary of field errors, empty if valid
        """
        errors = {}

        # Validate symbol
        if not self.symbol or not self.symbol.strip():
            errors["symbol"] = "Stock symbol cannot be empty"
        elif not self._is_valid_symbol_format(self.symbol.strip().upper()):
            errors["symbol"] = "Invalid stock symbol format. Use 1-5 uppercase letters."

        # Validate name
        if not self.name or not self.name.strip():
            errors["name"] = "Stock name cannot be empty"
        elif len(self.name.strip()) > 200:
            errors["name"] = "Name cannot exceed 200 characters"

        # Validate grade
        if self.grade and self.grade.upper() not in ["A", "B", "C"]:
            errors["grade"] = "Grade must be A, B, C, or empty"

        return errors

    def sanitize(self) -> "CreateStockRequest":
        """
        Sanitize and normalize input data.

        Returns:
            New instance with sanitized data
        """
        return CreateStockRequest(
            symbol=self.symbol.strip().upper() if self.symbol else "",
            name=self.name.strip() if self.name else "",
            industry_group=self.industry_group.strip() if self.industry_group else None,
            grade=self.grade.strip().upper() if self.grade else None,
            notes=self.notes.strip() if self.notes else "",
        )

    def to_command(self) -> CreateStockCommand:
        """
        Convert to application command.

        Returns:
            CreateStockCommand for application service
        """
        sanitized = self.sanitize()
        return CreateStockCommand(
            symbol=sanitized.symbol,
            name=sanitized.name,
            industry_group=sanitized.industry_group,
            grade=sanitized.grade,
            notes=sanitized.notes,
        )

    def _is_valid_symbol_format(self, symbol: str) -> bool:
        """Check if symbol matches expected format."""
        pattern = r"^[A-Z]{1,5}$"
        return bool(re.match(pattern, symbol))


@dataclass
class UpdateStockRequest:
    """Request model for updating an existing stock."""

    stock_id: int
    name: str
    industry_group: Optional[str] = field(default=None)
    grade: Optional[str] = field(default=None)
    notes: str = field(default="")

    def validate(self) -> Dict[str, str]:
        """Validate the update request data."""
        errors = {}

        if not self.name or not self.name.strip():
            errors["name"] = "Stock name cannot be empty"
        elif len(self.name.strip()) > 200:
            errors["name"] = "Name cannot exceed 200 characters"

        if self.grade and self.grade.upper() not in ["A", "B", "C"]:
            errors["grade"] = "Grade must be A, B, C, or empty"

        return errors


@dataclass
class StockViewModel:
    """View model for displaying stock information."""

    id: int
    symbol: str
    name: str
    industry_group: Optional[str] = field(default=None)
    grade: Optional[str] = field(default=None)
    notes: str = field(default="")

    @classmethod
    def from_dto(cls, dto: StockDto) -> "StockViewModel":
        """
        Create view model from application DTO.

        Args:
            dto: Stock DTO from application layer

        Returns:
            StockViewModel for presentation
        """
        return cls(
            id=dto.id,
            symbol=dto.symbol,
            name=dto.name,
            industry_group=dto.industry_group,
            grade=dto.grade,
            notes=dto.notes or "",
        )

    @property
    def display_name(self) -> str:
        """Get formatted display name."""
        return f"{self.symbol} - {self.name}"

    @property
    def grade_display(self) -> str:
        """Get formatted grade display."""
        if self.grade:
            return f"Grade {self.grade}"
        return "No Grade"

    @property
    def is_high_grade(self) -> bool:
        """Check if stock has high grade (A)."""
        return self.grade == "A"

    @property
    def has_notes(self) -> bool:
        """Check if stock has notes."""
        return bool(self.notes and self.notes.strip())

    @property
    def notes_preview(self) -> str:
        """Get truncated notes for preview."""
        if not self.has_notes:
            return "No notes"

        if len(self.notes) <= 100:
            return self.notes

        return self.notes[:97] + "..."


class StockListResponse:
    """Response model for stock list operations.

    NOTE: Temporarily implemented as regular class instead of @dataclass
    due to complex field ordering requirements with Optional[List[StockViewModel]].
    TODO: Convert back to @dataclass when Python dataclass field ordering
    with complex generic types is resolved, or use dataclasses with explicit
    field() ordering.
    """

    def __init__(
        self,
        success: bool,
        stocks: List[StockViewModel],
        total_count: int,
        message: str,
        errors: Optional[Dict[str, str]] = None,
        filters_applied: Optional[Dict[str, Any]] = None,
    ):
        self.success = success
        self.stocks = stocks
        self.total_count = total_count
        self.message = message
        self.errors = errors
        self.filters_applied = filters_applied

    @classmethod
    def success(
        cls,
        stocks: List[StockViewModel],
        message: str,
        filters_applied: Optional[Dict[str, Any]] = None,
    ) -> "StockListResponse":
        """Create successful response."""
        return cls(
            success=True,
            stocks=stocks,
            total_count=len(stocks),
            message=message,
            filters_applied=filters_applied,
        )

    @classmethod
    def error(cls, message: str) -> "StockListResponse":
        """Create error response."""
        return cls(success=False, stocks=[], total_count=0, message=message)

    @property
    def has_filters(self) -> bool:
        """Check if any filters are applied."""
        return bool(self.filters_applied)


class StockDetailResponse:
    """Response model for stock detail operations.

    NOTE: Temporarily implemented as regular class instead of @dataclass
    due to complex field ordering requirements with Optional fields.
    TODO: Convert back to @dataclass with proper field() ordering.
    """

    def __init__(
        self,
        success: bool,
        message: str,
        stock: Optional[StockViewModel] = None,
        errors: Optional[Dict[str, str]] = None,
    ):
        self.success = success
        self.message = message
        self.stock = stock
        self.errors = errors

    @classmethod
    def success(cls, stock: StockViewModel, message: str) -> "StockDetailResponse":
        """Create successful response."""
        return cls(success=True, stock=stock, message=message)

    @classmethod
    def error(cls, message: str) -> "StockDetailResponse":
        """Create error response."""
        return cls(success=False, stock=None, message=message)


class CreateStockResponse:
    """Response model for stock creation operations.

    NOTE: Temporarily implemented as regular class instead of @dataclass
    due to complex field ordering requirements with Optional fields.
    TODO: Convert back to @dataclass with proper field() ordering.
    """

    def __init__(
        self,
        success: bool,
        message: str,
        stock_id: Optional[int] = None,
        symbol: Optional[str] = None,
        errors: Optional[Dict[str, str]] = None,
    ):
        self.success = success
        self.message = message
        self.stock_id = stock_id
        self.symbol = symbol
        self.errors = errors

    @classmethod
    def success(cls, stock_id: int, symbol: str, message: str) -> "CreateStockResponse":
        """Create successful response."""
        return cls(success=True, stock_id=stock_id, symbol=symbol, message=message)

    @classmethod
    def error(cls, message: str) -> "CreateStockResponse":
        """Create error response."""
        return cls(success=False, stock_id=None, symbol=None, message=message)


class UpdateStockResponse:
    """Response model for stock update operations.

    NOTE: Temporarily implemented as regular class instead of @dataclass
    due to complex field ordering requirements with Optional fields.
    TODO: Convert back to @dataclass with proper field() ordering.
    """

    def __init__(
        self,
        success: bool,
        message: str,
        stock_id: Optional[int] = None,
        errors: Optional[Dict[str, str]] = None,
    ):
        self.success = success
        self.message = message
        self.stock_id = stock_id
        self.errors = errors

    @classmethod
    def success(cls, stock_id: int, message: str) -> "UpdateStockResponse":
        """Create successful response."""
        return cls(success=True, stock_id=stock_id, message=message)

    @classmethod
    def error(cls, message: str) -> "UpdateStockResponse":
        """Create error response."""
        return cls(success=False, stock_id=None, message=message)


class ValidationErrorResponse:
    """Response model for validation errors.

    NOTE: Temporarily implemented as regular class instead of @dataclass
    due to computed field requirements in __init__.
    TODO: Convert back to @dataclass with __post_init__ when field ordering is resolved.
    """

    def __init__(self, errors: Dict[str, str]):
        self.errors = errors
        self.success = False
        # Set message based on error count
        if len(self.errors) == 1:
            self.message = "Validation failed"
        else:
            self.message = f"Validation failed: {len(self.errors)} validation errors"

    @property
    def error_count(self) -> int:
        """Get number of validation errors."""
        return len(self.errors)

    @property
    def field_errors(self) -> List[str]:
        """Get list of formatted field errors."""
        return [f"{field}: {error}" for field, error in self.errors.items()]


@dataclass
class StockSearchRequest:
    """Request model for stock search and filtering."""

    symbol_filter: Optional[str] = field(default=None)
    name_filter: Optional[str] = field(default=None)
    grade_filter: Optional[str] = field(default=None)
    industry_filter: Optional[str] = field(default=None)

    @property
    def has_filters(self) -> bool:
        """Check if any filters are applied."""
        return any(
            [
                self.symbol_filter,
                self.name_filter,
                self.grade_filter,
                self.industry_filter,
            ]
        )

    @property
    def active_filters(self) -> Dict[str, str]:
        """Get dictionary of active filters."""
        filters = {}

        if self.symbol_filter:
            filters["symbol"] = self.symbol_filter
        if self.name_filter:
            filters["name"] = self.name_filter
        if self.grade_filter:
            filters["grade"] = self.grade_filter
        if self.industry_filter:
            filters["industry"] = self.industry_filter

        return filters

    def validate(self) -> Dict[str, str]:
        """Validate search parameters."""
        errors = {}

        if self.grade_filter and self.grade_filter not in ["A", "B", "C"]:
            errors["grade_filter"] = "Grade must be A, B, or C"

        return errors
