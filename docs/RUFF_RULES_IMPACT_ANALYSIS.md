# Ruff Rules Impact Analysis

## Overview
This document analyzes the potential impact of adding additional ruff linting rules to the stockbook codebase. Each rule is evaluated for its potential violations, required effort to implement, and expected benefits.

## Proposed Rules Analysis

### ASYNC - Async Best Practices
**Impact**: Low
- **Estimated violations**: 0-5
- **Affected areas**: Currently no async code detected in codebase
- **Benefits**: Ensures proper async patterns when async code is added
- **Implementation effort**: Minimal - safe to enable preemptively
- **Recommendation**: Enable now to prevent future issues

### TCH - Type Checking Imports Optimization
**Impact**: High
- **Estimated violations**: 40-50 files
- **Affected areas**: Most modules with typing imports
- **Benefits**: 
  - Faster import times (typing imports moved to TYPE_CHECKING blocks)
  - Reduced runtime overhead
  - Cleaner dependency graph
- **Implementation effort**: Medium - requires wrapping imports in TYPE_CHECKING blocks
- **Example pattern to fix**:
  ```python
  # Before
  from typing import Optional, List
  from src.domain.entities import Stock
  
  # After
  from typing import TYPE_CHECKING
  if TYPE_CHECKING:
      from src.domain.entities import Stock
  ```
- **Recommendation**: Implement in Phase 2 due to widespread changes needed

### TID - Tidy Imports (Banned Imports)
**Impact**: Minimal
- **Estimated violations**: 0-2
- **Affected areas**: None detected
- **Benefits**: Prevents accidental use of problematic imports
- **Implementation effort**: None - codebase already compliant
- **Recommendation**: Enable immediately

### PTH - Use pathlib over os.path
**Impact**: Low
- **Estimated violations**: 4-6 files
- **Affected areas**: 
  - `src/infrastructure/persistence/database_factory.py`
  - Test files using os.path
  - Configuration files
- **Benefits**:
  - More pythonic and modern code
  - Better cross-platform compatibility
  - Cleaner path manipulation syntax
- **Implementation effort**: Low - straightforward replacements
- **Example pattern to fix**:
  ```python
  # Before
  import os
  db_path = os.path.join(os.path.dirname(__file__), 'data.db')
  
  # After
  from pathlib import Path
  db_path = Path(__file__).parent / 'data.db'
  ```
- **Recommendation**: Enable in Phase 1

### FLY - Static String Joins
**Impact**: Minimal
- **Estimated violations**: 2-3
- **Affected areas**: String concatenation in a few places
- **Benefits**: 
  - Better performance for string operations
  - More readable code
- **Implementation effort**: Trivial
- **Example pattern to fix**:
  ```python
  # Before
  message = "Error: " + str(error) + " occurred"
  
  # After
  message = f"Error: {error} occurred"
  ```
- **Recommendation**: Enable immediately

### PERF - Performance Anti-patterns
**Impact**: Low
- **Estimated violations**: 1-3
- **Affected areas**: Potential unnecessary list comprehensions or loops
- **Benefits**:
  - Better runtime performance
  - More efficient memory usage
- **Implementation effort**: Low
- **Common patterns detected**:
  - Unnecessary list() calls around comprehensions
  - Using try/except in hot loops
- **Recommendation**: Enable in Phase 1

### FURB - Modern Python Refurbishments
**Impact**: Medium
- **Estimated violations**: 5-10
- **Affected areas**: Older Python patterns throughout codebase
- **Benefits**:
  - More modern, idiomatic Python
  - Better readability
  - Leverages newer Python features
- **Implementation effort**: Low to medium
- **Example patterns**:
  ```python
  # Before
  if x == None:
  
  # After
  if x is None:
  ```
- **Recommendation**: Enable in Phase 2

### LOG - Logging Best Practices
**Impact**: Low
- **Estimated violations**: 5-10
- **Affected areas**: 
  - Test files with print statements
  - Scripts in scripts/ directory
  - Limited production logging usage
- **Benefits**:
  - Consistent logging patterns
  - Better log formatting
  - Avoid common logging mistakes
- **Implementation effort**: Low
- **Recommendation**: Enable in Phase 1 with per-file ignores for scripts

### RET - Return Statement Improvements
**Impact**: Medium
- **Estimated violations**: 20-30
- **Affected areas**: Functions with redundant return statements
- **Benefits**:
  - Cleaner, more concise code
  - Better readability
- **Implementation effort**: Low - mostly removing unnecessary returns
- **Example patterns**:
  ```python
  # Before
  def foo():
      if condition:
          return True
      else:
          return False
  
  # After
  def foo():
      return condition
  ```
- **Recommendation**: Enable in Phase 2

### SLF - Private Member Access
**Impact**: Medium
- **Estimated violations**: 10-20 (mostly in tests)
- **Affected areas**: 
  - Test files accessing private members
  - Some production code with private access
- **Benefits**:
  - Better encapsulation
  - Clearer API boundaries
- **Implementation effort**: Medium - may require refactoring tests
- **Recommendation**: Enable in Phase 3 with test exemptions

### SLOT - __slots__ Usage
**Impact**: High
- **Estimated violations**: 20-30 classes
- **Affected areas**: All entity and value object classes
- **Benefits**:
  - Memory efficiency
  - Faster attribute access
  - Prevents dynamic attribute addition
- **Implementation effort**: High - needs careful consideration
- **Risks**:
  - May break serialization/ORM compatibility
  - Inheritance becomes more complex
- **Recommendation**: Consider selectively, not as blanket rule

### TRY - Exception Handling Best Practices
**Impact**: Low
- **Estimated violations**: 2-5
- **Affected areas**: Error handling code
- **Benefits**:
  - More specific exception handling
  - Cleaner try/except blocks
  - Better error messages
- **Implementation effort**: Low
- **Common patterns**:
  - Too broad exception catching
  - Empty except blocks
  - Not re-raising appropriately
- **Recommendation**: Enable in Phase 2

## Implementation Plan

### Phase 1: Quick Wins (Immediate)
```toml
[tool.ruff.lint]
select = [
    # ... existing rules ...
    "TID",    # Tidy imports - no violations
    "FLY",    # Static string joins - 2 trivial fixes
    "PTH",    # Use pathlib - 4-6 easy updates
    "PERF",   # Performance - 1-3 simple fixes
]
```

### Phase 2: Medium Effort (Week 1-2)
```toml
[tool.ruff.lint]
select = [
    # ... phase 1 rules ...
    "ASYNC",  # Async best practices
    "LOG",    # Logging (with per-file ignores)
    "FURB",   # Modern Python
    "RET",    # Return statements
    "TRY",    # Exception handling
]

[tool.ruff.lint.per-file-ignores]
"scripts/*" = ["LOG"]  # Allow print in scripts
"tests/*" = ["LOG"]    # Allow print in tests
```

### Phase 3: Higher Effort (Week 3-4)
```toml
[tool.ruff.lint]
select = [
    # ... phase 2 rules ...
    "TCH",    # Type checking imports
    "SLF",    # Private member access
]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["SLF", "LOG"]  # Tests need private access
```

### Phase 4: Selective Application (Optional)
- **SLOT**: Apply manually to specific value objects where memory efficiency matters

## Expected Outcomes

### Benefits
1. **Performance**: 5-10% import time improvement (TCH), minor runtime improvements (PERF, FLY)
2. **Code Quality**: More modern, idiomatic Python throughout
3. **Maintainability**: Clearer patterns, better error handling
4. **Type Safety**: Better typing import patterns
5. **Future-Proofing**: Async-ready, modern Python features

### Effort Summary
- **Total estimated violations**: 100-150 across all rules
- **Implementation time**: 2-4 weeks for full adoption
- **Risk level**: Low to medium (highest risk is SLOT rule)

## Recommendations

1. **Start with Phase 1** immediately - these are easy wins with minimal risk
2. **Run Phase 2** after a week to build momentum
3. **Phase 3** requires more coordination - plan for a dedicated refactoring sprint
4. **SLOT rule** should be evaluated case-by-case, not applied globally
5. **Monitor CI/CD** times after TCH implementation to quantify import speed improvements
6. **Document exceptions** with clear comments when using `# noqa` directives

## Migration Commands

For each phase, use these commands to verify and fix:

```bash
# Check current violations
ruff check --select RULE_CODE .

# Auto-fix where possible
ruff check --select RULE_CODE --fix .

# Run full quality check
make check
```

## Conclusion

The proposed ruff rules will enhance code quality with manageable implementation effort. The phased approach allows gradual adoption while maintaining development velocity. Most rules offer clear benefits with minimal disruption to the existing codebase.