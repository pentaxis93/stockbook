# Use Command Pattern for Application Layer

* Status: accepted
* Deciders: Development team
* Date: 2025-01-11

## Context and Problem Statement

StockBook's application layer needs to handle complex business operations that involve multiple steps, validations, and side effects. We need a pattern that clearly represents user intentions, enables validation before execution, supports undo/redo capabilities in the future, and provides a clean API for the presentation layer. How should we structure the requests coming into our application layer to maintain clarity, testability, and extensibility?

## Decision Drivers

* **Intent Clarity**: Each operation should clearly express what the user wants to do
* **Validation**: Need to validate requests before executing business logic
* **Testability**: Easy to test commands in isolation
* **Audit Trail**: Commands naturally provide a log of what was requested
* **CQRS Foundation**: Separate read and write operations cleanly
* **Type Safety**: Leverage Python's type system for command parameters
* **Extensibility**: Easy to add new operations without modifying existing code

## Considered Options

* **Command Pattern**: Explicit command objects for each operation
* **Service Methods**: Traditional service methods with multiple parameters
* **Request Objects**: Generic request/response objects
* **Direct Entity Manipulation**: Let presentation layer work with entities directly
* **Message-Based**: Use generic messages with type discrimination
* **RPC Style**: Remote procedure call style with dictionaries

## Decision Outcome

Chosen option: "Command Pattern", because it provides the clearest expression of user intent, enables comprehensive validation, and creates a foundation for advanced patterns like CQRS and event sourcing. Commands make our application layer's API explicit and self-documenting while maintaining excellent testability.

### Positive Consequences

* **Self-Documenting API**: Command names clearly express operations
* **Single Responsibility**: Each command does one thing
* **Easy Validation**: Validate command data before execution
* **Audit Trail**: Natural history of user actions
* **Test Isolation**: Test commands without full application context
* **Future CQRS**: Clear separation of commands and queries
* **Type Safety**: Full typing for command parameters

### Negative Consequences

* **More Classes**: One class per operation
* **Initial Overhead**: More setup than simple methods
* **Learning Curve**: Team needs to understand the pattern
* **Potential Duplication**: Similar commands might have similar fields

## Pros and Cons of the Options

### Command Pattern

Each operation is represented by a specific command class.

* Good, because explicit intent in class names
* Good, because self-contained validation
* Good, because supports command handlers
* Good, because enables command queuing/scheduling
* Good, because natural audit log
* Good, because easy to test
* Bad, because many small classes
* Bad, because initial setup overhead

### Service Methods

Traditional approach with methods accepting multiple parameters.

* Good, because familiar to most developers
* Good, because less initial setup
* Good, because fewer classes
* Bad, because parameter proliferation
* Bad, because unclear intent with many parameters
* Bad, because hard to validate complex operations
* Bad, because no natural audit trail
* Bad, because difficult to extend

### Request Objects

Generic request/response objects without specific types.

* Good, because fewer classes than commands
* Good, because reusable structures
* Bad, because less explicit intent
* Bad, because weaker type safety
* Bad, because validation scattered
* Bad, because generic names reduce clarity

### Direct Entity Manipulation

Let presentation layer create and modify entities directly.

* Good, because very simple
* Good, because no translation layer
* Bad, because breaks encapsulation
* Bad, because business logic leaks to presentation
* Bad, because hard to validate
* Bad, because tight coupling
* Bad, because no audit trail

### Message-Based

Generic messages with type field for discrimination.

* Good, because flexible structure
* Good, because single message type
* Bad, because runtime type checking
* Bad, because no compile-time safety
* Bad, because complex validation logic
* Bad, because poor IDE support

### RPC Style

Dictionary-based parameters like remote procedure calls.

* Good, because very flexible
* Good, because familiar from web services
* Bad, because no type safety
* Bad, because runtime validation only
* Bad, because poor documentation
* Bad, because error-prone

## Implementation Details

Our command pattern implementation:

### Base Command Class

```python
# src/application/commands/base.py
from abc import ABC
from dataclasses import dataclass
from typing import TypeVar, Generic

T = TypeVar('T')

@dataclass(frozen=True)
class Command(ABC):
    """Base class for all commands."""
    pass

class CommandHandler(ABC, Generic[T]):
    """Base class for command handlers."""
    
    @abstractmethod
    async def handle(self, command: T) -> Any:
        """Execute the command."""
        pass
```

### Domain Commands

```python
# src/application/commands/stock_commands.py
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from src.domain.value_objects import StockSymbol, CompanyName, Sector, Industry

@dataclass(frozen=True)
class CreateStockCommand(Command):
    """Command to create a new stock."""
    
    symbol: StockSymbol
    company: CompanyName
    sector: Sector
    industry: Industry
    
    def __post_init__(self):
        """Validate command data."""
        if not self.symbol:
            raise ValueError("Stock symbol is required")
        if not self.company:
            raise ValueError("Company name is required")
        # Additional validation...

@dataclass(frozen=True)
class UpdateStockPriceCommand(Command):
    """Command to update stock price."""
    
    stock_id: UUID
    new_price: Decimal
    
    def __post_init__(self):
        if self.new_price <= 0:
            raise ValueError("Price must be positive")

@dataclass(frozen=True)
class ExecuteTransactionCommand(Command):
    """Command to execute a stock transaction."""
    
    portfolio_id: UUID
    stock_id: UUID
    transaction_type: str  # "BUY" or "SELL"
    quantity: int
    price: Decimal
    
    def __post_init__(self):
        if self.transaction_type not in ["BUY", "SELL"]:
            raise ValueError("Transaction type must be BUY or SELL")
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.price <= 0:
            raise ValueError("Price must be positive")
```

### Command Handlers

```python
# src/application/handlers/stock_command_handler.py
class CreateStockCommandHandler(CommandHandler[CreateStockCommand]):
    """Handler for creating stocks."""
    
    def __init__(self, unit_of_work: IUnitOfWork, event_publisher: IEventPublisher):
        self._uow = unit_of_work
        self._event_publisher = event_publisher
    
    async def handle(self, command: CreateStockCommand) -> UUID:
        async with self._uow:
            stock_repo = self._uow.repository(IStockRepository)
            
            # Check if stock already exists
            existing = await stock_repo.find_by_symbol(command.symbol)
            if existing:
                raise StockAlreadyExistsError(command.symbol)
            
            # Create stock entity
            stock = Stock.create(
                symbol=command.symbol,
                company=command.company,
                sector=command.sector,
                industry=command.industry
            )
            
            # Save to repository
            await stock_repo.save(stock)
            
            # Publish events
            events = stock.pull_events()
            for event in events:
                await self._event_publisher.publish(event)
            
        return stock.id
```

### Command Bus

```python
# src/application/command_bus.py
from typing import Dict, Type, Any

class CommandBus:
    """Routes commands to their handlers."""
    
    def __init__(self):
        self._handlers: Dict[Type[Command], CommandHandler] = {}
    
    def register_handler(
        self, 
        command_type: Type[Command], 
        handler: CommandHandler
    ) -> None:
        """Register a handler for a command type."""
        self._handlers[command_type] = handler
    
    async def execute(self, command: Command) -> Any:
        """Execute a command using its registered handler."""
        handler = self._handlers.get(type(command))
        if not handler:
            raise ValueError(f"No handler registered for {type(command).__name__}")
        
        return await handler.handle(command)
```

### Usage in Application Service

```python
# src/application/services/stock_application_service.py
class StockApplicationService:
    """Application service using command pattern."""
    
    def __init__(self, command_bus: CommandBus):
        self._command_bus = command_bus
    
    async def create_stock(self, request: CreateStockRequest) -> StockDTO:
        """Create a new stock."""
        # Convert request to command
        command = CreateStockCommand(
            symbol=StockSymbol(request.symbol),
            company=CompanyName(request.company_name),
            sector=Sector(request.sector),
            industry=Industry(request.industry, Sector(request.sector))
        )
        
        # Execute command
        stock_id = await self._command_bus.execute(command)
        
        # Return response
        return StockDTO(id=stock_id, symbol=request.symbol, ...)
```

### Testing Commands

```python
# tests/application/commands/test_stock_commands.py
def test_create_stock_command_validation():
    """Test command validation."""
    # Valid command
    command = CreateStockCommand(
        symbol=StockSymbol("AAPL"),
        company=CompanyName("Apple Inc."),
        sector=Sector("Technology"),
        industry=Industry("Consumer Electronics", Sector("Technology"))
    )
    assert command.symbol.value == "AAPL"
    
    # Invalid command
    with pytest.raises(ValueError, match="Stock symbol is required"):
        CreateStockCommand(
            symbol=None,
            company=CompanyName("Apple Inc."),
            sector=Sector("Technology"),
            industry=Industry("Consumer Electronics", Sector("Technology"))
        )

@pytest.mark.asyncio
async def test_create_stock_command_handler():
    """Test command handler execution."""
    # Arrange
    mock_uow = MockUnitOfWork()
    mock_publisher = MockEventPublisher()
    handler = CreateStockCommandHandler(mock_uow, mock_publisher)
    
    command = CreateStockCommand(
        symbol=StockSymbol("AAPL"),
        company=CompanyName("Apple Inc."),
        sector=Sector("Technology"),
        industry=Industry("Consumer Electronics", Sector("Technology"))
    )
    
    # Act
    stock_id = await handler.handle(command)
    
    # Assert
    assert stock_id is not None
    assert mock_uow.committed
    assert len(mock_publisher.published_events) == 1
    assert isinstance(mock_publisher.published_events[0], StockCreatedEvent)
```

### Command Validation

```python
# src/application/validators/command_validator.py
class CommandValidator:
    """Additional validation beyond command self-validation."""
    
    async def validate_create_stock_command(
        self, 
        command: CreateStockCommand,
        stock_repo: IStockRepository
    ) -> None:
        """Validate business rules for stock creation."""
        # Check uniqueness
        existing = await stock_repo.find_by_symbol(command.symbol)
        if existing:
            raise ValidationError(f"Stock {command.symbol.value} already exists")
        
        # Check sector/industry combination
        if not self._is_valid_industry_for_sector(command.industry, command.sector):
            raise ValidationError(
                f"Invalid industry {command.industry.value} for sector {command.sector.value}"
            )
```

### Future Evolution

```python
# Future: Command queuing for async processing
class AsyncCommandQueue:
    """Queue commands for background processing."""
    
    async def enqueue(self, command: Command) -> UUID:
        """Add command to processing queue."""
        return await self._queue.put(command)

# Future: Command versioning for compatibility
@dataclass(frozen=True)
class CreateStockCommandV2(Command):
    """Version 2 with additional fields."""
    
    # All V1 fields plus...
    exchange: str
    currency: str
```

## Links

* Implements [ADR-0002: Use Clean Architecture](0002-use-clean-architecture.md)
* Supports [ADR-0003: Implement Domain-Driven Design](0003-implement-domain-driven-design.md)
* Foundation for future CQRS implementation
* References: "Implementing Domain-Driven Design" by Vaughn Vernon
* References: "Pattern-Oriented Software Architecture" by Buschmann et al.