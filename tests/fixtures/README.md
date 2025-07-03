# Infrastructure Test Fixtures

This directory contains comprehensive test fixtures for testing the infrastructure layer of StockBook using SQLAlchemy.

## Available Fixtures

### 1. SQLAlchemy In-Memory Engine (`sqlalchemy_in_memory_engine`)
Provides a fresh SQLAlchemy engine with in-memory SQLite database for each test:
```python
def test_database_operations(sqlalchemy_in_memory_engine):
    with sqlalchemy_in_memory_engine.connect() as conn:
        result = conn.execute(select(stock_table.c))
        # Engine is automatically disposed after test
```

### 2. SQLAlchemy Connection with Rollback (`sqlalchemy_connection`)
Provides a SQLAlchemy connection that automatically rolls back all changes after each test:
```python
def test_with_rollback(sqlalchemy_connection):
    # All operations on this connection are automatically rolled back
    stmt = insert(stock_table).values(symbol="AAPL", company_name="Apple Inc.")
    sqlalchemy_connection.execute(stmt)
    # Changes are rolled back after test completes
```

### 3. Mock Repositories
Pre-configured mock repositories for all domain interfaces:
- `mock_stock_repository`
- `mock_portfolio_repository`
- `mock_transaction_repository`
- `mock_target_repository`
- `mock_portfolio_balance_repository`
- `mock_journal_repository`
- `mock_unit_of_work`

Example:
```python
def test_service(mock_stock_repository, mock_unit_of_work):
    mock_stock_repository.get_by_symbol.return_value = test_stock
    service = StockApplicationService(mock_unit_of_work)
    # Test service logic
```

### 4. Stock Entity Builder (`stock_builder`)
Fluent builder for creating test stock entities:
```python
def test_stock_logic(stock_builder):
    stock = (
        stock_builder()
        .with_symbol("AAPL")
        .with_company_name("Apple Inc.")
        .with_sector("Technology")
        .build()
    )
```

Factory methods available:
- `StockBuilder.tech_stock()`
- `StockBuilder.financial_stock()`
- `StockBuilder.minimal_stock()`
- `StockBuilder.stock_with_id(stock_id)`

### 5. Sample Stocks (`sample_stocks`)
Provides a list of diverse pre-configured stock entities for testing.

### 6. SQLAlchemy Seeding Functions
- `seed_test_stocks_sqlalchemy(conn, stocks)` - Seed database with stock entities using SQLAlchemy
- `seed_test_portfolio_sqlalchemy(conn, name)` - Create a test portfolio using SQLAlchemy

## Usage Examples

### Testing with SQLAlchemy Fixtures

```python
from sqlalchemy import select
from src.infrastructure.persistence.tables.stock_table import stock_table

def test_repository_with_sqlalchemy(
    sqlalchemy_connection,
    sample_stocks,
    stock_builder
):
    # Seed test data using SQLAlchemy
    seed_test_stocks_sqlalchemy(sqlalchemy_connection, sample_stocks)
    
    # Create custom stock
    custom_stock = stock_builder().with_symbol("GOOGL").build()
    
    # Test repository with SQLAlchemy connection
    repo = SqlAlchemyStockRepository(sqlalchemy_connection)
    repo.create(custom_stock)
    
    # Verify using SQLAlchemy
    result = sqlalchemy_connection.execute(
        select(stock_table).where(stock_table.c.symbol == "GOOGL")
    ).fetchone()
    assert result.symbol == "GOOGL"
```

### Testing with Automatic Rollback

```python
def test_transaction_isolation(sqlalchemy_connection):
    # Insert test data
    stmt = insert(stock_table).values(
        id="test-123",
        symbol="TEST",
        company_name="Test Company"
    )
    sqlalchemy_connection.execute(stmt)
    
    # Verify it exists in this transaction
    result = sqlalchemy_connection.execute(
        select(stock_table.c).where(stock_table.c.id == "test-123")
    ).fetchone()
    assert result is not None
    
    # After test completes, all changes are automatically rolled back
```

### Testing with Mock Unit of Work

```python
def test_application_service(mock_unit_of_work, stock_builder):
    # Configure mock behavior
    test_stock = stock_builder.tech_stock()
    mock_unit_of_work.stocks.get_by_symbol.return_value = test_stock
    
    # Test service
    service = StockApplicationService(mock_unit_of_work)
    result = service.get_stock_by_symbol("MSFT")
    
    # Verify interactions
    mock_unit_of_work.stocks.get_by_symbol.assert_called_once()
    assert result == test_stock
```

## Migration from sqlite3 to SQLAlchemy

All fixtures now use SQLAlchemy Core for database operations. The legacy sqlite3-based fixtures have been removed to eliminate raw SQL usage and reduce technical debt. The only remaining raw SQL in the codebase is for SQLite PRAGMA commands, which SQLAlchemy doesn't support natively.

Benefits of SQLAlchemy fixtures:
- Type-safe query construction
- Automatic connection and transaction management
- Better integration with SQLAlchemy-based repositories
- Consistent API across all database operations
- Built-in support for connection pooling and isolation