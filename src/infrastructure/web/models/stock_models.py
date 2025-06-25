"""
Pydantic models for stock-related web API requests and responses.

These models handle validation, serialization, and documentation
for the FastAPI endpoints.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

if TYPE_CHECKING:
    pass


class StockRequest(BaseModel):
    """Request model for creating or updating a stock."""

    symbol: str = Field(..., description="Stock trading symbol")
    name: str = Field(..., description="Company name")
    sector: Optional[str] = Field(None, description="Business sector")
    industry_group: Optional[str] = Field(
        None, description="Industry group classification"
    )
    grade: Optional[str] = Field(None, description="Investment grade (A, B, C)")
    notes: Optional[str] = Field(None, description="Additional notes about the stock")

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        """Validate and transform stock symbol."""
        if not v or not v.strip():
            raise ValueError("Stock symbol cannot be empty")

        # Convert to uppercase
        symbol = v.strip().upper()

        # Validate format: 1-5 uppercase letters
        if not re.match(r"^[A-Z]{1,5}$", symbol):
            raise ValueError("Invalid stock symbol format. Use 1-5 uppercase letters.")

        return symbol

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate company name."""
        if not v or not v.strip():
            raise ValueError("Stock name cannot be empty")

        name = v.strip()
        if len(name) > 200:
            raise ValueError("Name cannot exceed 200 characters")

        return name

    @field_validator("grade")
    @classmethod
    def validate_grade(cls, v: Optional[str]) -> Optional[str]:
        """Validate investment grade."""
        if v is None or v == "":
            return None

        grade = v.strip().upper()
        if grade not in ["A", "B", "C"]:
            raise ValueError("Grade must be A, B, C, or empty")

        return grade

    @field_validator("sector")
    @classmethod
    def validate_sector(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize sector."""
        if v is None or v == "":
            return None
        return v.strip()

    @field_validator("industry_group")
    @classmethod
    def validate_industry_group(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize industry group."""
        if v is None or v == "":
            return None
        return v.strip()

    @field_validator("notes")
    @classmethod
    def validate_notes(cls, v: str | None) -> str:
        """Validate and normalize notes."""
        if v is None:
            return ""
        return v.strip()


class StockResponse(BaseModel):
    """Response model for stock data."""

    id: str = Field(..., description="Unique stock identifier")
    symbol: str = Field(..., description="Stock trading symbol")
    name: str = Field(..., description="Company name")
    sector: Optional[str] = Field(None, description="Business sector")
    industry_group: Optional[str] = Field(
        None, description="Industry group classification"
    )
    grade: Optional[str] = Field(None, description="Investment grade (A, B, C)")
    notes: str = Field("", description="Additional notes about the stock")

    model_config = {"from_attributes": True}


class StockListResponse(BaseModel):
    """Response model for a list of stocks."""

    stocks: List[StockResponse] = Field(default=[], description="List of stocks")
    total: int = Field(..., description="Total number of stocks")

    model_config = {"from_attributes": True}


class ErrorResponse(BaseModel):
    """Response model for API errors."""

    message: str = Field(..., description="Error message")
    code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details"
    )

    model_config = {"from_attributes": True}
