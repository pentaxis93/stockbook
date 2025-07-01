# Infrastructure Test Fixtures

This directory contains comprehensive test fixtures for testing the infrastructure layer of StockBook.

## Available Fixtures

### 1. In-Memory SQLite Database (`in_memory_db`)
Provides a fresh SQLite database in memory for each test:
```python
def test_database_operations(in_memory_db):
    cursor = in_memory_db.cursor()
    cursor.execute("INSERT INTO stocks ...")
```

### 2. Transaction Rollback (`transaction_rollback`)
Automatically rolls back all database changes after each test:
```python
def test_with_rollback(transaction_rollback):
    conn = transaction_rollback
    conn.execute("INSERT INTO stocks ...")
    # Changes are automatically rolled back after test
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
- `StockEntityBuilder.tech_stock()`
- `StockEntityBuilder.financial_stock()`
- `StockEntityBuilder.minimal_stock()`

### 5. Sample Stocks (`sample_stocks`)
Provides a list of diverse pre-configured stock entities for testing.

### 6. Helper Functions
- `seed_test_stocks(conn, stocks)` - Seed database with stock entities
- `seed_test_portfolio(conn, name)` - Create a test portfolio
- `db_transaction(conn)` - Context manager for database transactions

## Usage Example

```python
def test_repository_implementation(
    in_memory_db,
    sample_stocks,
    stock_builder
):
    # Seed test data
    seed_test_stocks(in_memory_db, sample_stocks)
    
    # Create custom stock
    custom_stock = stock_builder().with_symbol("GOOGL").build()
    
    # Test repository
    repo = SqliteStockRepository(in_memory_db)
    repo.create(custom_stock)
    
    # Verify
    result = repo.get_by_symbol(StockSymbol("GOOGL"))
    assert result == custom_stock
```