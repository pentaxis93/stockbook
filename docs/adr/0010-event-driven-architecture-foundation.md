# Event-Driven Architecture Foundation

* Status: accepted
* Deciders: Development team
* Date: 2025-01-11

## Context and Problem Statement

StockBook needs to handle complex workflows that span multiple bounded contexts and trigger side effects like notifications, audit logging, and cache invalidation. As the system grows, we need a way to decouple components while maintaining consistency and enabling new features without modifying existing code. Domain events provide a foundation for future features like real-time updates, integration with external systems, and event sourcing. How should we implement an event infrastructure that supports our current needs while enabling future architectural evolution?

## Decision Drivers

* **Loose Coupling**: Components should not directly depend on each other
* **Extensibility**: Add new features without modifying existing code
* **Audit Trail**: Natural history of what happened in the system
* **Future Readiness**: Foundation for event sourcing and CQRS if needed
* **Domain Focus**: Events should represent business occurrences
* **Testability**: Easy to test event publishing and handling
* **Performance**: Minimal overhead for synchronous operations

## Considered Options

* **Domain Events with In-Process Bus**: Synchronous event handling within the application
* **Message Queue Integration**: RabbitMQ/Kafka from the start
* **Observer Pattern**: Simple publish-subscribe implementation
* **No Events**: Direct method calls and tight coupling
* **Database Triggers**: Use database for event propagation
* **Full Event Sourcing**: Store events as primary source of truth

## Decision Outcome

Chosen option: "Domain Events with In-Process Bus", because it provides a solid foundation for event-driven architecture without the complexity of external message brokers. This approach allows us to implement domain events following DDD principles, with the flexibility to add asynchronous processing and external message queues later as the system scales.

### Positive Consequences

* **Clean Domain Model**: Events are first-class domain concepts
* **Incremental Adoption**: Can start simple and evolve
* **Easy Testing**: No external dependencies for unit tests
* **Performance**: No network overhead for local events
* **Future Migration Path**: Can add message queues later
* **Immediate Consistency**: Synchronous handling when needed
* **Clear Intent**: Events document what happened in business terms

### Negative Consequences

* **No Distribution**: Initially limited to single process
* **Synchronous Only**: No built-in async processing at start
* **Memory Pressure**: Events kept in memory during processing
* **No Persistence**: Events not stored by default

## Pros and Cons of the Options

### Domain Events with In-Process Bus

Implement domain events with a simple in-memory event bus for local handling.

* Good, because follows Domain-Driven Design principles
* Good, because simple to implement and understand
* Good, because no infrastructure dependencies
* Good, because can evolve to distributed system
* Good, because maintains transactional consistency
* Good, because easy to test
* Bad, because limited to single process initially
* Bad, because no built-in persistence

### Message Queue Integration

Use RabbitMQ, Kafka, or similar from the beginning.

* Good, because distributed from the start
* Good, because async processing built-in
* Good, because message persistence
* Good, because proven scalability
* Bad, because significant complexity overhead
* Bad, because requires infrastructure
* Bad, because harder to test
* Bad, because potential consistency issues

### Observer Pattern

Simple publish-subscribe without formal event infrastructure.

* Good, because very simple
* Good, because no dependencies
* Bad, because lacks structure
* Bad, because tight coupling through interfaces
* Bad, because no event history
* Bad, because hard to extend
* Bad, because not domain-focused

### No Events

Use direct method calls between components.

* Good, because simplest approach
* Good, because easiest to debug
* Bad, because tight coupling
* Bad, because hard to extend
* Bad, because no audit trail
* Bad, because violates Open-Closed Principle
* Bad, because difficult to test in isolation

### Database Triggers

Use database triggers to propagate changes.

* Good, because automatic propagation
* Good, because works across applications
* Bad, because logic hidden in database
* Bad, because hard to test
* Bad, because database vendor lock-in
* Bad, because violates Clean Architecture
* Bad, because poor visibility

### Full Event Sourcing

Store all changes as events, rebuild state from events.

* Good, because complete audit trail
* Good, because time travel debugging
* Good, because natural CQRS fit
* Bad, because significant complexity
* Bad, because requires event store
* Bad, because steep learning curve
* Bad, because overkill for current needs

## Implementation Details

Our event-driven architecture foundation includes:

### Domain Event Base

```python
# src/domain/events/base.py
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any
from uuid import UUID, uuid4

@dataclass(frozen=True)
class DomainEvent(ABC):
    """Base class for all domain events."""
    
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def event_type(self) -> str:
        """Return the event type name."""
        return self.__class__.__name__
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(),
            "data": self._event_data()
        }
    
    def _event_data(self) -> Dict[str, Any]:
        """Override to provide event-specific data."""
        return {}
```

### Domain Events

```python
# src/domain/events/stock_events.py
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from src.domain.events.base import DomainEvent

@dataclass(frozen=True)
class StockCreatedEvent(DomainEvent):
    """Raised when a new stock is created."""
    
    stock_id: UUID
    symbol: str
    company_name: str
    sector: str
    industry: str
    
    def _event_data(self) -> Dict[str, Any]:
        return {
            "stock_id": str(self.stock_id),
            "symbol": self.symbol,
            "company_name": self.company_name,
            "sector": self.sector,
            "industry": self.industry
        }

@dataclass(frozen=True)
class StockPriceUpdatedEvent(DomainEvent):
    """Raised when stock price is updated."""
    
    stock_id: UUID
    old_price: Decimal
    new_price: Decimal
    change_percentage: Decimal
    
    def _event_data(self) -> Dict[str, Any]:
        return {
            "stock_id": str(self.stock_id),
            "old_price": str(self.old_price),
            "new_price": str(self.new_price),
            "change_percentage": str(self.change_percentage)
        }

@dataclass(frozen=True)
class TransactionExecutedEvent(DomainEvent):
    """Raised when a stock transaction is executed."""
    
    transaction_id: UUID
    portfolio_id: UUID
    stock_id: UUID
    transaction_type: str  # BUY or SELL
    quantity: int
    price: Decimal
    total_amount: Decimal
```

### Event Publisher Interface

```python
# src/domain/events/i_event_publisher.py
from abc import ABC, abstractmethod
from typing import List

from src.domain.events.base import DomainEvent

class IEventPublisher(ABC):
    """Interface for publishing domain events."""
    
    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        """Publish a single event."""
        pass
    
    @abstractmethod
    def publish_batch(self, events: List[DomainEvent]) -> None:
        """Publish multiple events."""
        pass
```

### Event Handler Interface

```python
# src/domain/events/i_event_handler.py
from abc import ABC, abstractmethod
from typing import Type, TypeVar

from src.domain.events.base import DomainEvent

T = TypeVar('T', bound=DomainEvent)

class IEventHandler(ABC):
    """Interface for handling domain events."""
    
    @abstractmethod
    def handles(self) -> Type[DomainEvent]:
        """Return the event type this handler processes."""
        pass
    
    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """Process the event."""
        pass
```

### In-Memory Event Bus

```python
# src/infrastructure/events/in_memory_event_bus.py
from collections import defaultdict
from typing import List, Dict, Type

from src.domain.events import (
    DomainEvent, IEventPublisher, IEventHandler
)

class InMemoryEventBus(IEventPublisher):
    """In-memory implementation of event bus."""
    
    def __init__(self):
        self._handlers: Dict[Type[DomainEvent], List[IEventHandler]] = defaultdict(list)
    
    def register_handler(self, handler: IEventHandler) -> None:
        """Register an event handler."""
        event_type = handler.handles()
        self._handlers[event_type].append(handler)
    
    def publish(self, event: DomainEvent) -> None:
        """Publish event to all registered handlers."""
        handlers = self._handlers.get(type(event), [])
        for handler in handlers:
            # In production, consider async handling
            handler.handle(event)
    
    def publish_batch(self, events: List[DomainEvent]) -> None:
        """Publish multiple events."""
        for event in events:
            self.publish(event)
```

### Entity with Events

```python
# src/domain/entities/base.py
from typing import List

from src.domain.events.base import DomainEvent

class AggregateRoot:
    """Base class for aggregate roots that can raise events."""
    
    def __init__(self):
        self._domain_events: List[DomainEvent] = []
    
    def raise_event(self, event: DomainEvent) -> None:
        """Add a domain event to be published."""
        self._domain_events.append(event)
    
    def pull_events(self) -> List[DomainEvent]:
        """Get and clear pending events."""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events

# Example usage in Stock entity
class Stock(AggregateRoot):
    def __init__(self, symbol: StockSymbol, company: CompanyName, ...):
        super().__init__()
        self.symbol = symbol
        self.company = company
        
        # Raise creation event
        self.raise_event(StockCreatedEvent(
            stock_id=self.id,
            symbol=symbol.value,
            company_name=company.value,
            sector=self.sector.value,
            industry=self.industry.value
        ))
    
    def update_price(self, new_price: Money) -> None:
        """Update stock price and raise event."""
        old_price = self.price
        self.price = new_price
        
        change_percentage = ((new_price.amount - old_price.amount) 
                           / old_price.amount * 100)
        
        self.raise_event(StockPriceUpdatedEvent(
            stock_id=self.id,
            old_price=old_price.amount,
            new_price=new_price.amount,
            change_percentage=change_percentage
        ))
```

### Event Handlers

```python
# src/application/event_handlers/audit_log_handler.py
class AuditLogHandler(IEventHandler):
    """Log all domain events for audit trail."""
    
    def __init__(self, logger):
        self._logger = logger
    
    def handles(self) -> Type[DomainEvent]:
        return DomainEvent  # Handle all events
    
    async def handle(self, event: DomainEvent) -> None:
        self._logger.info(
            f"Domain Event: {event.event_type}",
            extra={"event_data": event.to_dict()}
        )

# src/application/event_handlers/cache_invalidation_handler.py
class StockCacheInvalidationHandler(IEventHandler):
    """Invalidate cache when stock is updated."""
    
    def __init__(self, cache_service):
        self._cache = cache_service
    
    def handles(self) -> Type[DomainEvent]:
        return StockPriceUpdatedEvent
    
    async def handle(self, event: StockPriceUpdatedEvent) -> None:
        await self._cache.invalidate(f"stock:{event.stock_id}")
        await self._cache.invalidate("stocks:all")
```

### Integration with Unit of Work

```python
# src/infrastructure/persistence/event_collecting_uow.py
class EventCollectingUnitOfWork(SqlAlchemyUnitOfWork):
    """Unit of Work that collects and publishes domain events."""
    
    def __init__(self, session_factory, event_publisher: IEventPublisher):
        super().__init__(session_factory)
        self._event_publisher = event_publisher
        self._collected_events: List[DomainEvent] = []
    
    def repository(self, repository_type: Type[T]) -> T:
        """Get repository that collects events from entities."""
        repo = super().repository(repository_type)
        
        # Wrap repository to collect events
        if hasattr(repo, 'set_event_collector'):
            repo.set_event_collector(self._collect_events)
        
        return repo
    
    def _collect_events(self, entity: AggregateRoot) -> None:
        """Collect events from an aggregate root."""
        events = entity.pull_events()
        self._collected_events.extend(events)
    
    async def commit(self) -> None:
        """Commit transaction and publish events."""
        # Commit database changes first
        await super().commit()
        
        # Then publish events (after successful commit)
        self._event_publisher.publish_batch(self._collected_events)
        self._collected_events.clear()
```

### Testing Events

```python
# tests/domain/test_stock_events.py
def test_stock_creation_raises_event():
    # Arrange & Act
    stock = Stock(
        symbol=StockSymbol("AAPL"),
        company=CompanyName("Apple Inc."),
        sector=Sector("Technology"),
        industry=Industry("Consumer Electronics", Sector("Technology"))
    )
    
    # Assert
    events = stock.pull_events()
    assert len(events) == 1
    assert isinstance(events[0], StockCreatedEvent)
    assert events[0].symbol == "AAPL"

# tests/infrastructure/test_event_bus.py
@pytest.mark.asyncio
async def test_event_bus_publishes_to_handlers():
    # Arrange
    bus = InMemoryEventBus()
    handler = MockEventHandler()
    bus.register_handler(handler)
    
    event = StockCreatedEvent(
        stock_id=uuid4(),
        symbol="AAPL",
        company_name="Apple Inc.",
        sector="Technology",
        industry="Consumer Electronics"
    )
    
    # Act
    bus.publish(event)
    
    # Assert
    assert handler.handled_events == [event]
```

### Future Evolution Path

```python
# Future: Async message queue integration
class RabbitMQEventPublisher(IEventPublisher):
    """Publish events to RabbitMQ for distributed processing."""
    
    async def publish(self, event: DomainEvent) -> None:
        await self._channel.publish(
            json.dumps(event.to_dict()),
            routing_key=event.event_type
        )

# Future: Event store for event sourcing
class EventStore:
    """Persist events for event sourcing."""
    
    async def append(self, stream_id: str, events: List[DomainEvent]) -> None:
        """Append events to an event stream."""
        pass
    
    async def load_stream(self, stream_id: str) -> List[DomainEvent]:
        """Load all events for a stream."""
        pass
```

## Links

* Implements [ADR-0003: Implement Domain-Driven Design](0003-implement-domain-driven-design.md)
* Works with [ADR-0009: Unit of Work Pattern](0009-unit-of-work-pattern.md)
* Enables future CQRS and Event Sourcing patterns
* References: "Domain-Driven Design" by Eric Evans
* References: "Implementing Domain-Driven Design" by Vaughn Vernon