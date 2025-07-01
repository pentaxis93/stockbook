# StockBook Architecture Documentation

## Table of Contents
1. [Overview](#overview)
2. [Clean Architecture Implementation](#clean-architecture-implementation)
3. [Domain-Driven Design](#domain-driven-design)
4. [Dependency Injection](#dependency-injection)
5. [Testing Strategy](#testing-strategy)
6. [Current Implementation Status](#current-implementation-status)
7. [Future Architecture](#future-architecture)

## Overview

StockBook is built using Clean Architecture principles combined with Domain-Driven Design (DDD) patterns. The architecture prioritizes:

- **Separation of Concerns**: Each layer has a specific responsibility
- **Dependency Inversion**: Dependencies flow inward toward the domain
- **Testability**: Every component is designed to be easily testable
- **Maintainability**: Clear boundaries make changes predictable
- **Type Safety**: Full static typing throughout the codebase

## Clean Architecture Implementation

### Layer Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│                      (Not yet implemented)               │
│  • REST API Controllers  • Request/Response Models      │
│  • Authentication       • OpenAPI Documentation         │
├─────────────────────────────────────────────────────────┤
│                    Application Layer ✅                  │
│  • Use Cases (Services) • Commands & Queries            │
│  • DTOs                 • Application Logic             │
├─────────────────────────────────────────────────────────┤
│                      Domain Layer ✅                     │
│  • Entities            • Value Objects                  │
│  • Domain Services     • Repository Interfaces          │
│  • Domain Events       • Business Rules                 │
├─────────────────────────────────────────────────────────┤
│                  Infrastructure Layer                    │
│                   (Not yet implemented)                  │
│  • Database Access     • External Services              │
│  • Repositories        • Persistence                    │
└─────────────────────────────────────────────────────────┘

→ Dependencies flow inward (outer layers depend on inner layers)
```

### Layer Responsibilities

#### Domain Layer (Core Business Logic)
- **Purpose**: Contains all business logic and rules
- **Components**:
  - Entities: Business objects with identity (Stock, Portfolio, Transaction)
  - Value Objects: Immutable objects without identity (Money, Quantity)
  - Domain Services: Complex business operations
  - Repository Interfaces: Contracts for data persistence
- **Dependencies**: None (purest layer)

#### Application Layer (Use Cases)
- **Purpose**: Orchestrates business operations
- **Components**:
  - Application Services: Coordinate domain objects
  - Commands: Represent intentions to change state
  - DTOs: Data transfer between layers
- **Dependencies**: Domain layer only

#### Infrastructure Layer (External Concerns) - *Planned*
- **Purpose**: Handles all external concerns
- **Components**:
  - Repository Implementations
  - Database connections
  - External service integrations
- **Dependencies**: Domain and Application layers

#### Presentation Layer (User Interface) - *Planned*
- **Purpose**: Handles HTTP requests and responses
- **Components**:
  - REST API controllers
  - Request/Response models
  - Authentication/Authorization
- **Dependencies**: Application layer only

## Domain-Driven Design

### Entity Model

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│   Stock     │     │  Portfolio  │     │ Transaction  │
├─────────────┤     ├─────────────┤     ├──────────────┤
│ id          │     │ id          │     │ id           │
│ symbol      │◄────┤ name        │     │ stock_id     │──┐
│ company     │     │ description │     │ portfolio_id │  │
│ sector      │     └─────────────┘     │ type         │  │
│ industry    │            ▲            │ quantity     │  │
└─────────────┘            │            │ price        │  │
                           │            │ date         │  │
                           │            └──────────────┘  │
                           │                              │
                           └──────────────────────────────┘

┌─────────────────┐     ┌──────────────────┐
│  Target         │     │  JournalEntry    │
├─────────────────┤     ├──────────────────┤
│ id              │     │ id               │
│ stock_id        │     │ stock_id         │
│ portfolio_id    │     │ date             │
│ target_price    │     │ content          │
│ status          │     │ sentiment        │
└─────────────────┘     └──────────────────┘
```

### Value Objects

Value objects encapsulate domain concepts and enforce business rules:

- **Money**: Handles currency and amount with precision
- **Quantity**: Represents share quantities with validation
- **StockSymbol**: Validates and normalizes stock symbols
- **Sector/Industry**: Categorization with validation
- **CompanyName**: Company name with formatting rules
- **PortfolioName**: Portfolio naming with constraints

### Domain Services

Complex business operations that don't belong to a single entity:

1. **PortfolioCalculationService**
   - Calculate portfolio value
   - Compute returns and performance metrics
   - Analyze asset allocation

2. **RiskAssessmentService**
   - Evaluate portfolio risk metrics
   - Calculate diversification scores
   - Identify concentration risks

3. **SectorIndustryService**
   - Validate sector/industry combinations
   - Provide categorization logic

### Domain Events

Event-driven architecture foundation (implemented, not yet used):

```python
# Example domain events
class StockCreatedEvent(DomainEvent):
    stock_id: UUID
    symbol: str
    timestamp: datetime

class TransactionExecutedEvent(DomainEvent):
    transaction_id: UUID
    stock_id: UUID
    quantity: int
    price: Decimal
    timestamp: datetime
```

## Dependency Injection

### Container Architecture

```python
# Composition Root Pattern
CompositionRoot
    │
    ├── configure()
    │     │
    │     ├── Register Domain Services
    │     ├── Register Application Services
    │     ├── Register Infrastructure (future)
    │     └── Register Presentation (future)
    │
    └── DIContainer
          ├── Singleton lifetime
          ├── Scoped lifetime
          └── Transient lifetime
```

### Service Registration Example

```python
# Domain services (Singleton - stateless)
container.register_singleton(
    PortfolioCalculationService,
    factory=lambda: PortfolioCalculationService()
)

# Application services (Scoped - per request)
container.register_scoped(
    StockApplicationService,
    factory=lambda c: StockApplicationService(
        stock_repository=c.resolve(IStockRepository)
    )
)
```

### Lifetime Management

- **Singleton**: One instance for application lifetime (domain services)
- **Scoped**: One instance per request/operation (application services)
- **Transient**: New instance every time (DTOs, commands)

## Testing Strategy

### Test Organization

```
tests/
├── domain/                 # Pure unit tests
│   ├── entities/          # Entity behavior tests
│   ├── value_objects/     # Value object validation
│   └── services/          # Domain service tests
├── application/           # Application layer tests
│   ├── services/         # Use case tests
│   └── commands/         # Command validation
└── dependency_injection/  # Container tests
```

### Layer-Specific Coverage Requirements

| Layer | Coverage | Enforcement |
|-------|----------|-------------|
| Domain | 100% | Enforced by pre-commit hooks |
| Application | 90% | Enforced by pre-commit hooks |
| Infrastructure | 100% | Will be enforced when implemented |
| Presentation | 100% | Will be enforced when implemented |

### Testing Principles

1. **Test-Driven Development (TDD)**
   - Write tests first
   - Tests define behavior
   - Refactor with confidence

2. **Isolation**
   - Each layer tested independently
   - Mock external dependencies
   - No database in unit tests

3. **Comprehensive Coverage**
   - Happy path scenarios
   - Edge cases
   - Error conditions
   - Business rule validation

## Current Implementation Status

### ✅ Completed Components

**Domain Layer**
- All core entities (Stock, Portfolio, Transaction, etc.)
- Comprehensive value objects
- Domain services with business logic
- Repository interfaces
- Domain event infrastructure

**Application Layer**
- Stock application service
- Command objects
- Data transfer objects
- Service orchestration

**Infrastructure**
- Dependency injection container
- Composition root
- Service lifetime management

**Development Tools**
- Pre-commit hooks
- Layer coverage enforcement
- Makefile automation
- Docker configuration

### 🚧 In Progress

Currently in Phase 1 of the development roadmap with focus on foundational infrastructure.

### 📋 Planned Components

**Infrastructure Layer** (Phase 2)
- SQLite/PostgreSQL repositories
- Database connection management
- Unit of Work pattern
- Data migrations

**Presentation Layer** (Phase 2)
- FastAPI REST API
- OpenAPI documentation
- Request/Response models
- Authentication middleware

## Future Architecture

### Phase 2: Infrastructure & API

```
Infrastructure Implementation:
├── SQLAlchemy Integration
│   ├── Table definitions
│   ├── Repository implementations
│   └── Unit of Work pattern
├── Database Management
│   ├── Connection pooling
│   ├── Transaction handling
│   └── Migration system
└── External Services
    ├── Stock price API integration
    ├── Email notifications
    └── Export services
```

### Phase 3: Advanced Features

```
Advanced Architecture:
├── Event Sourcing (optional)
│   ├── Event store
│   ├── Projections
│   └── Event replay
├── CQRS Pattern
│   ├── Command handlers
│   ├── Query handlers
│   └── Read models
└── Microservices Ready
    ├── Service boundaries
    ├── Message bus
    └── API gateway
```

### Scalability Considerations

1. **Horizontal Scaling**
   - Stateless services
   - Database read replicas
   - Caching layer

2. **Performance Optimization**
   - Query optimization
   - Lazy loading
   - Response caching

3. **Monitoring & Observability**
   - Structured logging
   - Metrics collection
   - Distributed tracing

## Architecture Decision Records (ADRs)

### ADR-001: Clean Architecture
- **Decision**: Use Clean Architecture with explicit layers
- **Rationale**: Provides clear boundaries and testability
- **Consequences**: More initial setup but better maintainability

### ADR-002: Domain-Driven Design
- **Decision**: Rich domain model with business logic in entities
- **Rationale**: Complex business rules need proper encapsulation
- **Consequences**: More complex than anemic models but more maintainable

### ADR-003: Dependency Injection
- **Decision**: Custom DI container with composition root
- **Rationale**: Full control over service lifetime and registration
- **Consequences**: More code but better testability and flexibility

### ADR-004: Test-First Development
- **Decision**: Mandatory TDD with 100% domain coverage
- **Rationale**: Critical business logic must be reliable
- **Consequences**: Slower initial development but fewer bugs