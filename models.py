"""
Pydantic data models for StockBook application
Provides type-safe data models with validation for all entities

FIXME: These legacy Pydantic models duplicate functionality now provided by 
the clean architecture domain entities and value objects. 

TODO: Phase out these models in favor of:
- domain/entities/stock_entity.py for Stock behavior
- domain/value_objects/ for validated value types
- application/dto/ for data transfer between layers
- presentation/view_models/ for UI data binding

TODO: Migrate remaining references in components.py and legacy code to use
the new clean architecture layers instead of these models.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Literal, get_args
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
import re
from config import config


class Stock(BaseModel):
    """Stock model with symbol validation and grade constraints"""
    
    symbol: str = Field(..., min_length=1, max_length=config.stock_symbol_max_length, description="Stock symbol")
    name: str = Field(..., min_length=1, max_length=200, description="Company name")
    industry_group: Optional[str] = Field(None, max_length=100, description="Industry classification")
    grade: Optional[str] = Field(None, description="Stock grade")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    
    @field_validator('grade')
    @classmethod
    def validate_grade(cls, v):
        """Validate stock grade against configured options"""
        if v is not None and v not in config.valid_grades:
            raise ValueError(f'Grade must be one of {config.valid_grades}')
        return v
    
    @field_validator('symbol')
    @classmethod
    def validate_symbol(cls, v):
        """Validate stock symbol format"""
        if not v:
            raise ValueError('Symbol cannot be empty')
        
        # Check if symbol matches configured pattern
        if not re.match(config.stock_symbol_pattern, v):
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
    
    name: str = Field(..., min_length=1, max_length=config.portfolio_name_max_length, description="Portfolio name")
    max_positions: int = Field(config.portfolio_defaults['max_positions'], ge=1, le=100, description="Maximum number of positions")
    max_risk_per_trade: float = Field(config.portfolio_defaults['max_risk_per_trade'], ge=0.1, le=config.max_risk_per_trade_limit, description="Maximum risk percentage per trade")
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
    type: str = Field(..., description="Transaction type")
    quantity: int = Field(..., ge=config.min_quantity, description="Number of shares")
    price: Decimal = Field(..., ge=config.min_price, decimal_places=config.decimal_places, description="Price per share")
    transaction_date: date = Field(..., description="Transaction date")
    notes: Optional[str] = Field(None, max_length=500, description="Transaction notes")
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        """Validate transaction type against configured options"""
        if v not in config.valid_transaction_types:
            raise ValueError(f'Transaction type must be one of {config.valid_transaction_types}')
        return v
    
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