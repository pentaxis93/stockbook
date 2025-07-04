# Code Quality Standards and Layer-Specific Configuration

This document outlines the code quality standards enforced in the Stockbook project and the rationale behind layer-specific configurations.

## Overview

The project uses a comprehensive quality pipeline with:
- **Black** for code formatting
- **isort** for import sorting  
- **Pylint** for code quality with layer-specific rules
- **Pyright** in strict mode for type checking
- **Flake8** for cognitive complexity limits
- **Bandit** for security scanning
- **Pydocstyle** and **docstr-coverage** for documentation standards
- **Import-linter** for architectural boundaries
- **pytest** with 100% coverage requirement

## Layer-Specific Pylint Configuration

### Domain Layer
**Configuration**: Strictest rules with minimal exceptions
```bash
# No additional disables beyond global config
```

**Rationale**: The domain layer represents core business logic and should maintain the highest code quality standards. Rich domain models may legitimately have many public methods, which is already allowed globally.

### Application Layer  
**Configuration**: 
```bash
--disable=too-many-arguments
```

**Rationale**: 
- Command handlers and DTOs often require many parameters to encapsulate complex operations
- This is a legitimate pattern in CQRS architectures where commands carry all necessary data

### Infrastructure Layer
**Configuration**:
```bash
--disable=too-many-locals
```

**Rationale**:
- Database configuration and connection setup often requires managing multiple local variables
- Repository implementations may need to handle complex SQL query construction
- This complexity is inherent to infrastructure concerns

### Presentation Layer
**Configuration**:
```bash
--disable=too-many-locals,too-many-arguments,too-many-statements,too-many-branches
```

**Rationale**:
- API endpoints often need to handle multiple query parameters and request validation
- Complex request/response transformations may require additional local variables
- Error handlers need multiple conditional branches for proper HTTP status mapping
- Multiple branches are often required to handle different error types appropriately
- This is acceptable at the boundary layer where external concerns are translated

### Dependency Injection
**Configuration**: Inline disables with documented rationale

**Rationale**:
- DI containers have inherent complexity in managing dependencies and resolution logic
- The complexity provides a clean abstraction over the underlying DI framework
- Each disable is documented at the point of use

### Test Code
**Configuration**:
```bash
--disable=too-few-public-methods,protected-access,redefined-outer-name,
          unused-argument,attribute-defined-outside-init,too-many-lines,
          duplicate-code,import-outside-toplevel
--max-locals=10
--max-statements=20
```

**Rationale**:
- Tests often need more setup code and assertions
- Pytest fixtures naturally redefine names
- Test isolation may require dynamic imports
- Accessing protected members is necessary for thorough testing
- Test patterns often repeat (legitimate duplication)

## Global Standards

### Balanced Complexity Limits
- **Cognitive Complexity**: 8 (enforced by Flake8)
- **Max args**: 7 (allows rich constructors and commands)
- **Max locals**: 10 (allows complex domain operations with intermediate values)
- **Max branches**: 6 (allows proper error handling)
- **Max statements**: 15 (allows complete domain operations without artificial splitting)
- **Max nested blocks**: 3 (prevents deep nesting)
- **Max module lines**: 500 (prevents God modules)
- **Min public methods**: 1 (allows single-method classes)
- **Docstring coverage**: 100%
- **Test coverage**: 100%

Test-specific limits:
- **Max locals**: 15 (tests need more setup variables)
- **Max statements**: 30 (comprehensive test scenarios)

### Philosophy
These limits are balanced to prevent truly problematic complexity while allowing:
- Rich domain models with multiple attributes
- Comprehensive error handling with proper HTTP status mapping
- Commands and DTOs that handle multiple fields
- Complete business operations without artificial splitting

## Type Safety

All code must pass **Pyright** in strict mode. We use Pyright exclusively for type checking to avoid conflicts and redundancy between multiple type checkers.

Type ignore comments (`# type: ignore`) are used sparingly for:
- SQLAlchemy internals where type stubs are incomplete
- Dependency injector framework internals
- Test fixtures with dynamic behavior

Each type ignore should be documented with a comment explaining why it's necessary.

## Security Standards

- **Bandit** scans all production code with no skipped tests
- All severity levels are reported
- No hardcoded secrets or unsafe practices allowed

## Import Architecture

Enforced layered architecture:
- Domain layer has no dependencies
- Application depends only on Domain
- Infrastructure depends on Domain and Application
- Presentation depends on all layers

## Refactoring Opportunities

Based on analysis, the following areas present genuine refactoring opportunities:

1. **Complex Integration Tests**: Break down into smaller, focused tests
2. **Test Data Builders**: Implement builder pattern for test data setup
3. **Extract Helper Methods**: Reduce complexity in tests by extracting common setup

These improvements should be addressed incrementally while maintaining the quality standards defined above.