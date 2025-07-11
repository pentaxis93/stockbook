# Implement Domain-Driven Design

* Status: accepted
* Deciders: Development team
* Date: 2025-01-11

## Context and Problem Statement

StockBook deals with complex financial domain logic including portfolio management, stock transactions, performance calculations, and risk assessment. We need a design approach that captures this complexity while keeping the code maintainable and aligned with business requirements. How should we model our domain to ensure that business rules are properly encapsulated and the code reflects the language used by domain experts?

## Decision Drivers

* **Complex Business Rules**: Portfolio calculations, transaction validation, and risk metrics require sophisticated logic
* **Domain Expert Communication**: Need to use the same language as financial professionals
* **Business Logic Encapsulation**: Prevent business rules from leaking into infrastructure or presentation layers
* **Model Integrity**: Ensure domain objects are always in a valid state
* **Evolving Requirements**: Financial domain rules change frequently and must be easy to modify
* **Team Understanding**: New developers should understand the business domain through the code

## Considered Options

* **Anemic Domain Model**: Simple data structures with logic in service layers
* **Rich Domain Model (DDD)**: Business logic encapsulated within domain entities
* **Transaction Script**: Procedural approach with business logic in transaction scripts
* **Table Module**: One class per database table with associated logic
* **Active Record**: Domain objects that know how to persist themselves

## Decision Outcome

Chosen option: "Rich Domain Model (DDD)", because it provides the best encapsulation of complex business rules while maintaining a clear separation between domain logic and technical concerns. This approach ensures our code speaks the language of the business domain and makes complex financial calculations explicit and testable.

### Positive Consequences

* **Business Logic Encapsulation**: All rules are contained within domain objects
* **Ubiquitous Language**: Code uses the same terms as domain experts
* **Invariant Protection**: Domain objects enforce their own validity
* **Explicit Business Rules**: Complex calculations are clear and documented
* **Easy to Test**: Business logic can be tested without infrastructure
* **Knowledge Capture**: Domain knowledge is codified in the model

### Negative Consequences

* **Initial Complexity**: Requires more upfront design and thinking
* **Learning Curve**: Team needs to understand DDD concepts
* **More Classes**: Value objects and entities create more files
* **Mapping Overhead**: Need to map between domain objects and persistence

## Pros and Cons of the Options

### Anemic Domain Model

Domain objects are simple data containers with getters/setters, logic resides in service layers.

* Good, because simple to understand initially
* Good, because easy to map to database tables
* Bad, because business logic scattered across services
* Bad, because no encapsulation of invariants
* Bad, because leads to procedural code
* Bad, because difficult to maintain as complexity grows

### Rich Domain Model (DDD)

Domain objects encapsulate both data and behavior with careful attention to business rules.

* Good, because business logic is cohesive and encapsulated
* Good, because enforces invariants at all times
* Good, because uses ubiquitous language from the domain
* Good, because makes complex rules explicit
* Good, because supports tactical patterns (entities, value objects, aggregates)
* Bad, because requires more design effort upfront
* Bad, because team needs DDD knowledge

### Transaction Script

Each business transaction is implemented as a single procedure.

* Good, because straightforward for simple operations
* Good, because easy to understand flow
* Bad, because leads to code duplication
* Bad, because difficult to reuse logic
* Bad, because becomes unwieldy with complexity
* Bad, because no domain model emerges

### Table Module

One class per database table containing all logic for that table.

* Good, because maps directly to database schema
* Good, because familiar to database-centric developers
* Bad, because couples domain to database structure
* Bad, because cross-table logic becomes complex
* Bad, because difficult to express domain concepts

### Active Record

Domain objects that know how to load and save themselves.

* Good, because simple for CRUD operations
* Good, because reduces layers
* Bad, because violates single responsibility principle
* Bad, because couples domain to persistence
* Bad, because makes testing difficult
* Bad, because inappropriate for complex domains

## Implementation Details

Our Domain-Driven Design implementation includes:

### Core Building Blocks

#### 1. Entities
Objects with identity that persists over time:
- **Stock**: Represents a tradable security with symbol, company, sector
- **Portfolio**: Collection of investments with performance tracking
- **Transaction**: Record of buying or selling stocks
- **Target**: Price targets for stocks
- **JournalEntry**: Investment notes and analysis

#### 2. Value Objects
Immutable objects that represent domain concepts:
- **Money**: Encapsulates amount and currency with precision
- **Quantity**: Share quantities with validation
- **StockSymbol**: Validated and normalized ticker symbols
- **Sector/Industry**: Hierarchical categorization
- **CompanyName**: Formatted company names
- **PortfolioName**: Validated portfolio names

#### 3. Domain Services
Operations that don't naturally belong to an entity:
- **PortfolioCalculationService**: Complex portfolio metrics
- **RiskAssessmentService**: Risk analysis and scoring
- **SectorIndustryService**: Categorization validation

#### 4. Repository Interfaces
Abstractions for persistence (implemented in infrastructure):
```python
class IStockRepository(ABC):
    @abstractmethod
    async def find_by_id(self, stock_id: UUID) -> Optional[Stock]:
        pass
    
    @abstractmethod
    async def find_by_symbol(self, symbol: str) -> Optional[Stock]:
        pass
    
    @abstractmethod
    async def save(self, stock: Stock) -> None:
        pass
```

### Domain Events
Foundation for event-driven features:
```python
@dataclass
class StockCreatedEvent(DomainEvent):
    stock_id: UUID
    symbol: str
    timestamp: datetime

@dataclass
class TransactionExecutedEvent(DomainEvent):
    transaction_id: UUID
    stock_id: UUID
    quantity: int
    price: Decimal
    timestamp: datetime
```

### Aggregate Design

Aggregates define consistency boundaries:

1. **Stock Aggregate**
   - Root: Stock entity
   - Ensures symbol uniqueness
   - Validates sector/industry combinations

2. **Portfolio Aggregate**
   - Root: Portfolio entity
   - Contains: Transactions, Targets
   - Ensures transaction consistency

### Business Rule Examples

```python
class Stock(Entity):
    def __init__(self, symbol: StockSymbol, company: CompanyName, 
                 sector: Sector, industry: Industry):
        # Invariant: Symbol must be valid
        if not symbol.is_valid():
            raise InvalidStockSymbolError(symbol.value)
        
        # Invariant: Sector/Industry must be valid combination
        if not self._sector_industry_service.is_valid_combination(sector, industry):
            raise InvalidSectorIndustryError(sector, industry)
        
        self.symbol = symbol
        self.company = company
        self.sector = sector
        self.industry = industry

class Transaction(Entity):
    def calculate_value(self) -> Money:
        """Domain logic for transaction value calculation"""
        return Money(self.quantity * self.price)
    
    def is_buy(self) -> bool:
        """Business rule: positive quantity means buy"""
        return self.quantity > 0
```

## Links

* Implements [ADR-0002: Use Clean Architecture](0002-use-clean-architecture.md)
* Refined by [ADR-0004: Use Dependency Injection](0004-use-dependency-injection.md)
* References: "Domain-Driven Design" by Eric Evans
* References: "Implementing Domain-Driven Design" by Vaughn Vernon