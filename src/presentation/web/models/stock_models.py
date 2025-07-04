"""
Stock models for FastAPI presentation layer.

Provides Pydantic models for request/response validation and serialization
for stock-related API endpoints.
"""

from typing import Any, Literal, Self

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from src.application.commands.stock import (
    CreateStockCommand,
    UpdateStockCommand,
)
from src.application.dto.stock_dto import StockDto


# Constants for validation
MAX_SYMBOL_LENGTH = 5


class StockRequest(BaseModel):
    """
    Request model for creating a stock.

    Validates and normalizes input data from API requests before
    passing to the application layer.
    """

    symbol: str
    name: str | None = None
    sector: str | None = None
    industry_group: str | None = None
    grade: Literal["A", "B", "C", "D", "F"] | str | None = None
    notes: str = ""

    model_config = ConfigDict(
        str_strip_whitespace=True,  # Automatically strip whitespace
        extra="forbid",  # Reject extra fields
    )

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, value: str) -> str:
        """
        Validate and normalize stock symbol.

        Args:
            value: Raw symbol string

        Returns:
            Normalized uppercase symbol

        Raises:
            ValueError: If symbol is invalid
        """
        # Strip and uppercase
        normalized = value.strip().upper()

        # Check not empty
        if not normalized:
            raise ValueError("Symbol cannot be empty")

        # Check format (letters only) - do this first
        if not normalized.isalpha():
            raise ValueError("Stock symbol must contain only uppercase letters")
        # Check length after format
        if len(normalized) < 1 or len(normalized) > MAX_SYMBOL_LENGTH:
            raise ValueError(
                f"Stock symbol must be between 1 and {MAX_SYMBOL_LENGTH} characters"
            )

        return normalized

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        """
        Validate company name.

        Args:
            value: Raw name string or None

        Returns:
            Trimmed name or None
        """
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed if trimmed else None

    @field_validator("sector", "industry_group")
    @classmethod
    def normalize_optional_strings(cls, value: str | None) -> str | None:
        """
        Normalize optional string fields.

        Args:
            value: Optional string value

        Returns:
            Normalized string or None
        """
        if value is None:
            return None

        trimmed = value.strip()
        return trimmed if trimmed else None

    @field_validator("grade", mode="before")
    @classmethod
    def normalize_grade(cls, value: Any) -> Literal["A", "B", "C", "D", "F"] | None:
        """
        Normalize and validate grade.

        Args:
            value: Grade value

        Returns:
            Normalized uppercase grade

        Raises:
            ValueError: If grade is invalid
        """
        if value is None:
            return None
        # Handle string input
        if isinstance(value, str):
            normalized = value.strip().upper()
            # Treat empty string as None
            if not normalized:
                return None
            if normalized in ["A", "B", "C", "D", "F"]:
                return normalized  # type: ignore[return-value]
        # If we get here, it's an invalid grade
        raise ValueError("Grade must be one of A, B, C, D, F or None")

    @model_validator(mode="after")
    def validate_sector_industry_relationship(self) -> Self:
        """
        Validate that industry_group requires sector.

        Returns:
            Self after validation

        Raises:
            ValueError: If industry_group provided without sector
        """
        if self.industry_group is not None and self.sector is None:
            raise ValueError("Sector must be provided when industry_group is specified")
        return self

    def to_command(self) -> CreateStockCommand:
        """
        Convert request to CreateStockCommand.

        Returns:
            CreateStockCommand for application layer
        """
        return CreateStockCommand(
            symbol=self.symbol,
            name=self.name,
            sector=self.sector,
            industry_group=self.industry_group,
            grade=self.grade,
            notes=self.notes,
        )


class StockResponse(BaseModel):
    """
    Response model for stock data.

    Provides consistent API response format for stock information.
    """

    id: str | None
    symbol: str
    name: str | None = None
    sector: str | None = None
    industry_group: str | None = None
    grade: str | None = None
    notes: str = ""

    model_config = ConfigDict(
        frozen=True,  # Make immutable
        from_attributes=True,  # Allow creation from ORM models
        validate_assignment=True,  # Validate on assignment attempts
    )

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, value: str) -> str:
        """
        Validate required symbol field.

        Args:
            value: String value

        Returns:
            Validated string

        Raises:
            ValueError: If string is empty
        """
        if not value or not value.strip():
            raise ValueError("Symbol cannot be empty")
        return value

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        """
        Validate optional name field.

        Args:
            value: String value or None

        Returns:
            Validated string or None
        """
        if value is None:
            return None
        if not value.strip():
            return None
        return value

    @classmethod
    def from_dto(cls, dto: StockDto) -> "StockResponse":
        """
        Create response from StockDto.

        Args:
            dto: Stock DTO from application layer

        Returns:
            StockResponse instance
        """
        return cls(
            id=dto.id,
            symbol=dto.symbol,
            name=dto.name,
            sector=dto.sector,
            industry_group=dto.industry_group,
            grade=dto.grade,
            notes=dto.notes,
        )


class StockListResponse(BaseModel):
    """
    Response model for a list of stocks.

    Provides paginated response format for stock listings.
    """

    stocks: list[StockResponse]
    total: int

    model_config = ConfigDict(
        frozen=True,  # Make immutable
    )

    @classmethod
    def from_dto_list(cls, dtos: list[StockDto]) -> "StockListResponse":
        """
        Create response from list of StockDto objects.

        Args:
            dtos: List of stock DTOs from application layer

        Returns:
            StockListResponse instance
        """
        stocks = [StockResponse.from_dto(dto) for dto in dtos]
        return cls(stocks=stocks, total=len(stocks))


class StockUpdateRequest(BaseModel):
    """
    Request model for updating a stock.

    All fields are optional to support partial updates.
    Validates and normalizes input data from API requests before
    passing to the application layer.
    """

    symbol: str | None = None
    name: str | None = None
    sector: str | None = None
    industry_group: str | None = None
    grade: Literal["A", "B", "C", "D", "F"] | str | None = None
    notes: str = ""

    model_config = ConfigDict(
        str_strip_whitespace=True,  # Automatically strip whitespace
        extra="forbid",  # Reject extra fields
    )

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, value: str | None) -> str | None:
        """
        Validate and normalize stock symbol.

        Args:
            value: Raw symbol string or None

        Returns:
            Normalized uppercase symbol or None

        Raises:
            ValueError: If symbol is invalid
        """
        if value is None:
            return None

        # Strip and uppercase
        normalized = value.strip().upper()

        # Check not empty
        if not normalized:
            return None

        # Check format (letters only) - do this first
        if not normalized.isalpha():
            raise ValueError("Stock symbol must contain only uppercase letters")
        # Check length after format
        if len(normalized) < 1 or len(normalized) > MAX_SYMBOL_LENGTH:
            raise ValueError(
                f"Stock symbol must be between 1 and {MAX_SYMBOL_LENGTH} characters"
            )

        return normalized

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        """
        Validate company name.

        Args:
            value: Raw name string or None

        Returns:
            Trimmed name or None
        """
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed if trimmed else None

    @field_validator("sector", "industry_group")
    @classmethod
    def normalize_optional_strings(cls, value: str | None) -> str | None:
        """
        Normalize optional string fields.

        Args:
            value: Optional string value

        Returns:
            Normalized string or None
        """
        if value is None:
            return None

        trimmed = value.strip()
        return trimmed if trimmed else None

    @field_validator("grade", mode="before")
    @classmethod
    def normalize_grade(cls, value: Any) -> Literal["A", "B", "C", "D", "F"] | None:
        """
        Normalize and validate grade.

        Args:
            value: Grade value

        Returns:
            Normalized uppercase grade

        Raises:
            ValueError: If grade is invalid
        """
        if value is None:
            return None
        # Handle string input
        if isinstance(value, str):
            normalized = value.strip().upper()
            # Treat empty string as None
            if not normalized:
                return None
            if normalized in ["A", "B", "C", "D", "F"]:
                return normalized  # type: ignore[return-value]
        # If we get here, it's an invalid grade
        raise ValueError("Grade must be one of A, B, C, D, F or None")

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, value: str) -> str:
        """
        Validate notes field.

        Args:
            value: Notes string

        Returns:
            Trimmed notes
        """
        return value.strip()

    @model_validator(mode="after")
    def validate_sector_industry_relationship(self) -> Self:
        """
        Validate that industry_group requires sector.

        Returns:
            Self after validation

        Raises:
            ValueError: If industry_group provided without sector
        """
        if self.industry_group is not None and self.sector is None:
            raise ValueError("Sector must be provided when industry_group is specified")
        return self

    def to_command(self, stock_id: str) -> UpdateStockCommand:
        """
        Convert request to UpdateStockCommand.

        Args:
            stock_id: ID of the stock to update

        Returns:
            UpdateStockCommand for application layer
        """
        return UpdateStockCommand(
            stock_id=stock_id,
            symbol=self.symbol,
            name=self.name,
            sector=self.sector,
            industry_group=self.industry_group,
            grade=self.grade,
            notes=self.notes,
        )
