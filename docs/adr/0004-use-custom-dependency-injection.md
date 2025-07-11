# Use Custom Dependency Injection Container

* Status: accepted
* Deciders: Development team
* Date: 2025-01-11

## Context and Problem Statement

StockBook's Clean Architecture requires careful management of dependencies between layers. We need a mechanism to wire up dependencies at runtime while maintaining the dependency inversion principle. The solution must support different object lifetimes (singleton, scoped, transient) and enable easy testing through dependency substitution. What dependency injection approach should we use to manage object creation and lifetime while keeping our architecture clean and testable?

## Decision Drivers

* **Clean Architecture Compliance**: Must support dependency inversion principle
* **Lifetime Management**: Need to control when objects are created and destroyed
* **Testing Support**: Easy substitution of dependencies for testing
* **Type Safety**: Full static typing support with mypy/pyright
* **Performance**: Minimal overhead for object resolution
* **Simplicity**: Solution should be understandable and maintainable
* **Framework Independence**: Avoid tight coupling to web frameworks

## Considered Options

* **Custom DI Container**: Build our own lightweight container
* **FastAPI Dependency Injection**: Use FastAPI's built-in DI system
* **Python Dependency Injector**: Third-party DI framework
* **Constructor Injection Only**: Manual dependency wiring
* **Service Locator Pattern**: Global registry of services
* **Factory Pattern**: Use factories for object creation

## Decision Outcome

Chosen option: "Custom DI Container", because it gives us full control over service lifetimes and registration while keeping the solution lightweight and tailored to our needs. This approach ensures we're not coupled to any framework and can maintain clean boundaries between layers.

### Positive Consequences

* **Full Control**: Complete control over registration and resolution logic
* **Lifetime Management**: Explicit singleton, scoped, and transient lifetimes
* **Framework Independence**: Not tied to FastAPI or any other framework
* **Type Safety**: Can be made fully type-safe with proper annotations
* **Testability**: Easy to create test containers with mock dependencies
* **Composition Root Pattern**: Clear single point of dependency configuration
* **Performance**: Optimized for our specific needs

### Negative Consequences

* **More Code**: Need to implement and maintain the container
* **No Advanced Features**: Missing features like auto-wiring or decorators
* **Learning Curve**: Team needs to understand our custom implementation
* **Documentation Burden**: Must document our own solution

## Pros and Cons of the Options

### Custom DI Container

Build a lightweight container tailored to our specific needs.

* Good, because we have full control over implementation
* Good, because can optimize for our use cases
* Good, because maintains framework independence
* Good, because supports all required lifetimes
* Good, because can ensure type safety
* Bad, because requires implementation effort
* Bad, because team must learn custom solution

### FastAPI Dependency Injection

Use FastAPI's built-in Depends() system.

* Good, because already integrated with our web framework
* Good, because well-documented and supported
* Good, because handles scoped dependencies automatically
* Bad, because couples domain/application layers to FastAPI
* Bad, because limited to request scope
* Bad, because difficult to use outside HTTP context
* Bad, because violates Clean Architecture principles

### Python Dependency Injector

Use the popular third-party dependency-injector library.

* Good, because feature-rich and mature
* Good, because supports advanced patterns
* Good, because well-documented
* Bad, because adds external dependency
* Bad, because more complex than needed
* Bad, because learning curve for advanced features
* Bad, because potential version conflicts

### Constructor Injection Only

Manually wire dependencies in constructors without a container.

* Good, because simple and explicit
* Good, because no magic or hidden behavior
* Good, because fully type-safe
* Bad, because repetitive boilerplate code
* Bad, because difficult to manage complex graphs
* Bad, because no lifetime management
* Bad, because testing requires manual wiring

### Service Locator Pattern

Global registry where services can be looked up.

* Good, because simple to implement
* Good, because easy to understand
* Bad, because hides dependencies
* Bad, because makes testing harder
* Bad, because considered an anti-pattern
* Bad, because reduces code clarity

### Factory Pattern

Use factory classes to create objects with dependencies.

* Good, because explicit and type-safe
* Good, because no framework needed
* Bad, because proliferation of factory classes
* Bad, because no centralized configuration
* Bad, because manual lifetime management

## Implementation Details

Our custom DI container implementation includes:

### Core Components

#### 1. DIContainer Class
```python
class DIContainer:
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
        self._scoped: Dict[Type, Any] = {}
    
    def register_singleton(self, service_type: Type[T], 
                         factory: Callable[[DIContainer], T]) -> None:
        """Register a service with singleton lifetime"""
        
    def register_scoped(self, service_type: Type[T], 
                       factory: Callable[[DIContainer], T]) -> None:
        """Register a service with scoped lifetime"""
        
    def register_transient(self, service_type: Type[T], 
                          factory: Callable[[DIContainer], T]) -> None:
        """Register a service with transient lifetime"""
        
    def resolve(self, service_type: Type[T]) -> T:
        """Resolve a service instance"""
```

#### 2. Service Lifetimes

**Singleton**: One instance for the entire application lifetime
- Domain services (stateless business logic)
- Configuration objects
- Shared resources

**Scoped**: One instance per request/operation
- Application services
- Unit of Work
- Request-specific context

**Transient**: New instance every time
- Commands and queries
- DTOs
- Temporary objects

#### 3. Composition Root Pattern
```python
class CompositionRoot:
    @staticmethod
    def configure(container: DIContainer) -> None:
        # Domain Services (Singleton)
        container.register_singleton(
            SectorIndustryService,
            factory=lambda c: SectorIndustryService()
        )
        
        container.register_singleton(
            PortfolioCalculationService,
            factory=lambda c: PortfolioCalculationService()
        )
        
        # Repositories (Scoped)
        container.register_scoped(
            IStockRepository,
            factory=lambda c: StockRepository(
                session_factory=c.resolve(SessionFactory)
            )
        )
        
        # Application Services (Scoped)
        container.register_scoped(
            StockApplicationService,
            factory=lambda c: StockApplicationService(
                stock_repository=c.resolve(IStockRepository),
                unit_of_work=c.resolve(IUnitOfWork)
            )
        )
```

#### 4. Scope Management
```python
class Scope:
    def __init__(self, container: DIContainer):
        self._container = container
        
    def __enter__(self):
        self._container.begin_scope()
        return self._container
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._container.end_scope()

# Usage in FastAPI
@app.post("/stocks")
async def create_stock(request: CreateStockRequest):
    with Scope(container) as scoped_container:
        service = scoped_container.resolve(StockApplicationService)
        return await service.create_stock(request)
```

### Testing Support

```python
# Test container with mocks
def create_test_container() -> DIContainer:
    container = DIContainer()
    
    # Register mock repository
    container.register_singleton(
        IStockRepository,
        factory=lambda c: MockStockRepository()
    )
    
    # Register real service with mock dependency
    container.register_scoped(
        StockApplicationService,
        factory=lambda c: StockApplicationService(
            stock_repository=c.resolve(IStockRepository)
        )
    )
    
    return container
```

### Integration Points

1. **FastAPI Integration**: Minimal coupling through request handlers
2. **Database Sessions**: Scoped lifetime for database connections
3. **Background Tasks**: Separate scope for async operations
4. **Testing**: Easy substitution of dependencies

## Links

* Implements [ADR-0002: Use Clean Architecture](0002-use-clean-architecture.md)
* Works with [ADR-0003: Implement Domain-Driven Design](0003-implement-domain-driven-design.md)
* References: "Dependency Injection Principles, Practices, and Patterns" by Steven van Deursen and Mark Seemann
* References: "Clean Architecture" by Robert C. Martin