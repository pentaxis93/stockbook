# Use Unit of Work Pattern for Transaction Management

* Status: accepted
* Deciders: Development team
* Date: 2025-01-11

## Context and Problem Statement

StockBook requires coordinated transactions across multiple repositories when handling complex business operations. For example, creating a transaction might require updating the portfolio, recording the transaction, and updating aggregate calculations. These operations must succeed or fail as a unit to maintain data consistency. We need a pattern that manages database transactions across multiple repository operations while keeping the domain layer unaware of transaction management details. How should we handle transaction boundaries and ensure data consistency across multiple repository operations?

## Decision Drivers

* **Transactional Consistency**: Multiple operations must succeed or fail together
* **Repository Coordination**: Need to share database sessions across repositories
* **Domain Ignorance**: Domain layer should not manage transactions
* **Testability**: Must be able to test transactional behavior
* **Performance**: Minimize database round trips and connection overhead
* **Error Handling**: Clear rollback semantics on failures
* **Clean Architecture**: Transaction management is an infrastructure concern

## Considered Options

* **Unit of Work Pattern**: Centralized transaction management with repository registry
* **Repository Transactions**: Each repository manages its own transactions
* **Service-Level Transactions**: Application services manage transaction boundaries
* **Aspect-Oriented Transactions**: Decorators/aspects for transaction management
* **Event Sourcing**: Store events instead of state changes
* **No Explicit Transactions**: Rely on database auto-commit

## Decision Outcome

Chosen option: "Unit of Work Pattern", because it provides a clean abstraction for transaction management that aligns perfectly with our Clean Architecture. It centralizes transaction control, ensures all repositories within a business operation share the same database session, and provides clear commit/rollback semantics while keeping the domain layer pure.

### Positive Consequences

* **Atomic Operations**: All changes within a unit succeed or fail together
* **Session Management**: Repositories automatically share database sessions
* **Clean Abstraction**: Transaction details hidden from domain and application layers
* **Testability**: Easy to mock for testing without database
* **Performance**: Single connection/transaction for multiple operations
* **Explicit Boundaries**: Clear transaction scope in application services
* **Error Recovery**: Automatic rollback on exceptions

### Negative Consequences

* **Additional Abstraction**: One more layer to understand and maintain
* **Complexity**: Need to manage repository registry within UoW
* **Learning Curve**: Developers must understand the pattern
* **Potential for Misuse**: Long-running transactions if not careful

## Pros and Cons of the Options

### Unit of Work Pattern

Maintains a list of objects affected by a business transaction and coordinates writing out changes.

* Good, because provides transactional consistency
* Good, because centralizes transaction management
* Good, because aligns with Domain-Driven Design
* Good, because repositories share the same session
* Good, because clear commit/rollback semantics
* Good, because supports the repository pattern well
* Bad, because adds complexity
* Bad, because requires careful lifecycle management

### Repository Transactions

Each repository manages its own transaction boundaries.

* Good, because simple to implement
* Good, because repositories are self-contained
* Bad, because no coordination between repositories
* Bad, because can't have atomic operations across repositories
* Bad, because leads to inconsistent data
* Bad, because violates single responsibility
* Bad, because complex operations need distributed transactions

### Service-Level Transactions

Application services directly manage database transactions.

* Good, because explicit transaction control
* Good, because flexible transaction boundaries
* Bad, because couples application layer to infrastructure
* Bad, because transaction code scattered across services
* Bad, because violates Clean Architecture
* Bad, because hard to test without database

### Aspect-Oriented Transactions

Use decorators or aspects to add transactional behavior.

* Good, because declarative transaction management
* Good, because keeps business logic clean
* Good, because familiar from Spring/Java
* Bad, because implicit behavior (magic)
* Bad, because harder to debug
* Bad, because Python decorator limitations
* Bad, because complex transaction propagation

### Event Sourcing

Store domain events instead of current state.

* Good, because natural transaction boundaries
* Good, because complete audit trail
* Good, because supports event-driven architecture
* Bad, because significant complexity increase
* Bad, because requires event store infrastructure
* Bad, because steep learning curve
* Bad, because overkill for current needs

### No Explicit Transactions

Rely on database auto-commit for each operation.

* Good, because simplest approach
* Good, because no transaction management needed
* Bad, because no atomicity across operations
* Bad, because data inconsistency risks
* Bad, because poor performance (multiple commits)
* Bad, because no rollback capability

## Implementation Details

Our Unit of Work implementation includes:

### Domain Interface

```python
# src/domain/repositories/i_unit_of_work.py
from abc import ABC, abstractmethod
from typing import TypeVar, Type, ContextManager

T = TypeVar('T')

class IUnitOfWork(ABC):
    """
    Unit of Work pattern interface.
    Manages transactions and provides access to repositories.
    """
    
    @abstractmethod
    async def __aenter__(self) -> 'IUnitOfWork':
        """Begin a unit of work (start transaction)."""
        pass
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """End unit of work (commit or rollback)."""
        pass
    
    @abstractmethod
    async def commit(self) -> None:
        """Explicitly commit the transaction."""
        pass
    
    @abstractmethod
    async def rollback(self) -> None:
        """Explicitly rollback the transaction."""
        pass
    
    @abstractmethod
    def repository(self, repository_type: Type[T]) -> T:
        """Get a repository instance within this unit of work."""
        pass
```

### Infrastructure Implementation

```python
# src/infrastructure/persistence/unit_of_work.py
from typing import Dict, Type, Any
from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction

from src.domain.repositories import (
    IUnitOfWork, IStockRepository, IPortfolioRepository,
    ITransactionRepository
)
from src.infrastructure.repositories import (
    StockRepository, PortfolioRepository, TransactionRepository
)

class SqlAlchemyUnitOfWork(IUnitOfWork):
    """SQLAlchemy implementation of Unit of Work pattern."""
    
    def __init__(self, session_factory):
        self._session_factory = session_factory
        self._session: Optional[AsyncSession] = None
        self._transaction: Optional[AsyncSessionTransaction] = None
        self._repositories: Dict[Type, Any] = {}
        self._repository_mapping = {
            IStockRepository: StockRepository,
            IPortfolioRepository: PortfolioRepository,
            ITransactionRepository: TransactionRepository,
        }
    
    async def __aenter__(self) -> 'SqlAlchemyUnitOfWork':
        """Start a new database session and transaction."""
        self._session = self._session_factory()
        self._transaction = await self._session.begin()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Commit or rollback based on exception status."""
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        
        await self._session.close()
        self._repositories.clear()
    
    async def commit(self) -> None:
        """Commit the current transaction."""
        if self._transaction:
            await self._transaction.commit()
            self._transaction = None
    
    async def rollback(self) -> None:
        """Rollback the current transaction."""
        if self._transaction:
            await self._transaction.rollback()
            self._transaction = None
    
    def repository(self, repository_type: Type[T]) -> T:
        """
        Get or create a repository instance for this unit of work.
        All repositories share the same session.
        """
        if repository_type not in self._repositories:
            repo_class = self._repository_mapping.get(repository_type)
            if not repo_class:
                raise ValueError(f"No mapping for repository type: {repository_type}")
            
            self._repositories[repository_type] = repo_class(self._session)
        
        return self._repositories[repository_type]
```

### Usage in Application Services

```python
# src/application/services/portfolio_service.py
class PortfolioApplicationService:
    def __init__(self, unit_of_work: IUnitOfWork):
        self._uow = unit_of_work
    
    async def execute_transaction(
        self, 
        command: ExecuteTransactionCommand
    ) -> TransactionDTO:
        """
        Execute a stock transaction within a unit of work.
        All operations succeed or fail together.
        """
        async with self._uow:
            # Get repositories within the same UoW
            portfolio_repo = self._uow.repository(IPortfolioRepository)
            transaction_repo = self._uow.repository(ITransactionRepository)
            stock_repo = self._uow.repository(IStockRepository)
            
            # Load entities
            portfolio = await portfolio_repo.find_by_id(command.portfolio_id)
            if not portfolio:
                raise PortfolioNotFoundError(command.portfolio_id)
            
            stock = await stock_repo.find_by_id(command.stock_id)
            if not stock:
                raise StockNotFoundError(command.stock_id)
            
            # Create and execute transaction
            transaction = Transaction.create(
                portfolio_id=portfolio.id,
                stock_id=stock.id,
                transaction_type=command.transaction_type,
                quantity=command.quantity,
                price=command.price,
                date=command.date
            )
            
            # Update portfolio (domain logic)
            portfolio.add_transaction(transaction)
            
            # Persist changes (all in same transaction)
            await transaction_repo.save(transaction)
            await portfolio_repo.save(portfolio)
            
            # If any operation fails, all changes are rolled back
            
        return TransactionDTO.from_domain(transaction)
```

### Testing Unit of Work

```python
# tests/mocks/mock_unit_of_work.py
class MockUnitOfWork(IUnitOfWork):
    """Mock implementation for testing."""
    
    def __init__(self):
        self.committed = False
        self.rolled_back = False
        self._repositories = {}
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
    
    async def commit(self):
        self.committed = True
    
    async def rollback(self):
        self.rolled_back = True
    
    def repository(self, repository_type: Type[T]) -> T:
        if repository_type not in self._repositories:
            if repository_type == IStockRepository:
                self._repositories[repository_type] = MockStockRepository()
            elif repository_type == IPortfolioRepository:
                self._repositories[repository_type] = MockPortfolioRepository()
            # Add other mock repositories
        
        return self._repositories[repository_type]

# Test example
@pytest.mark.asyncio
async def test_transaction_rollback_on_error():
    # Arrange
    uow = MockUnitOfWork()
    service = PortfolioApplicationService(uow)
    
    # Setup mock to raise error
    mock_portfolio_repo = uow.repository(IPortfolioRepository)
    mock_portfolio_repo.save = AsyncMock(
        side_effect=Exception("Database error")
    )
    
    # Act & Assert
    with pytest.raises(Exception):
        await service.execute_transaction(command)
    
    assert uow.rolled_back
    assert not uow.committed
```

### Advanced Patterns

#### Nested Unit of Work

```python
class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory):
        self._session_factory = session_factory
        self._session = None
        self._savepoint = None
    
    async def begin_nested(self) -> 'SqlAlchemyUnitOfWork':
        """Start a nested transaction (savepoint)."""
        if not self._session:
            raise RuntimeError("Cannot create nested UoW without active session")
        
        self._savepoint = await self._session.begin_nested()
        return self
```

#### Unit of Work with Events

```python
class EventCollectingUnitOfWork(SqlAlchemyUnitOfWork):
    """Collects domain events during the unit of work."""
    
    def __init__(self, session_factory, event_dispatcher):
        super().__init__(session_factory)
        self._event_dispatcher = event_dispatcher
        self._collected_events = []
    
    def collect_event(self, event: DomainEvent) -> None:
        """Collect domain event to be dispatched after commit."""
        self._collected_events.append(event)
    
    async def commit(self) -> None:
        """Commit transaction and dispatch collected events."""
        await super().commit()
        
        # Dispatch events only after successful commit
        for event in self._collected_events:
            await self._event_dispatcher.dispatch(event)
        
        self._collected_events.clear()
```

### Configuration in DI Container

```python
# src/infrastructure/di/composition_root.py
def configure_infrastructure(container: DIContainer) -> None:
    # Register session factory
    container.register_singleton(
        AsyncSessionFactory,
        factory=lambda: create_async_session_factory(settings.database_url)
    )
    
    # Register Unit of Work
    container.register_scoped(
        IUnitOfWork,
        factory=lambda c: SqlAlchemyUnitOfWork(
            session_factory=c.resolve(AsyncSessionFactory)
        )
    )
    
    # Application services use UoW
    container.register_scoped(
        PortfolioApplicationService,
        factory=lambda c: PortfolioApplicationService(
            unit_of_work=c.resolve(IUnitOfWork)
        )
    )
```

## Links

* Complements [ADR-0008: Repository Pattern](0008-repository-pattern.md)
* Implements [ADR-0002: Use Clean Architecture](0002-use-clean-architecture.md)
* Supports [ADR-0003: Implement Domain-Driven Design](0003-implement-domain-driven-design.md)
* References: "Patterns of Enterprise Application Architecture" by Martin Fowler
* References: "Implementing Domain-Driven Design" by Vaughn Vernon