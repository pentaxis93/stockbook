# Use Composition Root Pattern

* Status: accepted
* Deciders: Development team
* Date: 2025-01-11

## Context and Problem Statement

StockBook uses dependency injection to manage object creation and dependencies, but we need a pattern for configuring the DI container itself. The configuration should happen in a single, well-defined location to maintain clarity about how the application is wired together. We need to decide where and how to compose the object graph for our application. Where should we configure our dependency injection container and how should we structure this configuration?

## Decision Drivers

* **Single Source of Truth**: All DI configuration in one place
* **Early Validation**: Detect misconfiguration at startup, not runtime
* **Testability**: Easy to create test configurations
* **Modularity**: Support modular registration by layer
* **Clear Dependencies**: Make the dependency graph visible
* **Framework Independence**: Don't scatter DI configuration throughout the codebase
* **Environment Flexibility**: Support different configurations for different environments

## Considered Options

* **Composition Root Pattern**: Single point of configuration at application entry
* **Module-Based Registration**: Each module registers its own dependencies
* **Attribute-Based Registration**: Use decorators/attributes for registration
* **Configuration Files**: XML/JSON/YAML-based DI configuration
* **Auto-Discovery**: Scan and auto-register based on conventions
* **Distributed Registration**: Register dependencies where they're defined

## Decision Outcome

Chosen option: "Composition Root Pattern", because it provides a single, clear location where the entire object graph is composed. This pattern makes dependencies explicit, enables early validation of the configuration, and keeps the DI configuration separate from business logic. It aligns perfectly with our Clean Architecture by keeping infrastructure concerns in the infrastructure layer.

### Positive Consequences

* **Single Configuration Point**: All DI wiring in one place
* **Early Error Detection**: Configuration errors caught at startup
* **Clear Dependency Graph**: Easy to understand object relationships
* **Test Isolation**: Simple to create test-specific configurations
* **Environment Support**: Easy per-environment configuration
* **Refactoring Safety**: Changes to DI are localized
* **Documentation**: Composition root serves as system documentation

### Negative Consequences

* **Large Configuration**: Can become large for complex applications
* **Central Coupling**: All modules known to composition root
* **Startup Performance**: All configuration happens at startup
* **Learning Curve**: Team must understand the pattern

## Pros and Cons of the Options

### Composition Root Pattern

Configure entire object graph at application entry point.

* Good, because single source of truth
* Good, because dependencies are explicit
* Good, because early validation possible
* Good, because supports different environments
* Good, because clear startup sequence
* Good, because testable configuration
* Bad, because can become large
* Bad, because central knowledge required

### Module-Based Registration

Each module provides its own registration logic.

* Good, because distributed knowledge
* Good, because modules are self-contained
* Good, because scales with modules
* Bad, because configuration scattered
* Bad, because harder to see full graph
* Bad, because circular dependencies possible
* Bad, because inconsistent patterns

### Attribute-Based Registration

Use decorators to mark classes for registration.

* Good, because declarative approach
* Good, because less configuration code
* Good, because co-located with classes
* Bad, because magic behavior
* Bad, because runtime scanning required
* Bad, because harder to test
* Bad, because couples to DI framework

### Configuration Files

Use external files for DI configuration.

* Good, because configuration separate from code
* Good, because runtime changes possible
* Good, because familiar from other frameworks
* Bad, because runtime errors
* Bad, because no type safety
* Bad, because verbose XML/JSON
* Bad, because refactoring issues

### Auto-Discovery

Automatically discover and register components.

* Good, because minimal configuration
* Good, because convention over configuration
* Bad, because implicit behavior
* Bad, because magic registration
* Bad, because harder to debug
* Bad, because performance overhead
* Bad, because less control

### Distributed Registration

Register dependencies near their definitions.

* Good, because local changes only
* Good, because no central file
* Bad, because configuration scattered
* Bad, because no single truth
* Bad, because harder to test
* Bad, because dependency cycles
* Bad, because startup order issues

## Implementation Details

Our Composition Root implementation:

### Main Composition Root

```python
# src/infrastructure/di/composition_root.py
from src.domain.repositories import (
    IStockRepository, IPortfolioRepository, ITransactionRepository, IUnitOfWork
)
from src.domain.services import (
    PortfolioCalculationService, RiskAssessmentService, SectorIndustryService
)
from src.application.services import (
    StockApplicationService, PortfolioApplicationService
)
from src.application.command_bus import CommandBus
from src.application.handlers import (
    CreateStockCommandHandler, ExecuteTransactionCommandHandler
)
from src.infrastructure.di.container import DIContainer
from src.infrastructure.persistence import (
    SqlAlchemyUnitOfWork, StockRepository, PortfolioRepository
)

class CompositionRoot:
    """
    The composition root where the entire object graph is composed.
    This is the only place where we use the new operator and configure dependencies.
    """
    
    @staticmethod
    def configure(
        container: DIContainer,
        settings: Settings,
        environment: str = "production"
    ) -> None:
        """Configure the DI container with all dependencies."""
        
        # Configure based on environment
        if environment == "production":
            CompositionRoot._configure_production(container, settings)
        elif environment == "test":
            CompositionRoot._configure_test(container, settings)
        else:
            raise ValueError(f"Unknown environment: {environment}")
    
    @staticmethod
    def _configure_production(container: DIContainer, settings: Settings) -> None:
        """Production configuration."""
        
        # Infrastructure
        CompositionRoot._configure_infrastructure(container, settings)
        
        # Domain
        CompositionRoot._configure_domain(container)
        
        # Application
        CompositionRoot._configure_application(container)
        
        # Presentation
        CompositionRoot._configure_presentation(container)
        
        # Verify configuration
        CompositionRoot._verify_configuration(container)
    
    @staticmethod
    def _configure_infrastructure(container: DIContainer, settings: Settings) -> None:
        """Configure infrastructure layer."""
        
        # Database
        container.register_singleton(
            AsyncSessionFactory,
            factory=lambda: create_async_session_factory(settings.database_url)
        )
        
        # Unit of Work
        container.register_scoped(
            IUnitOfWork,
            factory=lambda c: SqlAlchemyUnitOfWork(
                session_factory=c.resolve(AsyncSessionFactory),
                event_publisher=c.resolve(IEventPublisher)
            )
        )
        
        # Event Publisher
        container.register_singleton(
            IEventPublisher,
            factory=lambda: InMemoryEventBus()
        )
    
    @staticmethod
    def _configure_domain(container: DIContainer) -> None:
        """Configure domain layer services."""
        
        # Domain Services (Singleton - stateless)
        container.register_singleton(
            SectorIndustryService,
            factory=lambda: SectorIndustryService()
        )
        
        container.register_singleton(
            PortfolioCalculationService,
            factory=lambda: PortfolioCalculationService()
        )
        
        container.register_singleton(
            RiskAssessmentService,
            factory=lambda: RiskAssessmentService()
        )
    
    @staticmethod
    def _configure_application(container: DIContainer) -> None:
        """Configure application layer."""
        
        # Command Bus
        container.register_singleton(
            CommandBus,
            factory=lambda: CompositionRoot._create_command_bus(container)
        )
        
        # Application Services (Scoped - per request)
        container.register_scoped(
            StockApplicationService,
            factory=lambda c: StockApplicationService(
                unit_of_work=c.resolve(IUnitOfWork),
                command_bus=c.resolve(CommandBus)
            )
        )
        
        container.register_scoped(
            PortfolioApplicationService,
            factory=lambda c: PortfolioApplicationService(
                unit_of_work=c.resolve(IUnitOfWork),
                portfolio_calculator=c.resolve(PortfolioCalculationService),
                risk_assessor=c.resolve(RiskAssessmentService)
            )
        )
    
    @staticmethod
    def _create_command_bus(container: DIContainer) -> CommandBus:
        """Create and configure command bus with handlers."""
        bus = CommandBus()
        
        # Register command handlers
        bus.register_handler(
            CreateStockCommand,
            CreateStockCommandHandler(
                unit_of_work=container.resolve(IUnitOfWork),
                event_publisher=container.resolve(IEventPublisher)
            )
        )
        
        bus.register_handler(
            ExecuteTransactionCommand,
            ExecuteTransactionCommandHandler(
                unit_of_work=container.resolve(IUnitOfWork),
                event_publisher=container.resolve(IEventPublisher)
            )
        )
        
        return bus
    
    @staticmethod
    def _configure_presentation(container: DIContainer) -> None:
        """Configure presentation layer dependencies."""
        
        # API Dependencies
        container.register_factory(
            "current_user",
            factory=lambda c: get_current_user,
            lifetime=ServiceLifetime.SCOPED
        )
    
    @staticmethod
    def _verify_configuration(container: DIContainer) -> None:
        """Verify that all dependencies can be resolved."""
        required_services = [
            IUnitOfWork,
            StockApplicationService,
            PortfolioApplicationService,
            CommandBus
        ]
        
        for service_type in required_services:
            try:
                # Try to resolve in a test scope
                with container.create_scope() as scope:
                    scope.resolve(service_type)
            except Exception as e:
                raise ConfigurationError(
                    f"Failed to resolve {service_type.__name__}: {e}"
                )
```

### Test Configuration

```python
# src/infrastructure/di/test_composition_root.py
class TestCompositionRoot:
    """Composition root for test environment."""
    
    @staticmethod
    def configure_unit_tests(container: DIContainer) -> None:
        """Configure for unit tests with mocks."""
        
        # Mock infrastructure
        container.register_singleton(
            IUnitOfWork,
            factory=lambda: MockUnitOfWork()
        )
        
        container.register_singleton(
            IEventPublisher,
            factory=lambda: MockEventPublisher()
        )
        
        # Real domain services
        CompositionRoot._configure_domain(container)
        
        # Real application services with mock dependencies
        CompositionRoot._configure_application(container)
    
    @staticmethod
    def configure_integration_tests(container: DIContainer, test_db_url: str) -> None:
        """Configure for integration tests with real database."""
        
        # Test database
        container.register_singleton(
            AsyncSessionFactory,
            factory=lambda: create_async_session_factory(test_db_url)
        )
        
        # Real services
        settings = Settings(database_url=test_db_url)
        CompositionRoot._configure_production(container, settings)
```

### Application Entry Point

```python
# src/main.py
from fastapi import FastAPI
from src.infrastructure.di import DIContainer, CompositionRoot
from src.config import Settings

def create_app(settings: Settings = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    
    if settings is None:
        settings = Settings()
    
    # Create DI container
    container = DIContainer()
    
    # Configure dependencies at the composition root
    CompositionRoot.configure(
        container=container,
        settings=settings,
        environment=settings.environment
    )
    
    # Create FastAPI app
    app = FastAPI(
        title="StockBook API",
        version="1.0.0"
    )
    
    # Store container in app state
    app.state.container = container
    
    # Register routes
    register_routes(app, container)
    
    # Register middleware
    register_middleware(app, container)
    
    return app

# Application startup
if __name__ == "__main__":
    import uvicorn
    
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Modular Configuration

```python
# src/infrastructure/di/modules/infrastructure_module.py
class InfrastructureModule:
    """Infrastructure layer DI configuration."""
    
    @staticmethod
    def configure(container: DIContainer, settings: Settings) -> None:
        """Configure infrastructure dependencies."""
        
        # Database
        container.register_singleton(
            AsyncSessionFactory,
            factory=lambda: create_async_session_factory(settings.database_url)
        )
        
        # Caching
        if settings.redis_url:
            container.register_singleton(
                ICache,
                factory=lambda: RedisCache(settings.redis_url)
            )
        else:
            container.register_singleton(
                ICache,
                factory=lambda: InMemoryCache()
            )

# Usage in composition root
class CompositionRoot:
    @staticmethod
    def configure(container: DIContainer, settings: Settings) -> None:
        """Modular configuration."""
        
        # Configure each module
        InfrastructureModule.configure(container, settings)
        DomainModule.configure(container, settings)
        ApplicationModule.configure(container, settings)
        PresentationModule.configure(container, settings)
```

### FastAPI Integration

```python
# src/presentation/api/dependencies.py
from fastapi import Depends, Request

def get_container(request: Request) -> DIContainer:
    """Get DI container from request."""
    return request.app.state.container

def get_scoped_container(
    request: Request,
    container: DIContainer = Depends(get_container)
) -> DIContainer:
    """Get scoped container for request."""
    # Create request scope
    scope = container.create_scope()
    # Store in request state for cleanup
    request.state.di_scope = scope
    return scope

def get_stock_service(
    container: DIContainer = Depends(get_scoped_container)
) -> StockApplicationService:
    """Get stock application service."""
    return container.resolve(StockApplicationService)

# Usage in routes
@router.post("/stocks")
async def create_stock(
    request: CreateStockRequest,
    service: StockApplicationService = Depends(get_stock_service)
) -> StockResponse:
    """Create a new stock."""
    dto = await service.create_stock(request)
    return StockResponse.from_dto(dto)
```

## Links

* Implements [ADR-0004: Custom Dependency Injection](0004-use-custom-dependency-injection.md)
* Supports [ADR-0002: Use Clean Architecture](0002-use-clean-architecture.md)
* References: "Dependency Injection Principles, Practices, and Patterns" by Steven van Deursen and Mark Seemann
* References: "Clean Architecture" by Robert C. Martin