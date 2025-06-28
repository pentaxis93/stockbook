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
    threshold: 100  # Complete coverage for infrastructure integrations
    
  presentation:
    path: src/presentation
    threshold: 75   # Lower for UI code
