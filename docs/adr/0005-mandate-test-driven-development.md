# Mandate Test-Driven Development

* Status: accepted
* Deciders: Development team
* Date: 2025-01-11

## Context and Problem Statement

StockBook handles critical financial data and calculations where accuracy is paramount. Business logic errors could lead to incorrect portfolio valuations, wrong transaction records, or flawed investment decisions. We need a development approach that ensures code correctness, prevents regressions, and maintains high quality standards. How should we structure our development process to guarantee that all business logic is thoroughly tested and reliable?

## Decision Drivers

* **Financial Accuracy**: Errors in calculations can have serious financial consequences
* **Business Logic Complexity**: Portfolio calculations and risk assessments are intricate
* **Regression Prevention**: Changes must not break existing functionality
* **Code Confidence**: Developers need certainty that their changes are correct
* **Documentation**: Tests serve as living documentation of expected behavior
* **Refactoring Safety**: Need to refactor with confidence as the system evolves
* **Quality Gates**: Automated enforcement of quality standards

## Considered Options

* **Test-Driven Development (TDD)**: Write tests before implementation
* **Test-After Development**: Write tests after implementing features
* **Behavior-Driven Development (BDD)**: Use Gherkin syntax for test scenarios
* **Property-Based Testing**: Generate test cases based on properties
* **Manual Testing Only**: Rely on manual QA processes
* **Selective Testing**: Test only critical paths

## Decision Outcome

Chosen option: "Test-Driven Development (TDD)", because it forces us to think about requirements before implementation, ensures comprehensive test coverage, and creates a safety net for refactoring. This approach is particularly crucial for financial calculations where correctness is non-negotiable.

### Positive Consequences

* **Design Quality**: Writing tests first improves API design
* **Complete Coverage**: Every line of business logic is tested
* **Living Documentation**: Tests document expected behavior
* **Refactoring Confidence**: Safe to improve code without breaking functionality
* **Bug Prevention**: Catch issues before they reach production
* **Clear Requirements**: Forces clarity about what code should do
* **Fast Feedback**: Know immediately when something breaks

### Negative Consequences

* **Initial Slowdown**: Writing tests first takes more time upfront
* **Learning Curve**: Team must master TDD practices
* **Test Maintenance**: Tests need updates when requirements change
* **Over-testing Risk**: Possibility of testing implementation details

## Pros and Cons of the Options

### Test-Driven Development (TDD)

Write tests first, then implementation, then refactor (Red-Green-Refactor cycle).

* Good, because forces thinking about requirements first
* Good, because ensures 100% test coverage
* Good, because improves design through test-first approach
* Good, because provides immediate feedback
* Good, because prevents scope creep
* Bad, because slower initial development
* Bad, because requires discipline and practice

### Test-After Development

Implement features first, then write tests to verify them.

* Good, because familiar to most developers
* Good, because faster initial implementation
* Bad, because often results in incomplete coverage
* Bad, because tests tend to match implementation, not requirements
* Bad, because harder to achieve full coverage retroactively
* Bad, because design issues discovered late

### Behavior-Driven Development (BDD)

Write tests in business-readable language using Given-When-Then format.

* Good, because readable by non-technical stakeholders
* Good, because focuses on behavior not implementation
* Good, because promotes collaboration
* Bad, because adds complexity with Gherkin syntax
* Bad, because can be verbose for simple tests
* Bad, because requires additional tooling

### Property-Based Testing

Generate test inputs based on properties that should hold true.

* Good, because finds edge cases automatically
* Good, because tests invariants comprehensively
* Bad, because harder to understand failures
* Bad, because not suitable for all types of tests
* Bad, because requires different mindset
* Bad, because limited tooling in Python

### Manual Testing Only

Rely on human testers to verify functionality.

* Good, because no test code to maintain
* Good, because can test user experience
* Bad, because slow and expensive
* Bad, because not repeatable
* Bad, because prone to human error
* Bad, because cannot catch regressions quickly

### Selective Testing

Test only critical or complex parts of the system.

* Good, because less test code to write
* Good, because focuses effort on high-risk areas
* Bad, because leaves gaps in coverage
* Bad, because "critical" is subjective
* Bad, because non-critical code can have critical bugs
* Bad, because difficult to maintain standards

## Implementation Details

Our TDD implementation includes:

### TDD Cycle

1. **Red Phase**: Write a failing test
   ```python
   def test_stock_creation_with_valid_data():
       # Arrange
       symbol = StockSymbol("AAPL")
       company = CompanyName("Apple Inc.")
       
       # Act & Assert
       stock = Stock(symbol=symbol, company=company, ...)
       assert stock.symbol == symbol
       assert stock.company == company
   ```

2. **Green Phase**: Write minimal code to pass
   ```python
   class Stock(Entity):
       def __init__(self, symbol: StockSymbol, company: CompanyName, ...):
           self.symbol = symbol
           self.company = company
   ```

3. **Refactor Phase**: Improve code while keeping tests green

### Coverage Requirements by Layer

| Layer | Required Coverage | Rationale |
|-------|------------------|-----------|
| Domain | 100% | Core business logic must be bulletproof |
| Application | 90% | Use cases need comprehensive testing |
| Infrastructure | 100% | Data persistence must be reliable |
| Presentation | 100% | API contracts must be tested |

### Enforcement Mechanisms

#### Pre-commit Hooks
```yaml
- repo: local
  hooks:
    - id: domain-coverage
      name: Check domain coverage
      entry: pytest tests/domain --cov=src/domain --cov-fail-under=100
      language: system
      pass_filenames: false
```

#### CI/CD Pipeline
```yaml
test:
  script:
    - make test  # Runs all tests with coverage
    - make coverage-report  # Generates detailed report
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

### Test Organization

```
tests/
├── domain/
│   ├── entities/
│   │   ├── test_stock.py         # Stock entity tests
│   │   ├── test_portfolio.py     # Portfolio entity tests
│   │   └── test_transaction.py   # Transaction entity tests
│   ├── value_objects/
│   │   ├── test_money.py         # Money value object tests
│   │   └── test_quantity.py      # Quantity value object tests
│   └── services/
│       └── test_portfolio_calculation_service.py
├── application/
│   ├── services/
│   │   └── test_stock_application_service.py
│   └── commands/
│       └── test_create_stock_command.py
├── infrastructure/
│   └── repositories/
│       └── test_stock_repository.py
└── presentation/
    └── api/
        └── test_stock_endpoints.py
```

### Testing Patterns

#### Arrange-Act-Assert (AAA)
```python
def test_portfolio_value_calculation():
    # Arrange
    portfolio = Portfolio(name="My Portfolio")
    stock = Stock(symbol="AAPL", price=Money(150.00))
    transaction = Transaction(stock=stock, quantity=10)
    
    # Act
    total_value = portfolio.calculate_total_value([transaction])
    
    # Assert
    assert total_value == Money(1500.00)
```

#### Test Builders for Complex Objects
```python
class StockBuilder:
    def __init__(self):
        self._symbol = "AAPL"
        self._company = "Apple Inc."
        self._sector = "Technology"
    
    def with_symbol(self, symbol: str) -> 'StockBuilder':
        self._symbol = symbol
        return self
    
    def build(self) -> Stock:
        return Stock(
            symbol=StockSymbol(self._symbol),
            company=CompanyName(self._company),
            sector=Sector(self._sector)
        )

# Usage in tests
stock = StockBuilder().with_symbol("GOOGL").build()
```

### Test Categories

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test component interactions
3. **Contract Tests**: Verify API contracts
4. **Property Tests**: Test invariants with generated data

### Continuous Improvement

- Regular test review sessions
- Refactor tests when they become brittle
- Monitor test execution time
- Maintain test/production code ratio

## Links

* Supports [ADR-0002: Use Clean Architecture](0002-use-clean-architecture.md)
* Enables [ADR-0003: Implement Domain-Driven Design](0003-implement-domain-driven-design.md)
* References: "Test Driven Development: By Example" by Kent Beck
* References: "Growing Object-Oriented Software, Guided by Tests" by Steve Freeman and Nat Pryce