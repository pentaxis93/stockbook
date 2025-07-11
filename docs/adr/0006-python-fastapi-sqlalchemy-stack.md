# Python FastAPI SQLAlchemy Technology Stack

* Status: accepted
* Deciders: Development team
* Date: 2025-01-11

## Context and Problem Statement

StockBook requires a technology stack that supports building a robust, scalable financial portfolio management system. We need to choose programming language, web framework, database toolkit, and supporting libraries that align with our Clean Architecture principles while providing excellent developer experience and performance. What technology stack should we adopt to build a maintainable, type-safe, and performant application?

## Decision Drivers

* **Type Safety**: Need static typing support for financial calculations
* **Performance**: Must handle complex portfolio calculations efficiently
* **Developer Experience**: Tools should be productive and well-documented
* **Clean Architecture Fit**: Technologies must support our architectural patterns
* **Ecosystem Maturity**: Need stable, well-maintained libraries
* **Testing Support**: Excellent testing tools and frameworks required
* **Async Support**: Modern async/await patterns for scalability
* **Community**: Active community for support and hiring

## Considered Options

* **Python + FastAPI + SQLAlchemy Core**: Modern Python stack with async support
* **Python + Django + Django ORM**: Traditional full-stack Python framework
* **TypeScript + NestJS + TypeORM**: Enterprise Node.js framework
* **Go + Gin + GORM**: High-performance compiled language
* **Java + Spring Boot + Hibernate**: Enterprise Java stack
* **Rust + Actix + Diesel**: Systems programming with safety

## Decision Outcome

Chosen option: "Python + FastAPI + SQLAlchemy Core", because it provides the best balance of developer productivity, type safety through Python's type hints, excellent async support, and alignment with Clean Architecture principles. This stack allows us to build a maintainable system while leveraging Python's rich ecosystem for financial calculations.

### Positive Consequences

* **Type Safety**: Full static typing with mypy/pyright
* **High Performance**: FastAPI is one of the fastest Python frameworks
* **Clean Architecture**: Easy separation of concerns
* **Excellent Documentation**: Auto-generated OpenAPI docs
* **Modern Python**: Async/await, type hints, dataclasses
* **Testing Excellence**: pytest ecosystem is best-in-class
* **Developer Productivity**: Python's expressiveness and libraries

### Negative Consequences

* **Runtime Type Checking**: Types are hints, not enforced at runtime
* **GIL Limitations**: Python's Global Interpreter Lock affects CPU-bound tasks
* **Deployment Size**: Python applications larger than compiled languages
* **Performance Ceiling**: Not as fast as Go or Rust for computation

## Pros and Cons of the Options

### Python + FastAPI + SQLAlchemy Core

Modern Python stack focusing on performance and developer experience.

* Good, because FastAPI provides automatic OpenAPI documentation
* Good, because SQLAlchemy Core gives fine-grained SQL control
* Good, because Python has excellent financial/scientific libraries
* Good, because async support throughout the stack
* Good, because type hints provide static analysis
* Good, because pytest is the gold standard for testing
* Bad, because Python performance limited by GIL
* Bad, because runtime type safety requires discipline

### Python + Django + Django ORM

Traditional batteries-included Python web framework.

* Good, because mature and battle-tested
* Good, because includes everything out of the box
* Good, because large community and resources
* Bad, because Django ORM fights Clean Architecture
* Bad, because heavy and opinionated
* Bad, because async support is recent and incomplete
* Bad, because harder to separate concerns

### TypeScript + NestJS + TypeORM

Enterprise-grade Node.js framework with strong typing.

* Good, because compile-time type safety
* Good, because familiar to frontend developers
* Good, because excellent async support
* Bad, because less mature financial libraries
* Bad, because TypeORM can be limiting
* Bad, because JavaScript ecosystem churn
* Bad, because fewer data science tools

### Go + Gin + GORM

High-performance compiled language with simple syntax.

* Good, because excellent performance
* Good, because compiles to single binary
* Good, because great concurrency model
* Good, because simple and maintainable
* Bad, because less expressive than Python
* Bad, because fewer financial libraries
* Bad, because GORM fights Clean Architecture
* Bad, because verbose error handling

### Java + Spring Boot + Hibernate

Enterprise Java stack with decades of maturity.

* Good, because extremely mature ecosystem
* Good, because strong type system
* Good, because excellent tooling
* Bad, because verbose and ceremonious
* Bad, because Hibernate complexity
* Bad, because slower development cycle
* Bad, because heavyweight for our needs

### Rust + Actix + Diesel

Systems programming language with memory safety.

* Good, because blazing fast performance
* Good, because memory safety guarantees
* Good, because excellent type system
* Bad, because steep learning curve
* Bad, because longer development time
* Bad, because smaller ecosystem
* Bad, because overkill for web application

## Implementation Details

Our technology stack implementation includes:

### Core Technologies

#### Python 3.11+
- Type hints for static analysis
- Async/await for concurrent operations
- Dataclasses for value objects
- Pattern matching for complex logic

#### FastAPI
```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI(
    title="StockBook API",
    description="Portfolio Management System",
    version="1.0.0",
)

@app.post("/stocks", response_model=StockResponse)
async def create_stock(
    request: CreateStockRequest,
    service: StockApplicationService = Depends(get_stock_service)
) -> StockResponse:
    stock = await service.create_stock(request)
    return StockResponse.from_domain(stock)
```

#### SQLAlchemy Core
```python
from sqlalchemy import Table, Column, String, DateTime, MetaData

metadata = MetaData()

stocks_table = Table(
    "stocks",
    metadata,
    Column("id", String, primary_key=True),
    Column("symbol", String, nullable=False, unique=True),
    Column("company_name", String, nullable=False),
    Column("sector", String, nullable=False),
    Column("created_at", DateTime, nullable=False),
)

# Repository implementation using Core
class StockRepository(IStockRepository):
    async def save(self, stock: Stock) -> None:
        query = stocks_table.insert().values(
            id=str(stock.id),
            symbol=stock.symbol.value,
            company_name=stock.company.value,
            sector=stock.sector.value,
            created_at=stock.created_at,
        )
        await self._connection.execute(query)
```

### Supporting Libraries

#### Type Checking
- **mypy**: Static type checker
- **pyright**: Microsoft's type checker (strict mode)
- **pydantic**: Runtime validation and serialization

#### Testing
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking utilities
- **hypothesis**: Property-based testing

#### Code Quality
- **ruff**: Fast Python linter
- **black**: Code formatter
- **isort**: Import sorter
- **bandit**: Security linter
- **pre-commit**: Git hooks framework

#### Development Tools
- **uvicorn**: ASGI server
- **alembic**: Database migrations
- **httpx**: Async HTTP client
- **python-dotenv**: Environment management

### Configuration Example

```toml
# pyproject.toml
[tool.pyright]
pythonVersion = "3.11"
typeCheckingMode = "strict"
reportMissingImports = true
reportMissingTypeStubs = false

[tool.pytest.ini_options]
minversion = "7.0"
addopts = [
    "--strict-markers",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-fail-under=90",
]

[tool.ruff]
target-version = "py311"
line-length = 88
select = ["E", "F", "B", "I", "N", "UP", "S", "A", "C4", "ICN", "PIE", "T20"]
```

### Performance Considerations

1. **Async Everywhere**: Use async/await for I/O operations
2. **Connection Pooling**: Configure SQLAlchemy connection pools
3. **Caching**: Redis for frequently accessed data
4. **Background Tasks**: Celery for long-running operations
5. **Profiling**: py-spy for performance analysis

### Deployment Strategy

```dockerfile
# Multi-stage build for smaller images
FROM python:3.11-slim as builder

# Install dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-root

FROM python:3.11-slim
COPY --from=builder /app/.venv /app/.venv
COPY src/ /app/src/

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Links

* Implements [ADR-0002: Use Clean Architecture](0002-use-clean-architecture.md)
* Supports [ADR-0003: Implement Domain-Driven Design](0003-implement-domain-driven-design.md)
* Enables [ADR-0005: Mandate Test-Driven Development](0005-mandate-test-driven-development.md)
* References: FastAPI documentation (https://fastapi.tiangolo.com)
* References: SQLAlchemy documentation (https://www.sqlalchemy.org)