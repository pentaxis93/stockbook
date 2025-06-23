# Test Writing Best Practices

## Overview

This document captures the essential best practices learned during our successful journey to achieve 100% domain layer test coverage. These practices ensure meaningful tests, strict type safety, and maintainable code quality while avoiding common pitfalls.

## Core Principles

### 1. Write Meaningful Tests, Not Coverage Tests

**❌ BAD: Testing for coverage numbers**
```python
def test_some_method_exists(self) -> None:
    """Test that method exists."""
    obj = SomeClass()
    obj.some_method()  # Just calling to get coverage
```

**✅ GOOD: Testing business logic and behavior**
```python
def test_portfolio_balance_calculates_net_change_correctly(self) -> None:
    """Should calculate net change between current and previous balance."""
    current_balance = PortfolioBalanceEntity(
        portfolio_id="portfolio-1",
        balance_date=date(2024, 1, 15),
        final_balance=Money(Decimal("10000.00")),
        index_change=IndexChange(2.5),
    )
    
    net_change = current_balance.calculate_net_change(Money(Decimal("9500.00")))
    assert net_change == Money(Decimal("500.00"))
```

### 2. Test-Driven Development (TDD) Approach

Always follow the TDD cycle:

1. **Write failing tests first** - Define expected behavior
2. **Allow tests to fail** - Never skip or comment out failing tests
3. **Implement minimal code** to make tests pass
4. **Refactor** for maintainability

### 3. Comprehensive Equality Testing Pattern

For domain entities and value objects, always test equality with different types to achieve complete coverage:

```python
def test_entity_equality_with_non_matching_types(self) -> None:
    """Test equality returns False for non-Entity objects."""
    entity = SomeEntity(id="test-id", value="test")
    
    # Test against different types - covers return False branches
    assert entity != "string"
    assert entity != 123
    assert entity != None
    assert entity != {"id": "test-id"}
    assert entity != []
```

## Critical Rules

### Never Use `--no-verify`

**🚨 NEVER BYPASS PRE-COMMIT HOOKS**

```bash
# ❌ NEVER DO THIS
git commit --no-verify -m "bypass hooks"

# ✅ ALWAYS DO THIS
git commit -m "proper commit"
# If hooks fail, fix the code, don't bypass
```

**Why this matters:**
- Pre-commit hooks ensure code quality
- Bypassing them introduces technical debt
- It violates the team's quality standards
- Problems compound over time

**When hooks fail:**
1. Read the error messages carefully
2. Fix the underlying code issues
3. Re-run the commit process
4. Never use shortcuts

### Strict Type Safety from the Start

**Always begin with type safety:**

```python
# ✅ Explicit type annotations
def calculate_portfolio_value(
    transactions: List[TransactionEntity],
    current_prices: Dict[str, Money]
) -> Money:
    """Calculate total portfolio value with explicit types."""
    total: Money = Money(Decimal("0.00"))
    # Implementation...
    return total
```

**Never retrofit types later:**
- Use `pyright --strict` from day one
- Add type annotations to all function signatures
- Use explicit type annotations where inference isn't clear

## Coverage Configuration Best Practices

### Strategic Coverage Exclusions

Use `.coveragerc` or `pyproject.toml` to exclude legitimate patterns:

```ini
# .coveragerc
[report]
exclude_lines = 
    # Abstract methods - these are contracts, not implementation
    @(abc\.)?abstractmethod
    
    # Defensive programming patterns that shouldn't be tested
    ^\s*raise\s*$
    super\(\).__setattr__
    except.*:\s*$
    
    # Standard exclusions
    pragma: no cover
    if __name__ == .__main__.:
```

**Critical Learning: Avoid Overly Broad Exclusions**

❌ **NEVER exclude these patterns globally:**
```ini
return False  # Too broad - often legitimate control flow
return None   # Too broad - often legitimate control flow
```

✅ **Instead, use inline exclusions for specific cases:**
```python
# For truly untestable defensive code only
if sector is None:
    return None  # pragma: no cover
```

**What to exclude:**
- Abstract method `pass` statements
- Defensive `raise` statements without logic
- Standard boilerplate code
- Debug-only code paths

**What NOT to exclude:**
- Business logic with `return False` or `return None`
- Error handling with meaningful behavior
- Validation logic that returns boolean values
- State changes that return None
- Legitimate control flow statements

### Layer-Specific Coverage Enforcement

Implement different coverage thresholds by architectural layer:

```yaml
# hooks/layer-coverage.yaml
layers:
  domain:
    path: src/domain
    threshold: 100  # Strictest for business logic
    description: "Core business logic - requires 100% coverage"
    
  application:
    path: src/application  
    threshold: 90   # High for use cases
    
  infrastructure:
    path: src/infrastructure
    threshold: 85   # Moderate for integrations
    
  presentation:
    path: src/presentation
    threshold: 75   # Lower for UI code
```

## Code Quality Integration

### Pre-Commit Pipeline Components

Ensure your pre-commit hooks include:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: black              # Code formatting
      - id: isort              # Import sorting  
      - id: pyright            # Type checking
      - id: pylint             # Code quality
      - id: pytest             # Test execution
      - id: layer-coverage     # Layer-specific coverage
      - id: bandit             # Security scanning
```

### Import Organization

**❌ BAD: Local imports that duplicate top-level imports**
```python
# At top of file
from src.domain.value_objects import Money

class TestSomething:
    def test_method(self) -> None:
        from src.domain.value_objects import Money  # ❌ Duplicate!
```

**✅ GOOD: Centralized imports**
```python
# At top of file
from src.domain.value_objects import Money, IndexChange, TargetStatus

class TestSomething:
    def test_method(self) -> None:
        # Use Money directly - already imported
        money = Money(Decimal("100.00"))
```

## Test Organization Patterns

### Test Class Structure

```python
class TestEntityName:
    """Test EntityName domain entity with value objects and business logic."""
    
    def test_create_entity_with_valid_data(self) -> None:
        """Should create entity with valid input data."""
        # Arrange, Act, Assert pattern
        
    def test_entity_validation_rules(self) -> None:
        """Should enforce business validation rules."""
        # Test boundary conditions and business rules
        
    def test_entity_equality_and_hash(self) -> None:
        """Should implement equality and hash correctly."""
        # Comprehensive equality testing
        
    def test_entity_string_representations(self) -> None:
        """Should have proper string representations."""
        # Test __str__ and __repr__
        
    def test_entity_immutability(self) -> None:
        """Should enforce immutability constraints."""
        # Test that value objects can't be modified
```

### Test Naming Conventions

- **Use descriptive names** that explain expected behavior
- **Start with action word**: `test_calculate_`, `test_validate_`, `test_create_`
- **Include context**: `test_create_entity_with_invalid_data_raises_error`
- **Describe expected outcome**: `test_equality_returns_false_for_different_types`

## Common Pitfalls to Avoid

### 1. Testing Implementation Details
```python
# ❌ BAD: Testing internal implementation
def test_private_method_called(self):
    obj = SomeClass()
    obj.public_method()
    assert obj._private_method_called  # Testing internals

# ✅ GOOD: Testing behavior
def test_public_method_produces_expected_result(self):
    obj = SomeClass()
    result = obj.public_method()
    assert result == expected_value  # Testing observable behavior
```

### 2. Brittle Test Data
```python
# ❌ BAD: Hard-coded magic values
def test_calculation(self):
    result = calculate_fee(100, 0.05)  # What do these numbers mean?
    assert result == 5

# ✅ GOOD: Meaningful test data
def test_fee_calculation_with_standard_rate(self):
    principal = Money(Decimal("100.00"))
    standard_rate = Decimal("0.05")  # 5% standard fee
    
    fee = calculate_fee(principal, standard_rate)
    
    assert fee == Money(Decimal("5.00"))
```

### 3. Missing Edge Cases
Always test:
- **Boundary values**: minimum, maximum, zero, negative
- **Empty collections**: empty lists, empty strings, None values
- **Error conditions**: invalid input, constraint violations
- **Type mismatches**: wrong types passed to methods

## Performance Considerations

### Parallel Test Execution
```python
# pytest configuration for performance
[tool.pytest.ini_options]
addopts = [
    "--dist=worksteal",     # Better load balancing
    "--maxfail=5",          # Fail fast
    "-n=auto",              # Use all CPU cores
]
```

### Test Data Factories
Use factories for complex test data:

```python
class EntityFactory:
    @staticmethod
    def create_portfolio_balance(
        portfolio_id: str = "default-portfolio",
        balance: Decimal = Decimal("1000.00"),
        **kwargs
    ) -> PortfolioBalanceEntity:
        return PortfolioBalanceEntity(
            portfolio_id=portfolio_id,
            balance_date=kwargs.get("balance_date", date.today()),
            final_balance=Money(balance),
            index_change=kwargs.get("index_change", IndexChange(0.0)),
            **kwargs
        )
```

## Documentation Standards

### Test Documentation
```python
def test_portfolio_rebalancing_with_market_volatility(self) -> None:
    """
    Should rebalance portfolio correctly during high market volatility.
    
    Given: A portfolio with mixed asset allocation
    When: Market volatility exceeds threshold during rebalancing
    Then: Should apply conservative rebalancing strategy
    And: Should preserve risk tolerance settings
    """
```

### Coverage Reports
Include coverage reports in CI/CD:
- Generate HTML reports for detailed analysis
- Set up layer-specific coverage badges
- Track coverage trends over time
- Fail builds on coverage regression

## Migration Strategy

### For Existing Codebases

1. **Start with domain layer** - highest business value
2. **Set achievable initial targets** - gradually increase thresholds
3. **Focus on business logic first** - not trivial getters/setters
4. **Refactor while adding tests** - improve design during testing
5. **Document patterns** - establish team conventions

### Team Adoption

1. **Training sessions** on TDD and test patterns
2. **Code review standards** emphasizing test quality
3. **Pair programming** for knowledge transfer
4. **Regular retrospectives** to improve practices
5. **Tooling investment** in test infrastructure

## Real-World Coverage Examples

### Case Study: Achieving 100% Coverage Responsibly

**Problem**: Initial attempt to achieve 100% coverage used overly broad exclusions:
```ini
# ❌ BAD - Too broad exclusions in .coveragerc
exclude_lines = 
    return False
    return None
```

**Solution**: Removed broad exclusions and used targeted inline exclusions:
```python
# ✅ GOOD - Targeted inline exclusion for defensive code
@staticmethod
def _normalize_sector(sector: Optional[str]) -> Optional[str]:
    """Normalize sector."""
    if sector is None:
        return None  # pragma: no cover  # Defensive, hard to test
    normalized = sector.strip()
    return normalized if normalized else None
```

**Results**: 
- Domain layer: 100% coverage (all legitimate business logic tested)
- Application layer: 100% coverage (1 inline exclusion for defensive code)
- No false coverage inflation
- All meaningful code paths properly tested

### When to Use `# pragma: no cover`

**Appropriate uses:**
```python
# Defensive programming that's hard to trigger in tests
if unexpected_none_value is None:
    return None  # pragma: no cover

# Platform-specific code that can't be tested in CI
if sys.platform == "win32":  # pragma: no cover
    return windows_specific_implementation()
```

**Inappropriate uses:**
```python
# ❌ Don't exclude business logic
def calculate_fee(amount: Money) -> Money:
    if amount.is_zero():
        return Money.zero()  # This SHOULD be tested!
    return amount * Decimal("0.05")

# ❌ Don't exclude error conditions
def validate_stock_symbol(symbol: str) -> None:
    if not symbol.strip():
        raise ValueError("Symbol required")  # This SHOULD be tested!
```

## Conclusion

Quality testing is not about achieving arbitrary coverage numbers—it's about building confidence in your codebase through meaningful validation of business logic and behavior. By following these practices, you'll create a robust test suite that serves as both documentation and safety net for your domain logic.

Remember:
- **Tests are documentation** of expected behavior
- **Coverage is a tool, not a goal** - use it to find gaps, not to chase numbers
- **Use targeted exclusions, not broad patterns** - each exclusion should be justified
- **Type safety and testing go hand-in-hand** - both contribute to code quality
- **Never compromise on quality** - shortcuts always cost more in the long run

The investment in proper testing practices pays dividends in reduced bugs, easier refactoring, and increased developer confidence. Build this foundation correctly from the start, and your team will benefit throughout the entire project lifecycle.