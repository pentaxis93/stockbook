# StockBook Architecture Primer

**A Developer's Guide to Understanding StockBook's Clean Architecture Implementation**

---

## Table of Contents

1. [Overview](#overview)
2. [Architectural Principles](#architectural-principles)
3. [Layer-by-Layer Breakdown](#layer-by-layer-breakdown)
4. [Core Components](#core-components)
5. [Development Workflow](#development-workflow)
6. [Practical Examples](#practical-examples)
7. [Testing Strategy](#testing-strategy)
8. [Best Practices](#best-practices)

---

## Overview

StockBook is built using **Clean Architecture** principles with **Domain-Driven Design (DDD)** patterns, providing a robust, maintainable, and testable codebase for personal stock portfolio management. This architecture ensures that business logic remains independent of external concerns like databases, frameworks, and UI technologies.

### Why Clean Architecture?

- **Independence**: Business logic is isolated from external dependencies
- **Testability**: Each layer can be tested independently with comprehensive coverage
- **Maintainability**: Changes in one layer don't cascade through the entire system
- **Flexibility**: Easy to swap implementations (e.g., database, UI framework)
- **Scalability**: Architecture supports growth in complexity and team size

### Architecture Visualization

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Controllers │  │ Coordinators│  │  Adapters   │         │
│  │             │  │             │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│                    Application Layer                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Services   │  │  Commands   │  │    DTOs     │         │
│  │             │  │             │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│                     Domain Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Entities   │  │  Services   │  │ Repositories│         │
│  │             │  │             │  │ (Interfaces)│         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│                  Infrastructure Layer                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Repositories│  │  Database   │  │ External    │         │
│  │(Implementations)│ Connections │  │  Services   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
              ┌─────────────────────────────────┐
              │         Shared Kernel           │
              │   Value Objects | Events        │
              │   Exceptions   | Interfaces     │
              └─────────────────────────────────┘
```

---

## Architectural Principles

### 1. Dependency Rule

**Dependencies point inward**: Outer layers can depend on inner layers, but inner layers cannot depend on outer layers.

```python
# ✅ CORRECT: Presentation depends on Application
from application.services.stock_application_service import StockApplicationService

# ✅ CORRECT: Application depends on Domain
from domain.entities.stock_entity import StockEntity

# ❌ WRONG: Domain depending on Infrastructure
from infrastructure.repositories.sqlite_stock_repository import SqliteStockRepository
```

### 2. Separation of Concerns

Each layer has a single, well-defined responsibility:

- **Domain**: Business logic and rules
- **Application**: Use case orchestration  
- **Infrastructure**: External concerns (database, APIs)
- **Presentation**: User interface and interaction

### 3. Interface Segregation

Use interfaces to define contracts between layers:

```python
# Domain defines the contract
class IStockRepository(ABC):
    def create(self, stock: StockEntity) -> int: ...
    def get_by_symbol(self, symbol: StockSymbol) -> Optional[StockEntity]: ...

# Infrastructure implements the contract
class SqliteStockRepository(IStockRepository):
    def create(self, stock: StockEntity) -> int:
        # SQLite-specific implementation
```

---

## Layer-by-Layer Breakdown

### Domain Layer (`domain/`)

**Purpose**: Contains the core business logic, entities, and rules that define what StockBook does.

**Key Components**:

#### Entities (`domain/entities/`)
Rich objects that encapsulate business logic and maintain invariants:

```python
class StockEntity:
    """Rich domain entity with business logic"""
    
    def __init__(self, symbol: StockSymbol, name: str, ...):
        self._validate_inputs(symbol, name)
        self.symbol = symbol
        self.name = name
    
    def update_grade(self, new_grade: str) -> None:
        """Business logic for grade updates"""
        if new_grade not in self.VALID_GRADES:
            raise InvalidGradeError(f"Grade must be one of: {self.VALID_GRADES}")
        self.grade = new_grade
```

#### Value Objects (`domain/value_objects/`)
Immutable objects that represent concepts without identity:

```python
class StockSymbol:
    """Value object ensuring symbol validity"""
    
    def __init__(self, value: str):
        self._validate_symbol_format(value)
        self._value = value.upper()
    
    @property
    def value(self) -> str:
        return self._value
```

#### Domain Services (`domain/services/`)
Operations that don't naturally belong to a specific entity:

```python
class PortfolioCalculationService:
    """Domain service for complex portfolio calculations"""
    
    def calculate_diversification_score(self, stocks: List[StockEntity]) -> float:
        # Complex business logic that spans multiple entities
```

#### Repository Interfaces (`domain/repositories/`)
Contracts for data access without implementation details:

```python
class IStockRepository(ABC):
    """Domain contract for stock data access"""
    
    @abstractmethod
    def create(self, stock: StockEntity) -> int: ...
    
    @abstractmethod
    def get_by_symbol(self, symbol: StockSymbol) -> Optional[StockEntity]: ...
```

### Application Layer (`application/`)

**Purpose**: Orchestrates domain entities to fulfill specific use cases.

#### Application Services (`application/services/`)
Coordinate domain entities and repositories to implement use cases:

```python
class StockApplicationService:
    """Orchestrates stock-related use cases"""
    
    def __init__(self, unit_of_work: IStockBookUnitOfWork):
        self._unit_of_work = unit_of_work
    
    def create_stock(self, command: CreateStockCommand) -> StockDto:
        """Use case: Create a new stock"""
        with self._unit_of_work:
            # 1. Validate business rules
            if self._unit_of_work.stocks.get_by_symbol(command.symbol):
                raise DuplicateStockError(f"Stock {command.symbol} already exists")
            
            # 2. Create domain entity
            stock = StockEntity(command.symbol, command.name, ...)
            
            # 3. Persist through repository
            stock_id = self._unit_of_work.stocks.create(stock)
            
            # 4. Return DTO for presentation layer
            return StockDto.from_entity(stock, stock_id)
```

#### Commands (`application/commands/`)
Request objects that encapsulate operation parameters:

```python
@dataclass
class CreateStockCommand:
    """Command for creating a new stock"""
    symbol: str
    name: str
    industry_group: Optional[str] = None
    grade: Optional[str] = None
    notes: str = ""
```

#### DTOs (`application/dto/`)
Data transfer objects for communication between layers:

```python
@dataclass
class StockDto:
    """Data transfer object for stocks"""
    id: int
    symbol: str
    name: str
    industry_group: Optional[str]
    grade: Optional[str]
    notes: str
    
    @classmethod
    def from_entity(cls, entity: StockEntity, stock_id: int) -> 'StockDto':
        """Convert domain entity to DTO"""
        return cls(
            id=stock_id,
            symbol=entity.symbol.value,
            name=entity.name,
            # ... other fields
        )
```

### Infrastructure Layer (`infrastructure/`)

**Purpose**: Implements technical concerns like data persistence and external service integration.

#### Repositories (`infrastructure/repositories/`)
Concrete implementations of domain repository interfaces:

```python
class SqliteStockRepository(IStockRepository):
    """SQLite implementation of stock repository"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db_connection = db_connection
    
    def create(self, stock: StockEntity) -> int:
        """Persist stock entity to SQLite database"""
        with self.db_connection.transaction() as conn:
            cursor = conn.execute("""
                INSERT INTO stock (symbol, name, industry_group, grade, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (
                stock.symbol.value,
                stock.name,
                stock.industry_group.value if stock.industry_group else None,
                stock.grade,
                stock.notes
            ))
            return cursor.lastrowid
```

#### Persistence (`infrastructure/persistence/`)
Database connections and transaction management:

```python
class SqliteUnitOfWork(IStockBookUnitOfWork):
    """Unit of Work pattern implementation"""
    
    def __enter__(self):
        self._transaction = self.db_connection.begin_transaction()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self._transaction.commit()
        else:
            self._transaction.rollback()
```

### Presentation Layer (`presentation/`)

**Purpose**: Handles user interaction and UI concerns.

#### Controllers (`presentation/controllers/`)
Coordinate between UI and application services:

```python
class StockController:
    """Handles stock-related UI interactions"""
    
    def __init__(self, stock_service: StockApplicationService):
        self.stock_service = stock_service
    
    def create_stock(self, request: CreateStockRequest) -> Union[CreateStockResponse, ValidationErrorResponse]:
        """Handle stock creation request from UI"""
        try:
            # Convert UI request to application command
            command = CreateStockCommand(
                symbol=request.symbol,
                name=request.name,
                # ... other fields
            )
            
            # Execute use case
            stock_dto = self.stock_service.create_stock(command)
            
            # Return success response
            return CreateStockResponse(
                success=True,
                stock=StockViewModel.from_dto(stock_dto)
            )
        except ValidationError as e:
            return ValidationErrorResponse(errors=e.errors)
```

#### Coordinators (`presentation/coordinators/`)
Orchestrate complex UI workflows:

```python
class StockPageCoordinator:
    """Coordinates the stock management page workflow"""
    
    def render_stock_page(self):
        """Render complete stock management interface"""
        self._render_header()
        self._render_stock_list()
        self._render_create_form()
        self._handle_user_interactions()
```

#### Adapters (`presentation/adapters/`)
Bridge between clean architecture and UI frameworks:

```python
class StreamlitStockAdapter:
    """Adapts stock operations to Streamlit UI framework"""
    
    def render_create_form(self) -> Optional[CreateStockRequest]:
        """Render Streamlit form for stock creation"""
        with st.form("create_stock"):
            symbol = st.text_input("Symbol", max_chars=10)
            name = st.text_input("Company Name", max_chars=200)
            submitted = st.form_submit_button("Create Stock")
            
            if submitted:
                return CreateStockRequest(symbol=symbol, name=name)
        return None
```

---

## Core Components

### Shared Kernel (`shared_kernel/`)

Contains reusable components used across multiple bounded contexts:

#### Value Objects
```python
class Money:
    """Immutable money representation with currency"""
    
    def __init__(self, amount: Decimal, currency: str):
        self.amount = amount
        self.currency = currency
    
    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise CurrencyMismatchError()
        return Money(self.amount + other.amount, self.currency)

class Quantity:
    """Represents quantities with validation"""
    
    def __init__(self, value: int):
        if value < 0:
            raise ValueError("Quantity cannot be negative")
        self.value = value
```

### Dependency Injection (`dependency_injection/`)

Professional IoC container for managing dependencies:

#### DI Container
```python
class DIContainer:
    """Dependency injection container"""
    
    def register_singleton(self, service_type: Type[T], implementation: Type[T]):
        """Register a singleton service"""
    
    def register_transient(self, service_type: Type[T], implementation: Type[T]):
        """Register a transient service"""
    
    def resolve(self, service_type: Type[T]) -> T:
        """Resolve a service instance"""
```

#### Composition Root
```python
class CompositionRoot:
    """Central dependency configuration"""
    
    @classmethod
    def configure(cls, database_path: str) -> DIContainer:
        container = DIContainer()
        
        # Infrastructure
        container.register_singleton(DatabaseConnection, lambda: DatabaseConnection(database_path))
        container.register_singleton(IStockBookUnitOfWork, SqliteUnitOfWork)
        container.register_transient(IStockRepository, SqliteStockRepository)
        
        # Application
        container.register_transient(StockApplicationService)
        
        # Presentation
        container.register_transient(StockController)
        
        return container
```

---

## Development Workflow

### 1. Adding New Features

Follow the **inside-out** approach:

1. **Start with Domain**: Create entities, value objects, and domain services
2. **Add Application Logic**: Create application services and commands
3. **Implement Infrastructure**: Add repository implementations
4. **Build Presentation**: Create controllers and UI adapters

### 2. Test-Driven Development

Write tests at each layer:

```python
# Domain layer test
def test_stock_entity_validates_symbol():
    with pytest.raises(InvalidSymbolError):
        StockEntity(StockSymbol(""), "Test Company")

# Application layer test  
def test_create_stock_use_case():
    command = CreateStockCommand(symbol="AAPL", name="Apple Inc.")
    result = stock_service.create_stock(command)
    assert result.symbol == "AAPL"

# Infrastructure layer test
def test_sqlite_repository_creates_stock():
    stock = StockEntity(StockSymbol("MSFT"), "Microsoft")
    stock_id = repository.create(stock)
    assert stock_id > 0
```

### 3. Error Handling Strategy

Use domain exceptions for business rule violations:

```python
# Domain exceptions
class StockDomainError(DomainError):
    """Base exception for stock domain errors"""

class DuplicateStockError(StockDomainError):
    """Raised when attempting to create duplicate stock"""

class InvalidSymbolError(StockDomainError):  
    """Raised for invalid stock symbols"""
```

---

## Practical Examples

### Example 1: Creating a New Stock

**Step 1: Domain Entity**
```python
# domain/entities/stock_entity.py
class StockEntity:
    def __init__(self, symbol: StockSymbol, name: str):
        self._validate_name(name)
        self.symbol = symbol
        self.name = name
```

**Step 2: Application Service**
```python
# application/services/stock_application_service.py
def create_stock(self, command: CreateStockCommand) -> StockDto:
    with self._unit_of_work:
        # Business logic
        stock = StockEntity(StockSymbol(command.symbol), command.name)
        stock_id = self._unit_of_work.stocks.create(stock)
        return StockDto.from_entity(stock, stock_id)
```

**Step 3: Infrastructure Implementation**
```python
# infrastructure/repositories/sqlite_stock_repository.py
def create(self, stock: StockEntity) -> int:
    with self.db_connection.transaction() as conn:
        cursor = conn.execute(
            "INSERT INTO stock (symbol, name) VALUES (?, ?)",
            (stock.symbol.value, stock.name)
        )
        return cursor.lastrowid
```

**Step 4: Presentation Layer**
```python
# presentation/controllers/stock_controller.py
def create_stock(self, request: CreateStockRequest) -> CreateStockResponse:
    command = CreateStockCommand(symbol=request.symbol, name=request.name)
    stock_dto = self.stock_service.create_stock(command)
    return CreateStockResponse(success=True, stock=StockViewModel.from_dto(stock_dto))
```

### Example 2: Adding a New Repository

**Step 1: Define Domain Interface**
```python
# domain/repositories/interfaces.py
class IPortfolioRepository(ABC):
    @abstractmethod
    def create(self, portfolio: PortfolioEntity) -> int: ...
    
    @abstractmethod
    def get_by_id(self, portfolio_id: int) -> Optional[PortfolioEntity]: ...
```

**Step 2: Implement Infrastructure**
```python
# infrastructure/repositories/sqlite_portfolio_repository.py
class SqlitePortfolioRepository(IPortfolioRepository):
    def create(self, portfolio: PortfolioEntity) -> int:
        # SQLite implementation
```

**Step 3: Register in Composition Root**
```python
# dependency_injection/composition_root.py
container.register_transient(IPortfolioRepository, SqlitePortfolioRepository)
```

---

## Testing Strategy

### Test Structure

```
tests/
├── domain/              # Domain layer tests (fast, isolated)
├── application/         # Application service tests (medium)
├── infrastructure/      # Repository and database tests (slower)
├── presentation/        # UI and controller tests (fast)
└── integration/         # End-to-end tests (slowest)
```

### Test Categories

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test layer interactions
3. **End-to-End Tests**: Test complete workflows

### Test Examples

```python
# Domain unit test
class TestStockEntity:
    def test_create_valid_stock(self):
        stock = StockEntity(StockSymbol("AAPL"), "Apple Inc.")
        assert stock.symbol.value == "AAPL"
        assert stock.name == "Apple Inc."

# Application integration test
class TestStockApplicationService:
    def test_create_stock_integration(self):
        service = container.resolve(StockApplicationService)
        command = CreateStockCommand(symbol="MSFT", name="Microsoft")
        result = service.create_stock(command)
        assert result.symbol == "MSFT"

# Infrastructure test
class TestSqliteStockRepository:
    def test_repository_persists_stock(self):
        stock = StockEntity(StockSymbol("GOOGL"), "Alphabet Inc.")
        stock_id = repository.create(stock)
        retrieved = repository.get_by_id(stock_id)
        assert retrieved.symbol.value == "GOOGL"
```

---

## Best Practices

### 1. Dependency Management

- Always depend on interfaces, not implementations
- Use dependency injection for all external dependencies
- Register dependencies in the composition root only

### 2. Domain Modeling

- Keep entities rich with business logic
- Make value objects immutable
- Use domain services for operations spanning multiple entities
- Validate business rules in the domain layer

### 3. Error Handling

- Use domain exceptions for business rule violations
- Handle technical exceptions in infrastructure
- Transform exceptions appropriately at layer boundaries

### 4. Testing

- Write tests first (TDD approach)
- Test each layer independently
- Use mocks for external dependencies
- Maintain high test coverage (95%+)

### 5. Code Organization

- Keep layers separate and well-organized
- Use clear, descriptive naming
- Follow single responsibility principle
- Document architectural decisions

### 6. Performance

- Use appropriate lifetime management in DI container
- Implement connection pooling for database access
- Consider caching for expensive operations
- Monitor and measure performance

---

## Getting Started as a StockBook Developer

### 1. Understanding the Codebase

1. **Start with Domain**: Read `domain/entities/` to understand business concepts
2. **Review Interfaces**: Check `domain/repositories/interfaces.py` for contracts
3. **Examine Application Services**: Look at `application/services/` for use cases
4. **Study Tests**: Read tests to understand expected behavior

### 2. Making Changes

1. **Write Tests First**: Define expected behavior with failing tests
2. **Follow Layer Boundaries**: Respect dependency directions
3. **Use Existing Patterns**: Follow established conventions
4. **Run Quality Checks**: Use `pytest`, `pylint`, `pyright`, `black`, `isort`

### 3. Common Development Tasks

- **Adding New Entity**: Start in `domain/entities/`, add tests, implement repositories
- **New Use Case**: Create application service method, add command/DTO
- **UI Changes**: Work in `presentation/` layer, use existing adapters
- **Database Changes**: Update schema, modify repository implementations

---

## Conclusion

StockBook's clean architecture provides a robust foundation for sustainable development. By understanding and following these architectural principles, developers can:

- Build maintainable, testable code
- Easily extend functionality
- Adapt to changing requirements
- Work confidently within established patterns

The architecture may seem complex initially, but it pays dividends in code quality, maintainability, and developer productivity over time. Each layer has a clear purpose, and the dependency injection system ensures components work together seamlessly while remaining loosely coupled.

Remember: **When in doubt, follow the dependency rule and keep business logic in the domain layer.**

---

*For more information, see the project [README](../README.md).*