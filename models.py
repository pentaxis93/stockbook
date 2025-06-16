"""
Pydantic data models for StockBook application
Provides type-safe data models with validation for all entities
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
import re


class Stock(BaseModel):
    """Stock model with symbol validation and grade constraints"""
    
    symbol: str = Field(..., min_length=1, max_length=5, description="Stock symbol (1-5 uppercase letters)")
    name: str = Field(..., min_length=1, max_length=200, description="Company name")
    industry_group: Optional[str] = Field(None, max_length=100, description="Industry classification")
    grade: Optional[Literal["A", "B", "C"]] = Field(None, description="Stock grade (A/B/C)")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    
    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v):
        """Validate stock symbol format"""
        if not v:
            raise ValueError('Symbol cannot be empty')
        
        # Check if symbol contains only uppercase letters
        if not re.match(r'^[A-Z]{1,5}$', v):
            raise ValueError('Symbol must be 1-5 uppercase letters only')
        
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate company name"""
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "industry_group": "Technology",
                "grade": "A",
                "notes": "Strong fundamentals"
            }
        }
    )


class Portfolio(BaseModel):
    """Portfolio model with name validation and risk percentage limits"""
    
    name: str = Field(..., min_length=1, max_length=100, description="Portfolio name")
    max_positions: int = Field(10, ge=1, le=100, description="Maximum number of positions")
    max_risk_per_trade: float = Field(2.0, ge=0.1, le=25.0, description="Maximum risk percentage per trade")
    is_active: bool = Field(True, description="Whether portfolio is active")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate portfolio name"""
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Growth Portfolio",
                "max_positions": 15,
                "max_risk_per_trade": 1.5,
                "is_active": True
            }
        }
    )


class Transaction(BaseModel):
    """Transaction model with price/quantity validation and date handling"""
    
    portfolio_id: int = Field(..., ge=1, description="Portfolio ID")
    stock_id: int = Field(..., ge=1, description="Stock ID")
    type: Literal["buy", "sell"] = Field(..., description="Transaction type")
    quantity: int = Field(..., ge=1, description="Number of shares")
    price: Decimal = Field(..., gt=0, decimal_places=2, description="Price per share")
    transaction_date: date = Field(..., description="Transaction date")
    notes: Optional[str] = Field(None, max_length=500, description="Transaction notes")
    
    @field_validator('transaction_date')
    @classmethod
    def validate_transaction_date(cls, v):
        """Validate transaction date is not in the future"""
        if v > date.today():
            raise ValueError('Transaction date cannot be in the future')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "portfolio_id": 1,
                "stock_id": 1,
                "type": "buy",
                "quantity": 100,
                "price": "150.25",
                "transaction_date": "2024-01-15",
                "notes": "Initial purchase"
            }
        }
    )


class Target(BaseModel):
    """Target model with price relationship validation"""
    
    stock_id: int = Field(..., ge=1, description="Stock ID")
    portfolio_id: int = Field(..., ge=1, description="Portfolio ID")
    pivot_price: Decimal = Field(..., gt=0, decimal_places=2, description="Pivot/breakout price")
    failure_price: Decimal = Field(..., gt=0, decimal_places=2, description="Failure/stop price")
    notes: Optional[str] = Field(None, max_length=500, description="Target notes")
    status: Literal["active", "hit", "failed", "cancelled"] = Field("active", description="Target status")
    
    @model_validator(mode='after')
    def validate_price_relationship(self):
        """Validate that pivot price is greater than failure price"""
        if self.pivot_price and self.failure_price:
            if self.pivot_price <= self.failure_price:
                raise ValueError('Pivot price must be greater than failure price')
        
        return self
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "stock_id": 1,
                "portfolio_id": 1,
                "pivot_price": "175.00",
                "failure_price": "140.00",
                "notes": "Breakout target above resistance",
                "status": "active"
            }
        }
    )


class PortfolioBalance(BaseModel):
    """Portfolio balance model with balance validation and date constraints"""
    
    portfolio_id: int = Field(..., ge=1, description="Portfolio ID")
    balance_date: date = Field(..., description="Balance date")
    withdrawals: Decimal = Field(Decimal("0.00"), ge=0, decimal_places=2, description="Withdrawals amount")
    deposits: Decimal = Field(Decimal("0.00"), ge=0, decimal_places=2, description="Deposits amount")
    final_balance: Decimal = Field(..., decimal_places=2, description="Final balance")
    index_change: Optional[Decimal] = Field(None, decimal_places=2, description="Benchmark index change %")
    
    @field_validator('balance_date')
    @classmethod
    def validate_balance_date(cls, v):
        """Validate balance date is not in the future"""
        if v > date.today():
            raise ValueError('Balance date cannot be in the future')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "portfolio_id": 1,
                "balance_date": "2024-01-31",
                "withdrawals": "500.00",
                "deposits": "1000.00",
                "final_balance": "15000.00",
                "index_change": "2.5"
            }
        }
    )


class JournalEntry(BaseModel):
    """Journal entry model with content validation"""
    
    entry_date: date = Field(..., description="Entry date")
    content: str = Field(..., min_length=1, max_length=10000, description="Journal entry content")
    stock_id: Optional[int] = Field(None, ge=1, description="Related stock ID")
    portfolio_id: Optional[int] = Field(None, ge=1, description="Related portfolio ID")
    transaction_id: Optional[int] = Field(None, ge=1, description="Related transaction ID")
    
    @field_validator('entry_date')
    @classmethod
    def validate_entry_date(cls, v):
        """Validate entry date is not in the future"""
        if v > date.today():
            raise ValueError('Entry date cannot be in the future')
        return v
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        """Validate content is not empty or whitespace only"""
        if not v or not v.strip():
            raise ValueError('Content cannot be empty or whitespace only')
        return v.strip()
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "entry_date": "2024-01-15",
                "content": "Bought AAPL at support level. Good risk/reward setup.",
                "stock_id": 1,
                "portfolio_id": 1,
                "transaction_id": 1
            }
        }
    )