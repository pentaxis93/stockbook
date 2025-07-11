# Use SQLAlchemy Core Over ORM

* Status: accepted
* Deciders: Development team
* Date: 2025-01-11

## Context and Problem Statement

StockBook requires a database access strategy that aligns with our Clean Architecture principles and Domain-Driven Design approach. SQLAlchemy offers two distinct APIs: the ORM (Object Relational Mapper) with its declarative models and the Core API with explicit SQL construction. We need to choose an approach that maintains clean separation between our domain models and persistence concerns while providing the control and performance required for a financial application. Which SQLAlchemy API should we use for database access?

## Decision Drivers

* **Clean Architecture Alignment**: Domain entities must not depend on persistence framework
* **Explicit Control**: Need fine-grained control over SQL queries for optimization
* **Domain Model Purity**: Domain objects should not inherit from ORM base classes
* **Performance Requirements**: Financial calculations need optimized queries
* **Repository Pattern Support**: Must work well with repository abstractions
* **SQL Transparency**: Developers should understand what SQL is being generated
* **Migration Flexibility**: Ability to optimize or change queries without affecting domain

## Considered Options

* **SQLAlchemy Core**: Use Core API with explicit table definitions and query construction
* **SQLAlchemy ORM**: Use declarative ORM models with relationships
* **Raw SQL**: Write raw SQL queries with parameter binding
* **Query Builder Library**: Use a lightweight query builder like pypika
* **Hybrid Approach**: ORM for simple CRUD, Core for complex queries
* **Alternative ORM**: Consider Tortoise ORM or other async-first ORMs

## Decision Outcome

Chosen option: "SQLAlchemy Core", because it provides the perfect balance of abstraction and control while maintaining complete separation between domain and persistence layers. Core allows us to keep our domain models pure while still benefiting from SQLAlchemy's excellent connection management, query construction, and type safety features.

### Positive Consequences

* **Pure Domain Models**: Domain entities remain framework-agnostic
* **Explicit Queries**: Full control over SQL generation
* **Performance Optimization**: Easy to optimize queries when needed
* **Repository Pattern**: Natural fit with repository implementations
* **Type Safety**: Still get SQLAlchemy's type checking benefits
* **Migration Path**: Can easily add ORM later if needed for specific features
* **Learning Opportunity**: Team learns SQL properly

### Negative Consequences

* **More Verbose**: Requires explicit query construction
* **Manual Mapping**: Need to map between domain objects and database rows
* **No Lazy Loading**: Must explicitly handle relationships
* **Less Magic**: No automatic dirty checking or cascades

## Pros and Cons of the Options

### SQLAlchemy Core

Low-level SQL toolkit with programmatic query construction.

* Good, because maintains clean separation of concerns
* Good, because provides explicit control over queries
* Good, because supports repository pattern naturally
* Good, because no base class requirements for domain models
* Good, because excellent performance characteristics
* Good, because SQL knowledge transfers directly
* Bad, because more verbose than ORM
* Bad, because requires manual object mapping

### SQLAlchemy ORM

High-level ORM with declarative models and automatic mapping.

* Good, because less code to write
* Good, because automatic relationship handling
* Good, because built-in dirty checking
* Good, because familiar to many developers
* Bad, because couples domain to ORM base classes
* Bad, because implicit query generation
* Bad, because harder to optimize complex queries
* Bad, because violates Clean Architecture principles

### Raw SQL

Direct SQL queries with parameter binding.

* Good, because complete control
* Good, because no abstraction overhead
* Good, because SQL skills transfer directly
* Bad, because no query construction helpers
* Bad, because prone to SQL injection if not careful
* Bad, because database-specific SQL
* Bad, because lots of string manipulation

### Query Builder Library

Lightweight query builders like pypika or sqlbuilder.

* Good, because lightweight abstraction
* Good, because no ORM coupling
* Good, because programmatic query building
* Bad, because another dependency
* Bad, because less mature than SQLAlchemy
* Bad, because smaller community
* Bad, because limited feature set

### Hybrid Approach

Use ORM for simple cases, Core for complex queries.

* Good, because best tool for each job
* Good, because flexibility
* Bad, because inconsistent codebase
* Bad, because two mental models
* Bad, because team confusion
* Bad, because still couples some models to ORM

### Alternative ORM

Modern ORMs like Tortoise ORM designed for async.

* Good, because built for async from ground up
* Good, because modern Python features
* Bad, because less mature ecosystem
* Bad, because smaller community
* Bad, because still has ORM coupling issues
* Bad, because limited documentation

## Implementation Details

Our SQLAlchemy Core implementation approach:

### Table Definitions

```python
# src/infrastructure/database/tables.py
from sqlalchemy import Table, Column, String, DateTime, Numeric, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()

stocks_table = Table(
    "stocks",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("symbol", String(10), nullable=False, unique=True, index=True),
    Column("company_name", String(255), nullable=False),
    Column("sector", String(50), nullable=False),
    Column("industry", String(100), nullable=False),
    Column("created_at", DateTime, nullable=False),
    Column("updated_at", DateTime),
)

transactions_table = Table(
    "transactions",
    metadata,
    Column("id", UUID, primary_key=True),
    Column("portfolio_id", UUID, ForeignKey("portfolios.id"), nullable=False),
    Column("stock_id", UUID, ForeignKey("stocks.id"), nullable=False),
    Column("transaction_type", String(10), nullable=False),
    Column("quantity", Integer, nullable=False),
    Column("price", Numeric(10, 2), nullable=False),
    Column("transaction_date", DateTime, nullable=False),
    Column("created_at", DateTime, nullable=False),
)
```

### Repository Implementation

```python
# src/infrastructure/repositories/stock_repository.py
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

class StockRepository(IStockRepository):
    """SQLAlchemy Core implementation of stock repository."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def find_by_symbol(self, symbol: StockSymbol) -> Optional[Stock]:
        # Explicit query construction
        query = select(stocks_table).where(
            stocks_table.c.symbol == symbol.value
        )
        
        result = await self._session.execute(query)
        row = result.first()
        
        if not row:
            return None
        
        # Manual mapping to domain object
        return Stock(
            id=UUID(row.id),
            symbol=StockSymbol(row.symbol),
            company=CompanyName(row.company_name),
            sector=Sector(row.sector),
            industry=Industry(row.industry, Sector(row.sector)),
            created_at=row.created_at,
            updated_at=row.updated_at
        )
    
    async def save(self, stock: Stock) -> None:
        # Check if exists for upsert pattern
        exists_query = select(stocks_table.c.id).where(
            stocks_table.c.id == str(stock.id)
        )
        exists = await self._session.execute(exists_query)
        
        if exists.first():
            # Update
            stmt = (
                update(stocks_table)
                .where(stocks_table.c.id == str(stock.id))
                .values(
                    symbol=stock.symbol.value,
                    company_name=stock.company.value,
                    sector=stock.sector.value,
                    industry=stock.industry.value,
                    updated_at=datetime.utcnow()
                )
            )
        else:
            # Insert
            stmt = insert(stocks_table).values(
                id=str(stock.id),
                symbol=stock.symbol.value,
                company_name=stock.company.value,
                sector=stock.sector.value,
                industry=stock.industry.value,
                created_at=stock.created_at,
                updated_at=stock.updated_at
            )
        
        await self._session.execute(stmt)
```

### Complex Query Example

```python
async def find_portfolio_value(self, portfolio_id: UUID) -> Money:
    """Calculate portfolio value using optimized SQL query."""
    
    # Complex query with joins and aggregation
    query = (
        select(
            func.sum(
                transactions_table.c.quantity * stocks_table.c.current_price
            ).label('total_value')
        )
        .select_from(
            transactions_table
            .join(stocks_table, transactions_table.c.stock_id == stocks_table.c.id)
        )
        .where(transactions_table.c.portfolio_id == str(portfolio_id))
        .group_by(transactions_table.c.portfolio_id)
    )
    
    result = await self._session.execute(query)
    row = result.first()
    
    if not row or row.total_value is None:
        return Money(Decimal("0.00"))
    
    return Money(Decimal(str(row.total_value)))
```

### Migration Strategy

```python
# If we need ORM features later, we can create hybrid repositories
class HybridStockRepository(IStockRepository):
    """Can use Core or ORM as needed."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def find_by_symbol(self, symbol: StockSymbol) -> Optional[Stock]:
        # Can still use Core for queries
        return await self._find_by_symbol_core(symbol)
    
    async def load_with_relationships(self, stock_id: UUID) -> StockAggregate:
        # Can add ORM for specific complex loading if needed
        # But still return domain objects
        pass
```

### Performance Benefits

```python
# Bulk operations are efficient with Core
async def bulk_insert_stocks(self, stocks: List[Stock]) -> None:
    """Efficient bulk insert using Core."""
    
    values = [
        {
            "id": str(stock.id),
            "symbol": stock.symbol.value,
            "company_name": stock.company.value,
            "sector": stock.sector.value,
            "industry": stock.industry.value,
            "created_at": stock.created_at
        }
        for stock in stocks
    ]
    
    await self._session.execute(
        insert(stocks_table),
        values
    )
```

## Links

* Supports [ADR-0002: Use Clean Architecture](0002-use-clean-architecture.md)
* Implements [ADR-0008: Repository Pattern](0008-repository-pattern.md)
* Complements [ADR-0006: Python FastAPI SQLAlchemy Stack](0006-python-fastapi-sqlalchemy-stack.md)
* References: SQLAlchemy Core documentation
* References: "Clean Architecture" by Robert C. Martin