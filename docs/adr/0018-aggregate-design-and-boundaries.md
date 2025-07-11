# Define Aggregate Design and Boundaries

* Status: accepted
* Deciders: Development team
* Date: 2025-01-11

## Context and Problem Statement

StockBook's domain model includes several interrelated entities like Stock, Portfolio, Transaction, Target, and JournalEntry. Following Domain-Driven Design principles, we need to group these entities into aggregates that define consistency boundaries and transaction scopes. How should we organize our domain entities into aggregates to ensure data consistency while maintaining performance and scalability?

## Decision Drivers

* **Consistency Requirements**: What data must be consistent at all times
* **Transaction Boundaries**: What operations must be atomic
* **Performance**: Avoid loading unnecessary data
* **Concurrency**: Minimize contention between users
* **Business Invariants**: Enforce business rules within boundaries
* **Scalability**: Design for future growth
* **Domain Logic**: Keep related behavior together

## Considered Options

* **Fine-grained Aggregates**: Each entity as its own aggregate root
* **Coarse-grained Aggregates**: Large aggregates with many entities
* **Portfolio-centric Design**: Portfolio as the main aggregate
* **Transaction-based Aggregates**: Design around business transactions
* **Event-sourced Aggregates**: Use events as aggregate boundaries
* **Anemic Aggregates**: Simple aggregates with external logic

## Decision Outcome

Chosen option: "Fine-grained Aggregates", because it provides the best balance between consistency, performance, and scalability. By keeping aggregates small and focused on specific consistency boundaries, we minimize lock contention, improve performance, and make the domain model easier to understand and maintain. This approach aligns with DDD best practices of designing aggregates around true invariants.

### Positive Consequences

* **Clear Boundaries**: Each aggregate has a specific purpose
* **Better Performance**: Smaller aggregates load faster
* **Reduced Contention**: Less locking conflicts
* **Easier Testing**: Smaller units to test
* **Scalability**: Can be distributed if needed
* **Flexibility**: Easier to refactor boundaries
* **Clear Invariants**: Business rules are localized

### Negative Consequences

* **Cross-aggregate Consistency**: Need eventual consistency
* **More Complex Queries**: May need to query multiple aggregates
* **Reference Management**: Must use IDs between aggregates
* **Transaction Coordination**: Some operations span aggregates

## Pros and Cons of the Options

### Fine-grained Aggregates

Small aggregates focused on single consistency boundaries.

* Good, because optimal performance
* Good, because minimal locking
* Good, because clear responsibilities
* Good, because easy to test
* Good, because scales well
* Good, because follows DDD guidelines
* Bad, because more aggregates to manage
* Bad, because cross-aggregate operations complex

### Coarse-grained Aggregates

Large aggregates containing many related entities.

* Good, because strong consistency
* Good, because fewer aggregates
* Good, because simpler queries
* Bad, because performance issues
* Bad, because high contention
* Bad, because difficult to scale
* Bad, because violates DDD principles
* Bad, because complex testing

### Portfolio-centric Design

Portfolio as main aggregate containing all related data.

* Good, because matches user mental model
* Good, because single entry point
* Bad, because huge aggregate
* Bad, because performance problems
* Bad, because concurrent user issues
* Bad, because difficult to maintain

### Transaction-based Aggregates

Design aggregates around business transactions.

* Good, because transaction alignment
* Good, because clear boundaries
* Bad, because data duplication
* Bad, because complex modeling
* Bad, because unintuitive structure
* Bad, because maintenance overhead

### Event-sourced Aggregates

Use events to define aggregate boundaries.

* Good, because natural boundaries
* Good, because audit trail
* Good, because temporal queries
* Bad, because complex implementation
* Bad, because performance overhead
* Bad, because steep learning curve
* Bad, because overkill for current needs

### Anemic Aggregates

Simple data containers with logic elsewhere.

* Good, because simple structure
* Good, because easy serialization
* Bad, because no encapsulation
* Bad, because scattered logic
* Bad, because not true DDD
* Bad, because invariant violations

## Implementation Details

Our aggregate design:

### Aggregate Definitions

```python
# src/domain/aggregates/README.md
"""
Aggregate Boundaries:

1. Stock Aggregate
   - Root: Stock
   - Invariants: Symbol uniqueness, valid sector/industry
   - No child entities

2. Portfolio Aggregate  
   - Root: Portfolio
   - Invariants: Name uniqueness per user, valid description
   - No child entities (transactions are separate)

3. Transaction Aggregate
   - Root: Transaction
   - Invariants: Valid quantity/price, consistent type
   - No child entities

4. Target Aggregate
   - Root: Target
   - Invariants: Valid target price, status transitions
   - No child entities

5. JournalEntry Aggregate
   - Root: JournalEntry
   - Invariants: Valid sentiment, content requirements
   - No child entities
"""
```

### Stock Aggregate

```python
# src/domain/aggregates/stock.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from src.domain.entities.base import AggregateRoot
from src.domain.events import StockCreatedEvent, StockPriceUpdatedEvent
from src.domain.value_objects import (
    StockSymbol, CompanyName, Sector, Industry, Money
)

@dataclass
class Stock(AggregateRoot):
    """
    Stock aggregate root.
    
    Invariants:
    - Symbol must be unique (enforced by repository)
    - Sector and industry must be valid combination
    - Price updates must be positive
    """
    
    id: UUID
    symbol: StockSymbol
    company: CompanyName
    sector: Sector
    industry: Industry
    current_price: Optional[Money]
    created_at: datetime
    updated_at: Optional[datetime]
    
    @classmethod
    def create(
        cls,
        symbol: StockSymbol,
        company: CompanyName,
        sector: Sector,
        industry: Industry,
        initial_price: Optional[Money] = None
    ) -> 'Stock':
        """Factory method to create new stock."""
        stock = cls(
            id=uuid4(),
            symbol=symbol,
            company=company,
            sector=sector,
            industry=industry,
            current_price=initial_price,
            created_at=datetime.utcnow(),
            updated_at=None
        )
        
        # Raise domain event
        stock.raise_event(StockCreatedEvent(
            stock_id=stock.id,
            symbol=symbol.value,
            company_name=company.value,
            sector=sector.value,
            industry=industry.value
        ))
        
        return stock
    
    def update_price(self, new_price: Money) -> None:
        """Update stock price with validation."""
        if new_price.amount <= 0:
            raise ValueError("Stock price must be positive")
        
        old_price = self.current_price
        self.current_price = new_price
        self.updated_at = datetime.utcnow()
        
        # Calculate change percentage
        if old_price:
            change_percentage = (
                (new_price.amount - old_price.amount) / old_price.amount * 100
            )
        else:
            change_percentage = 0
        
        # Raise domain event
        self.raise_event(StockPriceUpdatedEvent(
            stock_id=self.id,
            old_price=old_price.amount if old_price else None,
            new_price=new_price.amount,
            change_percentage=change_percentage
        ))
```

### Portfolio Aggregate

```python
# src/domain/aggregates/portfolio.py
@dataclass
class Portfolio(AggregateRoot):
    """
    Portfolio aggregate root.
    
    Invariants:
    - Name must be unique per user (enforced by repository)
    - Description length constraints
    
    Note: Transactions are NOT part of this aggregate to avoid
    loading all transactions when accessing portfolio.
    """
    
    id: UUID
    user_id: UUID  # Reference to user (not modeled here)
    name: PortfolioName
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    @classmethod
    def create(
        cls,
        user_id: UUID,
        name: PortfolioName,
        description: Optional[str] = None
    ) -> 'Portfolio':
        """Factory method to create new portfolio."""
        if description and len(description) > 500:
            raise ValueError("Description too long")
        
        portfolio = cls(
            id=uuid4(),
            user_id=user_id,
            name=name,
            description=description,
            created_at=datetime.utcnow(),
            updated_at=None
        )
        
        portfolio.raise_event(PortfolioCreatedEvent(
            portfolio_id=portfolio.id,
            user_id=user_id,
            name=name.value
        ))
        
        return portfolio
    
    def rename(self, new_name: PortfolioName) -> None:
        """Rename portfolio."""
        old_name = self.name
        self.name = new_name
        self.updated_at = datetime.utcnow()
        
        self.raise_event(PortfolioRenamedEvent(
            portfolio_id=self.id,
            old_name=old_name.value,
            new_name=new_name.value
        ))
```

### Transaction Aggregate

```python
# src/domain/aggregates/transaction.py
@dataclass
class Transaction(AggregateRoot):
    """
    Transaction aggregate root.
    
    Invariants:
    - Quantity must be positive
    - Price must be positive
    - Type must be BUY or SELL
    - Cannot modify after creation (immutable)
    
    Note: References Portfolio and Stock by ID only.
    """
    
    id: UUID
    portfolio_id: UUID  # Reference only
    stock_id: UUID      # Reference only
    transaction_type: TransactionType
    quantity: Quantity
    price: Money
    transaction_date: datetime
    created_at: datetime
    
    def __post_init__(self):
        """Ensure immutability."""
        # Make dataclass frozen after creation
        object.__setattr__(self, '_frozen', True)
    
    @classmethod
    def execute_buy(
        cls,
        portfolio_id: UUID,
        stock_id: UUID,
        quantity: Quantity,
        price: Money,
        transaction_date: Optional[datetime] = None
    ) -> 'Transaction':
        """Execute a buy transaction."""
        transaction = cls(
            id=uuid4(),
            portfolio_id=portfolio_id,
            stock_id=stock_id,
            transaction_type=TransactionType.BUY,
            quantity=quantity,
            price=price,
            transaction_date=transaction_date or datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        
        transaction.raise_event(TransactionExecutedEvent(
            transaction_id=transaction.id,
            portfolio_id=portfolio_id,
            stock_id=stock_id,
            transaction_type="BUY",
            quantity=quantity.value,
            price=price.amount,
            total_amount=transaction.calculate_total().amount
        ))
        
        return transaction
    
    def calculate_total(self) -> Money:
        """Calculate total transaction amount."""
        return Money(self.price.amount * self.quantity.value)
    
    def __setattr__(self, name, value):
        """Prevent modification after creation."""
        if hasattr(self, '_frozen') and self._frozen:
            raise ValueError("Transaction is immutable")
        super().__setattr__(name, value)
```

### Cross-Aggregate Operations

```python
# src/application/services/portfolio_service.py
class PortfolioApplicationService:
    """Handles operations that span aggregates."""
    
    async def get_portfolio_value(
        self, 
        portfolio_id: UUID
    ) -> PortfolioValueDTO:
        """
        Calculate portfolio value across aggregates.
        This is a read operation, so no consistency concerns.
        """
        async with self._uow:
            # Load portfolio aggregate
            portfolio_repo = self._uow.repository(IPortfolioRepository)
            portfolio = await portfolio_repo.find_by_id(portfolio_id)
            
            # Load related transactions (separate aggregate)
            transaction_repo = self._uow.repository(ITransactionRepository)
            transactions = await transaction_repo.find_by_portfolio(portfolio_id)
            
            # Load current stock prices (separate aggregates)
            stock_repo = self._uow.repository(IStockRepository)
            stock_ids = {t.stock_id for t in transactions}
            stocks = await stock_repo.find_by_ids(list(stock_ids))
            
            # Calculate value using domain service
            value = self._calculator.calculate_portfolio_value(
                transactions, stocks
            )
            
            return PortfolioValueDTO(
                portfolio_id=portfolio_id,
                total_value=value,
                as_of=datetime.utcnow()
            )
```

### Aggregate References

```python
# src/domain/specifications/portfolio_specs.py
class PortfolioOwnershipSpecification:
    """Specification for checking portfolio ownership."""
    
    def __init__(self, user_id: UUID):
        self.user_id = user_id
    
    def is_satisfied_by(self, portfolio: Portfolio) -> bool:
        """Check if portfolio belongs to user."""
        return portfolio.user_id == self.user_id

# Usage in service
async def execute_transaction(self, command: ExecuteTransactionCommand):
    """Execute transaction with ownership check."""
    async with self._uow:
        # Load aggregates
        portfolio = await self._get_portfolio(command.portfolio_id)
        stock = await self._get_stock(command.stock_id)
        
        # Check ownership (cross-aggregate rule)
        if not PortfolioOwnershipSpecification(command.user_id).is_satisfied_by(portfolio):
            raise UnauthorizedError("Portfolio not owned by user")
        
        # Create transaction (new aggregate)
        transaction = Transaction.execute_buy(
            portfolio_id=portfolio.id,
            stock_id=stock.id,
            quantity=command.quantity,
            price=command.price
        )
        
        # Save transaction
        await self._uow.repository(ITransactionRepository).save(transaction)
```

### Eventual Consistency

```python
# When consistency across aggregates is needed
class PortfolioStatsUpdater(IEventHandler):
    """Update portfolio statistics eventually."""
    
    def handles(self) -> Type[DomainEvent]:
        return TransactionExecutedEvent
    
    async def handle(self, event: TransactionExecutedEvent) -> None:
        """Update portfolio stats after transaction."""
        # This happens outside the transaction boundary
        # ensuring eventual consistency
        await self._update_portfolio_stats(event.portfolio_id)
```

## Links

* Implements [ADR-0003: Implement Domain-Driven Design](0003-implement-domain-driven-design.md)
* Works with [ADR-0008: Repository Pattern](0008-repository-pattern.md)
* Supports [ADR-0009: Unit of Work Pattern](0009-unit-of-work-pattern.md)
* References: "Domain-Driven Design" by Eric Evans (Chapter on Aggregates)
* References: "Implementing Domain-Driven Design" by Vaughn Vernon