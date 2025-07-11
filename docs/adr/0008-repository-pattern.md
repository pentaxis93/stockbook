# Use Repository Pattern for Data Access

* Status: accepted
* Deciders: Development team
* Date: 2025-01-11

## Context and Problem Statement

StockBook needs to persist and retrieve domain entities while maintaining a clean separation between business logic and data access concerns. Our Clean Architecture mandates that the domain layer should not depend on infrastructure details like databases or ORMs. We need a pattern that provides an abstraction over data persistence, enables easy testing through mocking, and allows us to change persistence mechanisms without affecting business logic. How should we structure our data access layer to achieve these goals?

## Decision Drivers

* **Domain Isolation**: Domain layer must not know about persistence details
* **Testability**: Need to test business logic without a database
* **Flexibility**: Ability to change database or ORM without affecting domain
* **Type Safety**: Maintain type safety across persistence boundaries
* **Performance**: Efficient queries without sacrificing abstraction
* **Consistency**: Uniform interface for all entity persistence
* **Transaction Support**: Handle complex operations atomically

## Considered Options

* **Repository Pattern**: Abstract interfaces in domain, concrete implementations in infrastructure
* **Active Record**: Entities know how to persist themselves
* **Data Mapper**: Separate mapping layer between domain and persistence
* **DAO Pattern**: Data Access Objects for each entity
* **Direct ORM Usage**: Use SQLAlchemy models directly in domain
* **CQRS with Separate Models**: Different models for reads and writes

## Decision Outcome

Chosen option: "Repository Pattern", because it provides the cleanest separation between domain and infrastructure while maintaining flexibility and testability. The pattern allows us to define repository interfaces in the domain layer and implement them in the infrastructure layer, perfectly aligning with our Clean Architecture principles and dependency inversion.

### Positive Consequences

* **Clean Separation**: Domain remains pure with no infrastructure dependencies
* **Easy Testing**: Mock repositories for unit tests
* **Flexibility**: Can change database or ORM without touching domain
* **Explicit Contracts**: Repository interfaces define clear boundaries
* **Type Safety**: Full typing from domain to persistence
* **Encapsulation**: Complex queries hidden behind simple methods
* **Consistency**: All entities accessed through similar interfaces

### Negative Consequences

* **More Code**: Need both interfaces and implementations
* **Potential Duplication**: Some mapping between domain and persistence models
* **Performance Concerns**: Abstraction might hide inefficient queries
* **Learning Curve**: Developers must understand the pattern

## Pros and Cons of the Options

### Repository Pattern

Define interfaces in domain layer, implement in infrastructure layer.

* Good, because perfect separation of concerns
* Good, because enables dependency inversion
* Good, because easy to mock for testing
* Good, because can optimize queries per repository
* Good, because supports Unit of Work pattern
* Bad, because requires interface and implementation
* Bad, because might lead to anemic repositories

### Active Record

Domain entities contain methods to save/load themselves.

* Good, because simple and intuitive
* Good, because less code to write
* Bad, because couples domain to persistence
* Bad, because violates single responsibility
* Bad, because hard to test without database
* Bad, because breaks Clean Architecture
* Bad, because limits persistence flexibility

### Data Mapper

Separate mapper classes handle domain-to-persistence conversion.

* Good, because complete separation of concerns
* Good, because flexible mapping strategies
* Good, because domain stays pure
* Bad, because additional complexity
* Bad, because more classes to maintain
* Bad, because potential performance overhead
* Bad, because verbose for simple cases

### DAO Pattern

Data Access Objects encapsulate all database access.

* Good, because centralizes data access logic
* Good, because familiar pattern
* Bad, because often becomes procedural
* Bad, because tends to expose SQL concerns
* Bad, because less domain-focused
* Bad, because often violates DRY

### Direct ORM Usage

Use SQLAlchemy models directly as domain entities.

* Good, because minimal code
* Good, because ORM features available
* Bad, because couples domain to ORM
* Bad, because domain polluted with persistence concerns
* Bad, because hard to test
* Bad, because violates Clean Architecture
* Bad, because ORM limitations affect domain design

### CQRS with Separate Models

Different models and repositories for commands and queries.

* Good, because optimized for different use cases
* Good, because scalable architecture
* Good, because clear command/query separation
* Bad, because significantly more complex
* Bad, because overkill for current needs
* Bad, because requires event sourcing for consistency

## Implementation Details

Our repository pattern implementation includes:

### Domain Layer Interfaces

```python
# src/domain/repositories/i_stock_repository.py
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from src.domain.entities.stock import Stock
from src.domain.value_objects import StockSymbol

class IStockRepository(ABC):
    """Repository interface for Stock aggregate persistence."""
    
    @abstractmethod
    async def find_by_id(self, stock_id: UUID) -> Optional[Stock]:
        """Find a stock by its unique identifier."""
        pass
    
    @abstractmethod
    async def find_by_symbol(self, symbol: StockSymbol) -> Optional[Stock]:
        """Find a stock by its symbol."""
        pass
    
    @abstractmethod
    async def find_all(self) -> List[Stock]:
        """Retrieve all stocks."""
        pass
    
    @abstractmethod
    async def save(self, stock: Stock) -> None:
        """Persist a stock entity."""
        pass
    
    @abstractmethod
    async def delete(self, stock_id: UUID) -> None:
        """Remove a stock from persistence."""
        pass
    
    @abstractmethod
    async def exists_with_symbol(self, symbol: StockSymbol) -> bool:
        """Check if a stock with the given symbol exists."""
        pass
```

### Infrastructure Implementation

```python
# src/infrastructure/repositories/stock_repository.py
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.stock import Stock
from src.domain.repositories import IStockRepository
from src.domain.value_objects import StockSymbol
from src.infrastructure.database.tables import stocks_table
from src.infrastructure.mappers import StockMapper

class StockRepository(IStockRepository):
    """SQLAlchemy implementation of stock repository."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
        self._mapper = StockMapper()
    
    async def find_by_id(self, stock_id: UUID) -> Optional[Stock]:
        query = select(stocks_table).where(stocks_table.c.id == str(stock_id))
        result = await self._session.execute(query)
        row = result.first()
        
        if row is None:
            return None
            
        return self._mapper.to_domain(row)
    
    async def find_by_symbol(self, symbol: StockSymbol) -> Optional[Stock]:
        query = select(stocks_table).where(stocks_table.c.symbol == symbol.value)
        result = await self._session.execute(query)
        row = result.first()
        
        if row is None:
            return None
            
        return self._mapper.to_domain(row)
    
    async def save(self, stock: Stock) -> None:
        data = self._mapper.to_persistence(stock)
        
        # Upsert pattern for save
        existing = await self.find_by_id(stock.id)
        if existing:
            query = (
                stocks_table.update()
                .where(stocks_table.c.id == str(stock.id))
                .values(**data)
            )
        else:
            query = stocks_table.insert().values(**data)
        
        await self._session.execute(query)
    
    async def exists_with_symbol(self, symbol: StockSymbol) -> bool:
        query = select(stocks_table.c.id).where(
            stocks_table.c.symbol == symbol.value
        )
        result = await self._session.execute(query)
        return result.first() is not None
```

### Domain-to-Persistence Mapping

```python
# src/infrastructure/mappers/stock_mapper.py
from typing import Dict, Any
from datetime import datetime
from uuid import UUID

from src.domain.entities.stock import Stock
from src.domain.value_objects import (
    StockSymbol, CompanyName, Sector, Industry
)

class StockMapper:
    """Maps between domain entities and persistence models."""
    
    def to_domain(self, row: Any) -> Stock:
        """Convert database row to domain entity."""
        return Stock(
            id=UUID(row.id),
            symbol=StockSymbol(row.symbol),
            company=CompanyName(row.company_name),
            sector=Sector(row.sector),
            industry=Industry(row.industry, Sector(row.sector)),
            created_at=row.created_at,
            updated_at=row.updated_at
        )
    
    def to_persistence(self, stock: Stock) -> Dict[str, Any]:
        """Convert domain entity to persistence format."""
        return {
            "id": str(stock.id),
            "symbol": stock.symbol.value,
            "company_name": stock.company.value,
            "sector": stock.sector.value,
            "industry": stock.industry.value,
            "created_at": stock.created_at,
            "updated_at": stock.updated_at or datetime.utcnow()
        }
```

### Unit of Work Pattern

```python
# src/domain/repositories/i_unit_of_work.py
from abc import ABC, abstractmethod
from typing import TypeVar, Type

T = TypeVar('T')

class IUnitOfWork(ABC):
    """Unit of Work interface for managing transactions."""
    
    @abstractmethod
    async def __aenter__(self) -> 'IUnitOfWork':
        pass
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass
    
    @abstractmethod
    async def commit(self) -> None:
        """Commit the current transaction."""
        pass
    
    @abstractmethod
    async def rollback(self) -> None:
        """Rollback the current transaction."""
        pass
    
    @abstractmethod
    def repository(self, repo_type: Type[T]) -> T:
        """Get a repository instance within this unit of work."""
        pass

# Infrastructure implementation
class SqlAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session_factory):
        self._session_factory = session_factory
        self._repositories = {}
    
    async def __aenter__(self):
        self._session = self._session_factory()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self._session.close()
    
    async def commit(self):
        await self._session.commit()
    
    async def rollback(self):
        await self._session.rollback()
    
    def repository(self, repo_type: Type[T]) -> T:
        if repo_type not in self._repositories:
            if repo_type == IStockRepository:
                self._repositories[repo_type] = StockRepository(self._session)
            # Add other repository mappings
        
        return self._repositories[repo_type]
```

### Usage in Application Services

```python
# src/application/services/stock_application_service.py
class StockApplicationService:
    def __init__(self, unit_of_work: IUnitOfWork):
        self._uow = unit_of_work
    
    async def create_stock(self, command: CreateStockCommand) -> StockDTO:
        async with self._uow:
            stock_repo = self._uow.repository(IStockRepository)
            
            # Check if symbol already exists
            if await stock_repo.exists_with_symbol(command.symbol):
                raise StockAlreadyExistsError(command.symbol)
            
            # Create and save new stock
            stock = Stock.create(
                symbol=command.symbol,
                company=command.company,
                sector=command.sector,
                industry=command.industry
            )
            
            await stock_repo.save(stock)
            
        return StockDTO.from_domain(stock)
```

### Testing with Mock Repositories

```python
# tests/application/test_stock_service.py
class MockStockRepository(IStockRepository):
    def __init__(self):
        self._stocks = {}
    
    async def find_by_id(self, stock_id: UUID) -> Optional[Stock]:
        return self._stocks.get(stock_id)
    
    async def save(self, stock: Stock) -> None:
        self._stocks[stock.id] = stock
    
    async def exists_with_symbol(self, symbol: StockSymbol) -> bool:
        return any(s.symbol == symbol for s in self._stocks.values())

@pytest.mark.asyncio
async def test_create_stock():
    # Arrange
    mock_repo = MockStockRepository()
    mock_uow = MockUnitOfWork(stock_repository=mock_repo)
    service = StockApplicationService(mock_uow)
    
    command = CreateStockCommand(
        symbol=StockSymbol("AAPL"),
        company=CompanyName("Apple Inc."),
        sector=Sector("Technology"),
        industry=Industry("Consumer Electronics", Sector("Technology"))
    )
    
    # Act
    result = await service.create_stock(command)
    
    # Assert
    assert result.symbol == "AAPL"
    assert await mock_repo.exists_with_symbol(StockSymbol("AAPL"))
```

### Advanced Repository Methods

```python
class IPortfolioRepository(ABC):
    @abstractmethod
    async def find_with_transactions(
        self, portfolio_id: UUID
    ) -> Optional[PortfolioWithTransactions]:
        """Load portfolio aggregate with all transactions."""
        pass
    
    @abstractmethod
    async def find_by_user(self, user_id: UUID) -> List[Portfolio]:
        """Find all portfolios for a user."""
        pass
    
    @abstractmethod
    async def calculate_total_value(self, portfolio_id: UUID) -> Money:
        """Calculate portfolio value using optimized query."""
        pass
```

## Links

* Implements [ADR-0002: Use Clean Architecture](0002-use-clean-architecture.md)
* Supports [ADR-0003: Implement Domain-Driven Design](0003-implement-domain-driven-design.md)
* Uses [ADR-0006: Python FastAPI SQLAlchemy Stack](0006-python-fastapi-sqlalchemy-stack.md)
* References: "Patterns of Enterprise Application Architecture" by Martin Fowler
* References: "Domain-Driven Design" by Eric Evans