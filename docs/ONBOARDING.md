# StockBook Developer Onboarding Guide

Welcome to the StockBook project! This guide will help you get up and running quickly.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Development Workflow](#development-workflow)
4. [Code Organization](#code-organization)
5. [Common Tasks](#common-tasks)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software
- **Python 3.13+** - Core language (must be 3.13 or higher)
- **Git** - Version control
- **Docker** (recommended) - Consistent development environment
- **Make** - Build automation (usually pre-installed on Unix systems)

### Recommended Tools
- **VS Code** or **PyCharm** - IDE with Python support
- **pyright** extension - Type checking in your editor
- **black** formatter extension - Code formatting

## Quick Start

### 1. Clone and Setup (5 minutes)

```bash
# Clone the repository
git clone https://github.com/yourusername/stockbook.git
cd stockbook

# Option A: Docker Setup (Recommended)
docker-compose up --build

# Option B: Local Setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pre-commit install  # IMPORTANT: Required for all contributors
```

### 2. Verify Installation

```bash
# Run tests to ensure everything works
make test

# Check all available commands
make help

# Run quality checks
make quality
```

### 3. Understand the Project Structure

```bash
# View project structure
tree -I '__pycache__|*.pyc|venv|.git' -L 3

# Key directories:
# - src/domain/      → Business logic lives here
# - src/application/ → Use cases and orchestration
# - tests/          → Comprehensive test suite
# - docs/           → Documentation (you are here!)
```

## Development Workflow

### The Golden Rules

1. **Always use TDD (Test-Driven Development)**
   ```bash
   # 1. Write a failing test
   # 2. Write minimal code to pass
   # 3. Refactor
   # 4. Repeat
   ```

2. **Type Safety is Mandatory**
   ```python
   # Bad ❌
   def calculate_total(price, quantity):
       return price * quantity
   
   # Good ✅
   def calculate_total(price: Money, quantity: Quantity) -> Money:
       return Money(price.amount * quantity.value, price.currency)
   ```

3. **Pre-commit Hooks Must Pass**
   ```bash
   # These run automatically on commit
   # NEVER use --no-verify to bypass!
   ```

### Daily Development Flow

```bash
# 1. Start your day
git pull origin main
make test  # Ensure clean state

# 2. Create a feature branch
git checkout -b feature/add-portfolio-metrics

# 3. Write tests first (TDD)
# Create: tests/domain/test_portfolio_metrics.py

# 4. Run tests (they should fail)
make test-watch  # Auto-runs on file changes

# 5. Implement feature
# Create: src/domain/services/portfolio_metrics.py

# 6. Ensure quality
make format  # Auto-format code
make quality  # Run all checks

# 7. Commit (pre-commit hooks run automatically)
git add .
git commit -m "feat: add portfolio metrics calculation"

# 8. Push and create PR
git push origin feature/add-portfolio-metrics
```

### Make Commands Reference

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `make test` | Run all tests with coverage | Before committing |
| `make test-fast` | Quick test run | During development |
| `make test-watch` | Auto-run tests on changes | Active development |
| `make format` | Format code (black + isort) | Before committing |
| `make lint` | Run pylint checks | Check code quality |
| `make typecheck` | Run type checking | Verify type safety |
| `make quality` | All quality checks | Same as pre-commit |
| `make all` | Format + quality | Full check |

## Code Organization

### Architecture Layers

```
src/
├── domain/           # Core business logic (innermost layer)
│   ├── entities/     # Business objects with identity
│   ├── value_objects/# Immutable values (Money, Quantity)
│   ├── services/     # Domain logic that spans entities
│   ├── repositories/ # Interfaces only (no implementation!)
│   └── events/       # Domain events
│
└── application/      # Use cases and orchestration
    ├── services/     # Application services (use cases)
    ├── commands/     # Command objects (intentions)
    └── dto/          # Data transfer objects
```

### Key Concepts

#### 1. Entities vs Value Objects
```python
# Entity: Has identity, mutable
class Stock(BaseEntity):
    def __init__(self, id: UUID, symbol: StockSymbol):
        self.id = id  # Identity
        self.symbol = symbol  # Can change

# Value Object: No identity, immutable
@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str = "USD"
    # Cannot change after creation
```

#### 2. Repository Pattern
```python
# Domain layer: Interface only
class IStockRepository(ABC):
    @abstractmethod
    def save(self, stock: Stock) -> None:
        pass

# Infrastructure layer (future): Implementation
class SqliteStockRepository(IStockRepository):
    def save(self, stock: Stock) -> None:
        # Actual database code
```

#### 3. Application Services
```python
# Orchestrates domain objects
class StockApplicationService:
    def create_stock(self, command: CreateStockCommand) -> StockDTO:
        # 1. Validate command
        # 2. Create domain objects
        # 3. Apply business rules
        # 4. Persist via repository
        # 5. Return DTO
```

## Common Tasks

### Adding a New Entity

1. **Define the entity** in `src/domain/entities/`
```python
# src/domain/entities/watchlist_entity.py
from dataclasses import dataclass
from uuid import UUID
from src.domain.entities.base import BaseEntity

@dataclass
class Watchlist(BaseEntity):
    """A collection of stocks being monitored."""
    id: UUID
    name: str
    stock_ids: List[UUID]
    
    def add_stock(self, stock_id: UUID) -> None:
        """Add a stock to the watchlist."""
        if stock_id not in self.stock_ids:
            self.stock_ids.append(stock_id)
```

2. **Write tests first** in `tests/domain/entities/`
```python
# tests/domain/entities/test_watchlist_entity.py
def test_watchlist_add_stock():
    watchlist = Watchlist(id=uuid4(), name="Tech Stocks", stock_ids=[])
    stock_id = uuid4()
    
    watchlist.add_stock(stock_id)
    
    assert stock_id in watchlist.stock_ids
```

3. **Create repository interface** in `src/domain/repositories/`
```python
# src/domain/repositories/interfaces.py
class IWatchlistRepository(ABC):
    @abstractmethod
    def save(self, watchlist: Watchlist) -> None:
        pass
```

### Adding a New Value Object

1. **Define the value object** in `src/domain/value_objects/`
```python
# src/domain/value_objects/percentage.py
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Percentage:
    """Represents a percentage value."""
    value: Decimal
    
    def __post_init__(self):
        if not 0 <= self.value <= 100:
            raise ValueError("Percentage must be between 0 and 100")
    
    def to_decimal(self) -> Decimal:
        """Convert to decimal representation (e.g., 50% -> 0.5)."""
        return self.value / 100
```

2. **Write comprehensive tests**
```python
# tests/domain/value_objects/test_percentage.py
def test_percentage_valid_range():
    percentage = Percentage(Decimal("50"))
    assert percentage.value == Decimal("50")
    assert percentage.to_decimal() == Decimal("0.5")

def test_percentage_invalid_range():
    with pytest.raises(ValueError):
        Percentage(Decimal("101"))
```

### Adding a New Use Case

1. **Create command object** in `src/application/commands/`
```python
# src/application/commands/watchlist_commands.py
@dataclass(frozen=True)
class CreateWatchlistCommand:
    name: str
    initial_stock_ids: List[UUID] = field(default_factory=list)
```

2. **Implement in application service**
```python
# src/application/services/watchlist_application_service.py
class WatchlistApplicationService:
    def create_watchlist(self, command: CreateWatchlistCommand) -> WatchlistDTO:
        # Implementation
```

3. **Write integration tests**
```python
# tests/application/services/test_watchlist_application_service.py
def test_create_watchlist():
    # Test the full use case
```

## Best Practices

### 1. Domain Logic Stays in Domain Layer
```python
# Bad ❌ - Business logic in application layer
class StockApplicationService:
    def calculate_gain(self, stock_id: UUID):
        stock = self.repo.get(stock_id)
        return (stock.current_price - stock.purchase_price) / stock.purchase_price

# Good ✅ - Business logic in domain
class Stock(BaseEntity):
    def calculate_gain(self) -> Decimal:
        return (self.current_price - self.purchase_price) / self.purchase_price
```

### 2. Use Value Objects for Type Safety
```python
# Bad ❌ - Primitive obsession
def transfer_stocks(from_portfolio: str, to_portfolio: str, amount: float):
    pass

# Good ✅ - Rich types
def transfer_stocks(
    from_portfolio: PortfolioId, 
    to_portfolio: PortfolioId, 
    quantity: Quantity
):
    pass
```

### 3. Test Behavior, Not Implementation
```python
# Bad ❌ - Testing implementation details
def test_stock_internal_state():
    stock = Stock(...)
    assert stock._internal_field == "something"

# Good ✅ - Testing behavior
def test_stock_purchase_updates_portfolio_value():
    stock = Stock(...)
    original_value = stock.total_value
    stock.purchase(Quantity(10), Money(100))
    assert stock.total_value > original_value
```

### 4. Keep Tests Fast and Isolated
```python
# Bad ❌ - Depends on database
def test_save_stock():
    db = Database()
    repo = StockRepository(db)
    repo.save(stock)

# Good ✅ - Use test doubles
def test_save_stock():
    repo = Mock(spec=IStockRepository)
    service = StockApplicationService(repo)
    service.create_stock(command)
    repo.save.assert_called_once()
```

## Troubleshooting

### Common Issues

#### 1. Pre-commit Hook Failures
```bash
# See what's failing
make quality

# Fix formatting issues automatically
make format

# Fix remaining issues manually, then retry
git commit
```

#### 2. Import Errors
```bash
# Ensure you're in the project root
pwd  # Should show .../stockbook

# Check PYTHONPATH
echo $PYTHONPATH  # Should include project root

# Set if needed
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### 3. Type Checking Errors
```bash
# Run type checker with details
make typecheck

# Common fixes:
# - Add type annotations
# - Use Optional[T] for nullable values
# - Import from typing module
```

#### 4. Test Coverage Failures
```bash
# Check which files need coverage
python hooks/check-layer-coverage.py

# Generate HTML report
make coverage-report
# Open htmlcov/index.html in browser
```

### Getting Help

1. **Check Documentation**
   - `docs/ARCHITECTURE.md` - System design
   - `docs/DEVELOPMENT_ROADMAP.md` - Project status
   - `docs/TEST_WRITING_BEST_PRACTICES.md` - Testing guide

2. **Review Examples**
   - Look at existing entities in `src/domain/entities/`
   - Check test patterns in `tests/domain/`

3. **Ask Questions**
   - Create an issue on GitHub
   - Tag with "question" or "help wanted"

## Next Steps

1. **Run the test suite** to familiarize yourself with the codebase
2. **Pick a small task** from the roadmap to start contributing
3. **Follow TDD** - write tests first!
4. **Ask questions** - we're here to help

Welcome aboard! 🚀