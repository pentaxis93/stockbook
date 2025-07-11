# Use Clean Architecture

* Status: accepted
* Deciders: Development team
* Date: 2025-01-11

## Context and Problem Statement

StockBook is a financial portfolio management application that requires handling complex business logic, multiple data sources, and various user interfaces. We need an architectural pattern that ensures maintainability, testability, and the ability to evolve the application over time without tight coupling between components. How should we structure our application to achieve these goals while maintaining clear separation of concerns?

## Decision Drivers

* **Business Logic Isolation**: Core business rules must be independent of frameworks, databases, and UI
* **Testability**: Each component must be easily testable in isolation
* **Maintainability**: Clear boundaries between concerns to make changes predictable and safe
* **Framework Independence**: Ability to change frameworks or external tools without affecting business logic
* **Scalability**: Architecture must support future growth in features and complexity
* **Team Productivity**: Clear structure helps developers understand where code belongs

## Considered Options

* **Traditional Layered Architecture**: Simple layers (UI, Business, Data) with top-down dependencies
* **Clean Architecture**: Concentric layers with dependencies pointing inward toward the domain
* **Hexagonal Architecture (Ports and Adapters)**: Business logic at center with ports defining contracts
* **MVVM/MVC Pattern**: Model-View-Controller or Model-View-ViewModel patterns
* **Microservices Architecture**: Distributed services with independent deployments

## Decision Outcome

Chosen option: "Clean Architecture", because it provides the best balance of maintainability, testability, and flexibility for our needs. It enforces dependency rules that keep business logic pure and framework-agnostic while providing clear guidelines for organizing code.

### Positive Consequences

* **Pure Domain Logic**: Business rules are completely isolated from external concerns
* **High Testability**: Each layer can be tested independently with appropriate mocks
* **Framework Flexibility**: Can change web frameworks, databases, or other tools without touching business logic
* **Clear Code Organization**: Developers know exactly where each piece of code belongs
* **Dependency Rule Enforcement**: Dependencies only point inward, preventing coupling
* **Parallel Development**: Teams can work on different layers simultaneously

### Negative Consequences

* **Initial Complexity**: More setup required compared to simpler architectures
* **More Code**: Interfaces, DTOs, and mapping between layers add boilerplate
* **Learning Curve**: Team needs to understand the principles and boundaries
* **Potential Over-engineering**: For simple CRUD operations, the architecture might feel heavy

## Pros and Cons of the Options

### Traditional Layered Architecture

Simple three-tier architecture with Presentation, Business Logic, and Data Access layers.

* Good, because simple to understand and implement
* Good, because familiar to most developers
* Bad, because business logic often becomes coupled to infrastructure
* Bad, because difficult to test business logic in isolation
* Bad, because changes in one layer often cascade to others

### Clean Architecture

Concentric layers with Domain at the center, surrounded by Application, Infrastructure, and Presentation layers.

* Good, because enforces dependency inversion principle
* Good, because business logic is completely isolated
* Good, because highly testable with clear boundaries
* Good, because supports Test-Driven Development naturally
* Bad, because requires more initial setup and planning
* Bad, because can lead to duplication between DTOs and domain models

### Hexagonal Architecture (Ports and Adapters)

Business logic at center with ports (interfaces) and adapters (implementations) for external concerns.

* Good, because very similar benefits to Clean Architecture
* Good, because explicit ports make integration points clear
* Bad, because terminology can be confusing (what's a port vs adapter?)
* Bad, because less community adoption than Clean Architecture

### MVVM/MVC Pattern

Model-View patterns focusing on separation of presentation concerns.

* Good, because well-understood patterns with good tooling support
* Good, because works well for UI-heavy applications
* Bad, because doesn't address infrastructure concerns well
* Bad, because business logic often leaks into controllers/view models
* Bad, because not sufficient for complex domain logic

### Microservices Architecture

Distributed services each handling specific business capabilities.

* Good, because allows independent deployment and scaling
* Good, because technology diversity per service
* Bad, because adds significant operational complexity
* Bad, because network latency and distributed system challenges
* Bad, because overkill for our current scale and team size

## Implementation Details

Our Clean Architecture implementation consists of four main layers:

### 1. Domain Layer (Innermost)
* **Purpose**: Core business logic and rules
* **Components**: Entities, Value Objects, Domain Services, Repository Interfaces
* **Dependencies**: None
* **Example**: Stock entity with business rules for valid symbols and sectors

### 2. Application Layer
* **Purpose**: Use case orchestration and application-specific logic
* **Components**: Application Services, Commands, Queries, DTOs
* **Dependencies**: Domain layer only
* **Example**: StockApplicationService coordinating stock creation

### 3. Infrastructure Layer
* **Purpose**: External concerns and technical details
* **Components**: Repository implementations, Database access, External services
* **Dependencies**: Domain layer (implements interfaces)
* **Example**: SQLAlchemy repository implementing IStockRepository

### 4. Presentation Layer (Outermost)
* **Purpose**: User interface and API endpoints
* **Components**: Controllers, View Models, API routing
* **Dependencies**: Application layer only
* **Example**: FastAPI endpoints for stock management

## Links

* Refined by [ADR-0003: Implement Domain-Driven Design](0003-implement-domain-driven-design.md)
* Refined by [ADR-0004: Use Dependency Injection](0004-use-dependency-injection.md)
* References: "Clean Architecture" by Robert C. Martin
* References: "Domain-Driven Design" by Eric Evans