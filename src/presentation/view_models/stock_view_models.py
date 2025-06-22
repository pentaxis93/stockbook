"""
Stock view models for presentation layer.

Provides data transfer objects and view models for stock-related UI operations,
handling validation, transformation, and display logic.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.application.commands.stock_commands import (
    CreateStockCommand,
    UpdateStockCommand,
)
from src.application.dto.stock_dto import StockDto


@dataclass
class CreateStockRequest:
    """Request model for creating a new stock."""

    symbol: str
    name: str
    sector: Optional[str] = field(default=None)
    industry_group: Optional[str] = field(default=None)
    grade: Optional[str] = field(default=None)
    notes: str = field(default="")

    def validate(self) -> Dict[str, str]:
        """
        Validate the request data.

        Returns:
            Dictionary of field errors, empty if valid
        """
        errors: Dict[str, str] = {}

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
            sector=self.sector.strip() if self.sector else None,
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
            sector=sanitized.sector,
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

    stock_id: str
    name: Optional[str] = field(default=None)
    sector: Optional[str] = field(default=None)
    industry_group: Optional[str] = field(default=None)
    grade: Optional[str] = field(default=None)
    notes: Optional[str] = field(default=None)

    def validate(self) -> Dict[str, str]:
        """Validate the update request data."""
        errors: Dict[str, str] = {}

        # Validate stock_id
        if not self.stock_id.strip():
            errors["stock_id"] = "Stock ID must be a non-empty string"

        # Only validate name if it's being updated
        if self.name is not None:
            if not self.name or not self.name.strip():
                errors["name"] = "Stock name cannot be empty"
            elif len(self.name.strip()) > 200:
                errors["name"] = "Name cannot exceed 200 characters"

        # Only validate grade if it's being updated
        if self.grade is not None and self.grade.upper() not in ["A", "B", "C"]:
            errors["grade"] = "Grade must be A, B, or C"

        # Validate industry group length if being updated
        if self.industry_group is not None and len(self.industry_group) > 100:
            errors["industry_group"] = "Industry group cannot exceed 100 characters"

        # Validate notes length if being updated
        if self.notes is not None and len(self.notes) > 1000:
            errors["notes"] = "Notes cannot exceed 1000 characters"

        return errors

    def sanitize(self) -> "UpdateStockRequest":
        """Sanitize input data."""
        return UpdateStockRequest(
            stock_id=self.stock_id,
            name=self.name.strip().title() if self.name else None,
            sector=self.sector.strip() if self.sector else None,
            industry_group=self.industry_group.strip() if self.industry_group else None,
            grade=self.grade.upper() if self.grade else None,
            notes=self.notes.strip() if self.notes else None,
        )

    def to_command(self) -> UpdateStockCommand:
        """Convert to application command."""
        return UpdateStockCommand(
            stock_id=self.stock_id,
            name=self.name,
            sector=self.sector,
            industry_group=self.industry_group,
            grade=self.grade,
            notes=self.notes,
        )

    def has_updates(self) -> bool:
        """Check if any fields are being updated."""
        return any(
            [
                self.name is not None,
                self.sector is not None,
                self.industry_group is not None,
                self.grade is not None,
                self.notes is not None,
            ]
        )


@dataclass
class StockViewModel:
    """View model for displaying stock information."""

    id: str
    symbol: str
    name: str
    sector: Optional[str] = field(default=None)
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
        if dto.id is None:
            raise ValueError("Cannot create view model from DTO without ID")

        return cls(
            id=dto.id,
            symbol=dto.symbol,
            name=dto.name,
            sector=dto.sector,
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


@dataclass
class StockListResponse:
    """Response model for stock list operations."""

    success: bool
    stocks: List[StockViewModel]
    total_count: int
    message: str
    errors: Optional[Dict[str, str]] = field(default=None)
    filters_applied: Optional[Dict[str, Any]] = field(default=None)

    @classmethod
    def create_success(
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
    def create_error(cls, message: str) -> "StockListResponse":
        """Create error response."""
        return cls(success=False, stocks=[], total_count=0, message=message)

    @property
    def has_filters(self) -> bool:
        """Check if any filters are applied."""
        return bool(self.filters_applied)


@dataclass
class StockDetailResponse:
    """Response model for stock detail operations."""

    success: bool
    message: str
    stock: Optional[StockViewModel] = field(default=None)
    errors: Optional[Dict[str, str]] = field(default=None)

    @classmethod
    def create_success(
        cls, stock: StockViewModel, message: str
    ) -> "StockDetailResponse":
        """Create successful response."""
        return cls(success=True, stock=stock, message=message)

    @classmethod
    def create_error(cls, message: str) -> "StockDetailResponse":
        """Create error response."""
        return cls(success=False, stock=None, message=message)


@dataclass
class CreateStockResponse:
    """Response model for stock creation operations."""

    success: bool
    message: str
    stock_id: Optional[str] = field(default=None)
    symbol: Optional[str] = field(default=None)
    errors: Optional[Dict[str, str]] = field(default=None)

    @classmethod
    def create_success(
        cls, stock_id: str, symbol: str, message: str
    ) -> "CreateStockResponse":
        """Create successful response."""
        return cls(success=True, stock_id=stock_id, symbol=symbol, message=message)

    @classmethod
    def create_error(cls, message: str) -> "CreateStockResponse":
        """Create error response."""
        return cls(success=False, stock_id=None, symbol=None, message=message)


@dataclass
class UpdateStockResponse:
    """Response model for stock update operations."""

    success: bool
    message: str
    stock_id: Optional[str] = field(default=None)
    errors: Optional[Dict[str, str]] = field(default=None)

    @classmethod
    def create_success(cls, stock_id: str, message: str) -> "UpdateStockResponse":
        """Create successful response."""
        return cls(success=True, stock_id=stock_id, message=message)

    @classmethod
    def create_error(cls, message: str) -> "UpdateStockResponse":
        """Create error response."""
        return cls(success=False, stock_id=None, message=message)


@dataclass
class ValidationErrorResponse:
    """Response model for validation errors."""

    errors: Dict[str, str]
    success: bool = field(default=False, init=False)
    message: str = field(init=False)

    def __post_init__(self):
        """Set computed fields after initialization."""
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
        filters: Dict[str, str] = {}

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
        errors: Dict[str, str] = {}

        if self.grade_filter and self.grade_filter not in ["A", "B", "C"]:
            errors["grade_filter"] = "Grade must be A, B, or C"

        return errors
