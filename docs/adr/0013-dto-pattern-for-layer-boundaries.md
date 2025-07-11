# Use DTO Pattern for Layer Boundaries

* Status: accepted
* Deciders: Development team
* Date: 2025-01-11

## Context and Problem Statement

StockBook's Clean Architecture requires clear boundaries between layers, but we need to pass data across these boundaries. Domain entities contain business logic and should not be exposed directly to outer layers. The presentation layer needs specific data shapes for API responses, while the application layer needs to return data from use cases. How should we transfer data between architectural layers while maintaining proper encapsulation and layer independence?

## Decision Drivers

* **Layer Independence**: Each layer should not depend on the internal structure of other layers
* **Domain Protection**: Domain entities should not leak outside the application layer
* **API Stability**: Changes to domain models should not break API contracts
* **Performance**: Avoid exposing unnecessary data or causing N+1 queries
* **Type Safety**: Maintain strong typing across layer boundaries
* **Serialization**: Need clean serialization for API responses
* **Documentation**: DTOs should be self-documenting for API consumers

## Considered Options

* **DTO Pattern**: Dedicated Data Transfer Objects for each layer boundary
* **Direct Entity Exposure**: Pass domain entities between layers
* **Dictionary/Map Approach**: Use generic dictionaries for data transfer
* **View Models**: Presentation-specific models only
* **Anemic Domain Objects**: Use domain objects without behavior
* **GraphQL/Query Objects**: Let clients specify what data they need

## Decision Outcome

Chosen option: "DTO Pattern", because it provides the clearest separation between layers while maintaining type safety and allowing each layer to evolve independently. DTOs act as contracts between layers, ensuring that changes in one layer don't ripple through the entire system.

### Positive Consequences

* **Clear Contracts**: DTOs define explicit contracts between layers
* **Domain Encapsulation**: Business logic stays hidden in domain layer
* **API Evolution**: Can version DTOs independently of domain models
* **Performance Control**: Include only necessary data in DTOs
* **Type Safety**: Full typing support with IDE assistance
* **Documentation**: DTOs serve as API documentation
* **Testing**: Easy to test DTO mappings and validate data

### Negative Consequences

* **Mapping Overhead**: Need to map between entities and DTOs
* **Potential Duplication**: Similar fields across entity and DTO
* **More Classes**: Additional classes to maintain
* **Maintenance**: Need to update DTOs when requirements change

## Pros and Cons of the Options

### DTO Pattern

Dedicated objects for transferring data between layers.

* Good, because enforces layer boundaries
* Good, because allows independent evolution
* Good, because explicit data contracts
* Good, because can optimize for specific use cases
* Good, because supports API versioning
* Good, because clear serialization boundary
* Bad, because requires mapping code
* Bad, because potential field duplication

### Direct Entity Exposure

Pass domain entities directly through layers.

* Good, because no mapping needed
* Good, because single source of truth
* Bad, because breaks encapsulation
* Bad, because couples layers together
* Bad, because exposes business logic
* Bad, because serialization issues
* Bad, because can't optimize for views
* Bad, because API changes with domain

### Dictionary/Map Approach

Use generic dictionaries or maps for data transfer.

* Good, because very flexible
* Good, because no class proliferation
* Bad, because no type safety
* Bad, because no IDE support
* Bad, because runtime errors
* Bad, because poor documentation
* Bad, because easy to miss fields

### View Models

Only use models for presentation layer.

* Good, because presentation-focused
* Good, because fewer classes than full DTO
* Bad, because application layer exposed
* Bad, because domain might leak
* Bad, because incomplete solution
* Bad, because mixed patterns

### Anemic Domain Objects

Domain objects without behavior for transfer.

* Good, because reuses domain structure
* Good, because familiar pattern
* Bad, because confuses domain model
* Bad, because anti-pattern in DDD
* Bad, because loses rich domain benefits
* Bad, because mixed responsibilities

### GraphQL/Query Objects

Let clients specify their data needs.

* Good, because flexible queries
* Good, because reduces over-fetching
* Good, because single endpoint
* Bad, because complex implementation
* Bad, because performance concerns
* Bad, because steep learning curve
* Bad, because overkill for REST APIs

## Implementation Details

Our DTO pattern implementation:

### Base DTO Classes

```python
# src/application/dtos/base.py
from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import TypeVar, Type
from uuid import UUID

T = TypeVar('T')

@dataclass(frozen=True)
class DTO(ABC):
    """Base class for all DTOs."""
    
    @classmethod
    def from_domain(cls: Type[T], domain_object: Any) -> T:
        """Create DTO from domain object."""
        raise NotImplementedError
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return asdict(self)
```

### Application Layer DTOs

```python
# src/application/dtos/stock_dto.py
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

@dataclass(frozen=True)
class StockDTO(DTO):
    """DTO for stock data transfer."""
    
    id: UUID
    symbol: str
    company_name: str
    sector: str
    industry: str
    current_price: Optional[Decimal]
    created_at: datetime
    updated_at: Optional[datetime]
    
    @classmethod
    def from_domain(cls, stock: Stock) -> 'StockDTO':
        """Create DTO from stock entity."""
        return cls(
            id=stock.id,
            symbol=stock.symbol.value,
            company_name=stock.company.value,
            sector=stock.sector.value,
            industry=stock.industry.value,
            current_price=stock.current_price.amount if stock.current_price else None,
            created_at=stock.created_at,
            updated_at=stock.updated_at
        )

@dataclass(frozen=True)
class TransactionDTO(DTO):
    """DTO for transaction data transfer."""
    
    id: UUID
    portfolio_id: UUID
    stock_id: UUID
    stock_symbol: str
    transaction_type: str
    quantity: int
    price: Decimal
    total_amount: Decimal
    transaction_date: datetime
    
    @classmethod
    def from_domain(cls, transaction: Transaction, stock: Stock) -> 'TransactionDTO':
        """Create DTO from transaction entity with stock info."""
        return cls(
            id=transaction.id,
            portfolio_id=transaction.portfolio_id,
            stock_id=transaction.stock_id,
            stock_symbol=stock.symbol.value,
            transaction_type=transaction.transaction_type,
            quantity=transaction.quantity,
            price=transaction.price.amount,
            total_amount=transaction.calculate_total().amount,
            transaction_date=transaction.transaction_date
        )
```

### Presentation Layer DTOs

```python
# src/presentation/api/dtos/requests.py
from pydantic import BaseModel, Field, validator

class CreateStockRequest(BaseModel):
    """API request for creating a stock."""
    
    symbol: str = Field(..., min_length=1, max_length=10)
    company_name: str = Field(..., min_length=1, max_length=255)
    sector: str
    industry: str
    
    @validator('symbol')
    def symbol_uppercase(cls, v):
        return v.upper()
    
    class Config:
        schema_extra = {
            "example": {
                "symbol": "AAPL",
                "company_name": "Apple Inc.",
                "sector": "Technology",
                "industry": "Consumer Electronics"
            }
        }

# src/presentation/api/dtos/responses.py
class StockResponse(BaseModel):
    """API response for stock data."""
    
    id: str
    symbol: str
    company_name: str
    sector: str
    industry: str
    current_price: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]
    
    @classmethod
    def from_dto(cls, dto: StockDTO) -> 'StockResponse':
        """Create response from application DTO."""
        return cls(
            id=str(dto.id),
            symbol=dto.symbol,
            company_name=dto.company_name,
            sector=dto.sector,
            industry=dto.industry,
            current_price=float(dto.current_price) if dto.current_price else None,
            created_at=dto.created_at,
            updated_at=dto.updated_at
        )
```

### Complex DTO with Nested Data

```python
@dataclass(frozen=True)
class PortfolioDetailDTO(DTO):
    """DTO for detailed portfolio information."""
    
    id: UUID
    name: str
    description: Optional[str]
    total_value: Decimal
    total_cost: Decimal
    total_return: Decimal
    return_percentage: Decimal
    positions: List['PositionDTO']
    created_at: datetime
    
    @classmethod
    def from_domain(
        cls, 
        portfolio: Portfolio,
        positions: List[Position],
        current_prices: Dict[UUID, Money]
    ) -> 'PortfolioDetailDTO':
        """Create detailed DTO with calculated values."""
        position_dtos = [
            PositionDTO.from_domain(pos, current_prices.get(pos.stock_id))
            for pos in positions
        ]
        
        total_value = sum(pos.current_value for pos in position_dtos)
        total_cost = sum(pos.cost_basis for pos in position_dtos)
        total_return = total_value - total_cost
        return_percentage = (total_return / total_cost * 100) if total_cost > 0 else Decimal("0")
        
        return cls(
            id=portfolio.id,
            name=portfolio.name.value,
            description=portfolio.description,
            total_value=total_value,
            total_cost=total_cost,
            total_return=total_return,
            return_percentage=return_percentage,
            positions=position_dtos,
            created_at=portfolio.created_at
        )
```

### DTO Mappers

```python
# src/application/mappers/dto_mapper.py
class DTOMapper:
    """Centralized DTO mapping logic."""
    
    def __init__(self):
        self._mappers = {}
    
    def register_mapper(self, source_type: Type, target_type: Type, mapper_func):
        """Register a mapping function."""
        key = (source_type, target_type)
        self._mappers[key] = mapper_func
    
    def map(self, source: Any, target_type: Type[T]) -> T:
        """Map source object to target DTO type."""
        key = (type(source), target_type)
        mapper = self._mappers.get(key)
        
        if not mapper:
            # Try to use class method
            if hasattr(target_type, 'from_domain'):
                return target_type.from_domain(source)
            raise ValueError(f"No mapper for {type(source)} to {target_type}")
        
        return mapper(source)
```

### Usage in Application Service

```python
class StockApplicationService:
    """Application service returning DTOs."""
    
    async def get_stock(self, stock_id: UUID) -> StockDTO:
        """Get stock by ID."""
        async with self._uow:
            repo = self._uow.repository(IStockRepository)
            stock = await repo.find_by_id(stock_id)
            
            if not stock:
                raise StockNotFoundError(stock_id)
            
            return StockDTO.from_domain(stock)
    
    async def list_stocks(self, sector: Optional[str] = None) -> List[StockDTO]:
        """List stocks with optional filtering."""
        async with self._uow:
            repo = self._uow.repository(IStockRepository)
            
            if sector:
                stocks = await repo.find_by_sector(Sector(sector))
            else:
                stocks = await repo.find_all()
            
            return [StockDTO.from_domain(stock) for stock in stocks]
```

### Testing DTOs

```python
def test_stock_dto_from_domain():
    """Test DTO creation from domain entity."""
    # Arrange
    stock = Stock(
        symbol=StockSymbol("AAPL"),
        company=CompanyName("Apple Inc."),
        sector=Sector("Technology"),
        industry=Industry("Consumer Electronics", Sector("Technology"))
    )
    
    # Act
    dto = StockDTO.from_domain(stock)
    
    # Assert
    assert dto.symbol == "AAPL"
    assert dto.company_name == "Apple Inc."
    assert dto.sector == "Technology"
    assert dto.industry == "Consumer Electronics"

def test_dto_serialization():
    """Test DTO serialization to dict."""
    # Arrange
    dto = StockDTO(
        id=uuid4(),
        symbol="AAPL",
        company_name="Apple Inc.",
        sector="Technology",
        industry="Consumer Electronics",
        current_price=Decimal("150.00"),
        created_at=datetime.utcnow(),
        updated_at=None
    )
    
    # Act
    data = dto.to_dict()
    
    # Assert
    assert data["symbol"] == "AAPL"
    assert isinstance(data["id"], str)
    assert isinstance(data["current_price"], str)
```

## Links

* Implements [ADR-0002: Use Clean Architecture](0002-use-clean-architecture.md)
* Supports [ADR-0003: Implement Domain-Driven Design](0003-implement-domain-driven-design.md)
* Works with [ADR-0012: Command Pattern](0012-command-pattern-for-application-layer.md)
* References: "Patterns of Enterprise Application Architecture" by Martin Fowler
* References: "Clean Architecture" by Robert C. Martin