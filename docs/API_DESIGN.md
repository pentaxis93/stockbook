# StockBook API Design

## Overview

This document outlines the planned REST API structure for StockBook. The API will be implemented using FastAPI in Phase 2 of development, following RESTful principles and OpenAPI 3.0 specification.

## Table of Contents
1. [API Principles](#api-principles)
2. [Authentication & Authorization](#authentication--authorization)
3. [Base URL Structure](#base-url-structure)
4. [Common Patterns](#common-patterns)
5. [API Endpoints](#api-endpoints)
6. [Error Handling](#error-handling)
7. [Data Models](#data-models)
8. [Integration Patterns](#integration-patterns)

## API Principles

### Design Philosophy
- **RESTful**: Follow REST architectural constraints
- **Consistent**: Uniform interface across all endpoints
- **Versioned**: API versioning from day one
- **Documented**: Auto-generated OpenAPI documentation
- **Type-Safe**: Leveraging Pydantic for validation

### Standards
- HTTP methods used semantically (GET, POST, PUT, DELETE, PATCH)
- Proper status codes (2xx success, 4xx client error, 5xx server error)
- JSON request/response bodies
- ISO 8601 date formats
- UUID for resource identifiers

## Authentication & Authorization

### Authentication Strategy (Planned)
```
POST /api/v1/auth/login
{
  "username": "user@example.com",
  "password": "secure_password"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Authorization Headers
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

## Base URL Structure

```
https://api.stockbook.com/api/v1/
│
├── /auth/          # Authentication endpoints
├── /stocks/        # Stock management
├── /portfolios/    # Portfolio management
├── /transactions/  # Transaction records
├── /targets/       # Price targets
├── /journal/       # Trading journal
├── /analytics/     # Analytics and reports
└── /health/        # Health check
```

## Common Patterns

### Pagination
```
GET /api/v1/stocks?page=1&size=20&sort=symbol:asc

Response:
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 20,
  "pages": 5
}
```

### Filtering
```
GET /api/v1/stocks?sector=Technology&min_price=100&max_price=500
```

### Sorting
```
GET /api/v1/stocks?sort=symbol:asc,price:desc
```

### Field Selection
```
GET /api/v1/stocks?fields=id,symbol,company_name,current_price
```

## API Endpoints

### Stock Management

#### List Stocks
```
GET /api/v1/stocks
```
Query Parameters:
- `page` (int): Page number (default: 1)
- `size` (int): Items per page (default: 20)
- `sector` (string): Filter by sector
- `search` (string): Search in symbol or company name

Response:
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "symbol": "AAPL",
      "company_name": "Apple Inc.",
      "sector": "Technology",
      "industry": "Consumer Electronics",
      "current_price": 150.25,
      "currency": "USD"
    }
  ],
  "total": 50,
  "page": 1,
  "size": 20
}
```

#### Get Stock Details
```
GET /api/v1/stocks/{stock_id}
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "symbol": "AAPL",
  "company_name": "Apple Inc.",
  "sector": "Technology",
  "industry": "Consumer Electronics",
  "current_price": 150.25,
  "currency": "USD",
  "market_cap": 2500000000000,
  "pe_ratio": 25.5,
  "dividend_yield": 0.5,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

#### Create Stock
```
POST /api/v1/stocks
```

Request:
```json
{
  "symbol": "AAPL",
  "company_name": "Apple Inc.",
  "sector": "Technology",
  "industry": "Consumer Electronics"
}
```

Response: 201 Created
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "symbol": "AAPL",
  "company_name": "Apple Inc.",
  "sector": "Technology",
  "industry": "Consumer Electronics"
}
```

#### Update Stock
```
PUT /api/v1/stocks/{stock_id}
```

Request:
```json
{
  "company_name": "Apple Inc.",
  "sector": "Technology",
  "industry": "Consumer Electronics"
}
```

Response: 200 OK

#### Delete Stock
```
DELETE /api/v1/stocks/{stock_id}
```

Response: 204 No Content

### Portfolio Management

#### List Portfolios
```
GET /api/v1/portfolios
```

Response:
```json
{
  "items": [
    {
      "id": "650e8400-e29b-41d4-a716-446655440000",
      "name": "Growth Portfolio",
      "description": "High growth technology stocks",
      "total_value": 50000.00,
      "currency": "USD",
      "stock_count": 10
    }
  ]
}
```

#### Get Portfolio Details
```
GET /api/v1/portfolios/{portfolio_id}
```

Response:
```json
{
  "id": "650e8400-e29b-41d4-a716-446655440000",
  "name": "Growth Portfolio",
  "description": "High growth technology stocks",
  "holdings": [
    {
      "stock_id": "550e8400-e29b-41d4-a716-446655440000",
      "symbol": "AAPL",
      "quantity": 100,
      "average_price": 140.50,
      "current_price": 150.25,
      "total_value": 15025.00,
      "gain_loss": 975.00,
      "gain_loss_percentage": 6.94
    }
  ],
  "total_value": 50000.00,
  "total_cost": 45000.00,
  "total_gain_loss": 5000.00,
  "total_gain_loss_percentage": 11.11
}
```

#### Portfolio Analytics
```
GET /api/v1/portfolios/{portfolio_id}/analytics
```

Response:
```json
{
  "portfolio_id": "650e8400-e29b-41d4-a716-446655440000",
  "metrics": {
    "total_value": 50000.00,
    "daily_change": 500.00,
    "daily_change_percentage": 1.0,
    "ytd_return": 15.5,
    "volatility": 0.18,
    "sharpe_ratio": 1.2,
    "beta": 1.1
  },
  "allocation": {
    "by_sector": [
      {"sector": "Technology", "percentage": 60.0, "value": 30000.00},
      {"sector": "Healthcare", "percentage": 25.0, "value": 12500.00},
      {"sector": "Finance", "percentage": 15.0, "value": 7500.00}
    ],
    "by_asset": [
      {"symbol": "AAPL", "percentage": 30.0, "value": 15000.00},
      {"symbol": "MSFT", "percentage": 20.0, "value": 10000.00}
    ]
  },
  "risk_metrics": {
    "concentration_risk": "MEDIUM",
    "diversification_score": 0.75,
    "max_drawdown": -0.15
  }
}
```

### Transaction Management

#### Record Transaction
```
POST /api/v1/transactions
```

Request:
```json
{
  "stock_id": "550e8400-e29b-41d4-a716-446655440000",
  "portfolio_id": "650e8400-e29b-41d4-a716-446655440000",
  "type": "BUY",
  "quantity": 10,
  "price": 150.00,
  "transaction_date": "2024-01-15T10:00:00Z",
  "fees": 9.99,
  "notes": "Adding to position on dip"
}
```

Response: 201 Created

#### List Transactions
```
GET /api/v1/transactions?portfolio_id={portfolio_id}&start_date=2024-01-01&end_date=2024-12-31
```

### Price Targets

#### Set Price Target
```
POST /api/v1/targets
```

Request:
```json
{
  "stock_id": "550e8400-e29b-41d4-a716-446655440000",
  "target_price": 200.00,
  "target_date": "2024-12-31",
  "notes": "Based on analyst consensus"
}
```

#### Get Active Targets
```
GET /api/v1/targets?status=ACTIVE
```

### Trading Journal

#### Create Journal Entry
```
POST /api/v1/journal
```

Request:
```json
{
  "stock_id": "550e8400-e29b-41d4-a716-446655440000",
  "content": "Strong earnings report. Revenue beat by 5%. Maintaining position.",
  "sentiment": "BULLISH",
  "tags": ["earnings", "hold"]
}
```

#### Search Journal
```
GET /api/v1/journal?search=earnings&stock_id={stock_id}
```

## Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": [
      {
        "field": "quantity",
        "message": "Must be greater than 0"
      }
    ],
    "request_id": "req_550e8400e29b41d4",
    "timestamp": "2024-01-15T12:00:00Z"
  }
}
```

### Common Error Codes
| Code | HTTP Status | Description |
|------|-------------|-------------|
| VALIDATION_ERROR | 400 | Invalid request data |
| AUTHENTICATION_REQUIRED | 401 | Missing or invalid token |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| CONFLICT | 409 | Resource conflict |
| RATE_LIMITED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Server error |

## Data Models

### Stock Model
```python
class Stock(BaseModel):
    id: UUID
    symbol: str  # Max 10 chars, uppercase
    company_name: str  # Max 100 chars
    sector: str
    industry: str
    current_price: Optional[Decimal]
    currency: str = "USD"
    market_cap: Optional[int]
    pe_ratio: Optional[float]
    dividend_yield: Optional[float]
    created_at: datetime
    updated_at: datetime
```

### Portfolio Model
```python
class Portfolio(BaseModel):
    id: UUID
    name: str  # Max 50 chars
    description: Optional[str]  # Max 200 chars
    currency: str = "USD"
    created_at: datetime
    updated_at: datetime
```

### Transaction Model
```python
class Transaction(BaseModel):
    id: UUID
    stock_id: UUID
    portfolio_id: UUID
    type: Literal["BUY", "SELL"]
    quantity: int  # Must be positive
    price: Decimal  # Per share price
    total_amount: Decimal  # Calculated
    fees: Decimal = Decimal("0")
    transaction_date: datetime
    notes: Optional[str]  # Max 500 chars
    created_at: datetime
```

## Integration Patterns

### Webhook Events (Future)
```json
{
  "event_type": "transaction.created",
  "event_id": "evt_550e8400e29b41d4",
  "timestamp": "2024-01-15T12:00:00Z",
  "data": {
    "transaction_id": "750e8400-e29b-41d4-a716-446655440000",
    "type": "BUY",
    "stock_symbol": "AAPL",
    "quantity": 100,
    "price": 150.00
  }
}
```

### Batch Operations (Future)
```
POST /api/v1/transactions/batch

Request:
{
  "transactions": [
    {...},
    {...}
  ]
}
```

### Export Endpoints (Future)
```
GET /api/v1/portfolios/{portfolio_id}/export?format=csv
GET /api/v1/transactions/export?format=pdf&year=2024
```

## Implementation Notes

### Phase 2 Implementation Order
1. Health check endpoint
2. Stock CRUD operations
3. Portfolio management
4. Transaction recording
5. Basic analytics
6. Authentication system

### Technology Stack
- **FastAPI**: Web framework
- **Pydantic**: Data validation
- **SQLAlchemy**: ORM (when implemented)
- **Alembic**: Database migrations
- **pytest**: API testing
- **OpenAPI**: Auto-documentation

### Performance Considerations
- Response caching for analytics
- Database query optimization
- Pagination for large datasets
- Rate limiting per user
- Async request handling

### Security Measures
- JWT token authentication
- Role-based access control
- Input validation
- SQL injection prevention
- CORS configuration
- HTTPS enforcement