# Use Value Objects for Type Safety and Domain Modeling

* Status: accepted
* Deciders: Development team
* Date: 2025-01-11

## Context and Problem Statement

Financial applications deal with numerous domain concepts that have specific rules and constraints: stock symbols must be uppercase, money requires precision handling, quantities must be positive, and sector/industry combinations must be valid. Using primitive types (strings, integers, decimals) for these concepts leads to validation logic scattered throughout the codebase and increases the risk of passing invalid data between layers. How can we ensure type safety and domain integrity while making our code more expressive and maintainable?

## Decision Drivers

* **Type Safety**: Prevent mixing incompatible values (e.g., passing a company name where a symbol is expected)
* **Business Rule Encapsulation**: Keep validation logic with the data it validates
* **Domain Expressiveness**: Code should clearly express business concepts
* **Prevent Invalid States**: Make illegal states unrepresentable
* **Immutability**: Financial data should not change after creation
* **Validation at Boundaries**: Ensure data validity as early as possible
* **Self-Documenting Code**: Types should communicate intent

## Considered Options

* **Extensive Value Objects**: Create value objects for all domain concepts
* **Primitive Obsession**: Use primitive types with validation functions
* **Type Aliases**: Use Python type aliases for documentation
* **Dataclasses Only**: Use dataclasses without custom validation
* **Pydantic Models Everywhere**: Use Pydantic for all domain objects
* **Mixed Approach**: Value objects for critical concepts only

## Decision Outcome

Chosen option: "Extensive Value Objects", because value objects provide the strongest guarantees for type safety and domain integrity. By creating specific types for each domain concept, we make invalid states unrepresentable and ensure business rules are consistently enforced. This approach aligns perfectly with our Domain-Driven Design principles.

### Positive Consequences

* **Compile-Time Safety**: Type checker prevents invalid assignments
* **Business Rules Centralized**: All validation in one place
* **Immutability Guaranteed**: Value objects are immutable by design
* **Self-Documenting**: Types clearly express domain concepts
* **Refactoring Safety**: Changes to rules affect all usages
* **Testing Simplified**: Test value objects in isolation
* **No Primitive Obsession**: Rich types instead of strings/ints

### Negative Consequences

* **More Classes**: Many small classes to maintain
* **Initial Development Time**: More upfront design work
* **Serialization Complexity**: Need to handle conversion to/from primitives
* **Learning Curve**: Developers must understand value object pattern

## Pros and Cons of the Options

### Extensive Value Objects

Create dedicated immutable classes for each domain concept.

* Good, because provides maximum type safety
* Good, because encapsulates all validation rules
* Good, because makes domain model expressive
* Good, because prevents invalid states
* Good, because supports Domain-Driven Design
* Bad, because requires more initial setup
* Bad, because needs serialization handling

### Primitive Obsession

Use strings, integers, and decimals with separate validation.

* Good, because simple to start with
* Good, because no serialization needed
* Bad, because validation scattered across codebase
* Bad, because easy to pass wrong types
* Bad, because no compile-time safety
* Bad, because duplicated validation logic
* Bad, because harder to refactor

### Type Aliases

Use Python's type alias feature for documentation.

```python
StockSymbol = str
CompanyName = str
```

* Good, because minimal overhead
* Good, because improves readability
* Bad, because no runtime validation
* Bad, because no actual type safety
* Bad, because aliases are just documentation
* Bad, because can still mix types

### Dataclasses Only

Use Python dataclasses without custom validation.

* Good, because standard Python feature
* Good, because reduces boilerplate
* Bad, because no inherent validation
* Bad, because mutable by default
* Bad, because no business rule enforcement
* Bad, because still allows invalid states

### Pydantic Models Everywhere

Use Pydantic for all domain objects, not just DTOs.

* Good, because automatic validation
* Good, because serialization built-in
* Bad, because couples domain to framework
* Bad, because mutable by default
* Bad, because validation at assignment, not construction
* Bad, because violates Clean Architecture

### Mixed Approach

Value objects only for critical concepts, primitives elsewhere.

* Good, because pragmatic balance
* Good, because less initial work
* Bad, because inconsistent approach
* Bad, because unclear which concepts are "critical"
* Bad, because team confusion about when to use which
* Bad, because gradual degradation likely

## Implementation Details

Our value object implementation includes:

### Base Value Object Pattern

```python
from abc import ABC
from dataclasses import dataclass
from typing import Any, TypeVar

T = TypeVar('T')

@dataclass(frozen=True)
class ValueObject(ABC):
    """Base class for all value objects."""
    
    def __post_init__(self) -> None:
        """Validate after initialization."""
        self._validate()
    
    def _validate(self) -> None:
        """Override to implement validation."""
        pass
```

### Domain Value Objects

#### Money
```python
@dataclass(frozen=True)
class Money(ValueObject):
    amount: Decimal
    currency: str = "USD"
    
    def _validate(self) -> None:
        if self.amount.as_tuple().exponent < -2:
            raise ValueError("Money cannot have more than 2 decimal places")
        if self.currency not in VALID_CURRENCIES:
            raise ValueError(f"Invalid currency: {self.currency}")
    
    def add(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    @classmethod
    def zero(cls, currency: str = "USD") -> 'Money':
        return cls(Decimal("0.00"), currency)
```

#### StockSymbol
```python
@dataclass(frozen=True)
class StockSymbol(ValueObject):
    value: str
    
    def _validate(self) -> None:
        if not self.value:
            raise ValueError("Stock symbol cannot be empty")
        if not self.value.isupper():
            raise ValueError("Stock symbol must be uppercase")
        if not 1 <= len(self.value) <= 5:
            raise ValueError("Stock symbol must be 1-5 characters")
        if not self.value.isalpha():
            raise ValueError("Stock symbol must contain only letters")
```

#### Quantity
```python
@dataclass(frozen=True)
class Quantity(ValueObject):
    value: int
    
    def _validate(self) -> None:
        if self.value <= 0:
            raise ValueError("Quantity must be positive")
    
    def add(self, other: 'Quantity') -> 'Quantity':
        return Quantity(self.value + other.value)
    
    def multiply(self, factor: int) -> 'Quantity':
        return Quantity(self.value * factor)
```

### Complex Value Objects

#### Sector and Industry
```python
@dataclass(frozen=True)
class Sector(ValueObject):
    value: str
    
    def _validate(self) -> None:
        if self.value not in VALID_SECTORS:
            raise ValueError(f"Invalid sector: {self.value}")

@dataclass(frozen=True)
class Industry(ValueObject):
    value: str
    sector: Sector
    
    def _validate(self) -> None:
        valid_industries = SECTOR_INDUSTRY_MAP.get(self.sector.value, [])
        if self.value not in valid_industries:
            raise ValueError(
                f"Invalid industry '{self.value}' for sector '{self.sector.value}'"
            )
```

### Usage in Entities

```python
class Stock(Entity):
    def __init__(
        self,
        symbol: StockSymbol,
        company: CompanyName,
        sector: Sector,
        industry: Industry,
        price: Money,
    ):
        # Value objects guarantee validity
        self.symbol = symbol
        self.company = company
        self.sector = sector
        self.industry = industry
        self.price = price
    
    def update_price(self, new_price: Money) -> None:
        """Type safety ensures only Money can be passed."""
        if new_price.amount <= Decimal("0"):
            raise ValueError("Price must be positive")
        self.price = new_price
```

### Serialization Support

```python
class MoneyDTO:
    @staticmethod
    def from_value_object(money: Money) -> dict:
        return {
            "amount": str(money.amount),
            "currency": money.currency
        }
    
    @staticmethod
    def to_value_object(data: dict) -> Money:
        return Money(
            amount=Decimal(data["amount"]),
            currency=data["currency"]
        )
```

### Type Safety Benefits

```python
# This won't compile - type checker catches error
stock = Stock(
    symbol=company_name,  # Error: Expected StockSymbol, got CompanyName
    company=stock_symbol,  # Error: Expected CompanyName, got StockSymbol
    ...
)

# This is caught at runtime by value object validation
try:
    symbol = StockSymbol("invalid!")  # Contains special character
except ValueError as e:
    print(f"Invalid symbol: {e}")

# Immutability prevents accidental changes
money = Money(Decimal("100.00"))
# money.amount = Decimal("200.00")  # Error: Cannot assign to field
new_money = money.add(Money(Decimal("50.00")))  # Create new instance
```

### Testing Value Objects

```python
class TestMoney:
    def test_valid_creation(self):
        money = Money(Decimal("100.50"))
        assert money.amount == Decimal("100.50")
        assert money.currency == "USD"
    
    def test_invalid_precision(self):
        with pytest.raises(ValueError, match="2 decimal places"):
            Money(Decimal("100.555"))
    
    def test_addition(self):
        money1 = Money(Decimal("100.00"))
        money2 = Money(Decimal("50.50"))
        result = money1.add(money2)
        assert result.amount == Decimal("150.50")
    
    def test_different_currency_addition_fails(self):
        usd = Money(Decimal("100.00"), "USD")
        eur = Money(Decimal("100.00"), "EUR")
        with pytest.raises(ValueError, match="different currencies"):
            usd.add(eur)
```

## Links

* Implements [ADR-0003: Implement Domain-Driven Design](0003-implement-domain-driven-design.md)
* Supports [ADR-0002: Use Clean Architecture](0002-use-clean-architecture.md)
* Enforced by [ADR-0006: Python FastAPI SQLAlchemy Stack](0006-python-fastapi-sqlalchemy-stack.md)
* References: "Domain-Driven Design" by Eric Evans (Value Object pattern)
* References: "Implementing Domain-Driven Design" by Vaughn Vernon