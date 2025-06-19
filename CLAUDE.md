# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Approach

- Always use the TDD approach by building comprehensive test coverage defining all expected behavior before writing a single line of implementation code.
  - Write tests first to define the expected behavior.
  - The tests should fail. At this point, simply allow the tests to fail, rather than skipping them or commenting them out.
  - Implement the code to make the tests pass.
  - Refactor the code to make it more readable.
- When you implement a temporary fix or defer a task in your code—like simplifying a class or postponing tests—document it with a clear TODO or FIXME comment that explains what needs to be done and why. This ensures the task isn't forgotten and can be revisited during code reviews or sprint planning.

## Essential Commands

### Code Quality (run before every commit)
```bash
pytest                    # Run all tests with coverage (829 tests, 80% minimum)
pytest -m "not slow"     # Skip slow tests during development
pylint .                 # Lint all source code
black .                  # Format code
isort .                  # Sort imports
pyright                  # Type checking (basic mode, some files excluded)
```

### Development Workflow
```bash
streamlit run app.py                    # Run the application
pre-commit install                      # Set up quality checks
pre-commit run --all-files             # Run all quality checks manually
pytest --cov-report=html:htmlcov       # Generate HTML coverage report
```

### Testing Commands
```bash
pytest tests/domain/                    # Test domain layer only
pytest tests/application/               # Test application layer only
pytest -k "test_stock"                 # Run specific test patterns
pytest --tb=short                      # Shorter tracebacks for debugging
```

## Architecture Overview

**StockBook** implements **Clean Architecture** with **Domain-Driven Design** principles in a **4-layer structure**:

### Layer Dependencies (Dependency Inversion)
- **Domain** ← Application ← Infrastructure/Presentation
- **Shared Kernel** ← All layers (common value objects, exceptions, interfaces)
- **Dependency Injection** wires everything together with IoC container

### 1. Domain Layer (`domain/`)
**Purpose**: Core business logic, independent of external concerns
- **Entities**: Rich domain objects with business behavior (`StockEntity`, `PortfolioEntity`)
- **Value Objects**: Immutable types in `domain/value_objects/` 
- **Domain Services**: Complex business logic (`PortfolioCalculationService`, `RiskAssessmentService`)
- **Repository Interfaces**: Abstract data access contracts

### 2. Application Layer (`application/`)
**Purpose**: Use cases and workflow orchestration
- **Application Services**: Coordinate domain operations (`StockApplicationService`)
- **Commands**: Operation requests with validation
- **DTOs**: Data transfer between layers

### 3. Infrastructure Layer (`infrastructure/`)
**Purpose**: External concerns (database, file system)
- **Repository Implementations**: SQLite-based data access
- **Unit of Work**: Transaction management (`infrastructure/persistence/`)
- **Database Connections**: Data access infrastructure

### 4. Presentation Layer (`presentation/`)
**Purpose**: User interface and external APIs
- **Controllers**: Handle user requests (`StockController`)
- **View Models**: UI data structures
- **Adapters**: Framework-specific integration (Streamlit)
- **Coordinators**: UI workflow management

### Shared Kernel (`shared_kernel/`)
**Cross-cutting concerns used by all layers:**
- **Value Objects**: `Money`, `Quantity` with arithmetic operations
- **Domain Events**: Event infrastructure with serialization
- **Domain Exceptions**: Rich exception hierarchy with context
- **Common Interfaces**: Unit of Work pattern, base repositories

### Dependency Injection (`dependency_injection/`)
**Professional IoC container:**
- **DIContainer**: Service lifetime management (singleton/transient)
- **CompositionRoot**: Central dependency configuration
- **Clean Integration**: All layers properly wired with dependency inversion

## Key Architectural Principles

1. **Clean Architecture Compliance**: No dependency violations between layers
2. **Domain-Driven Design**: Rich domain models with business logic encapsulation
3. **Dependency Inversion**: All dependencies point inward toward domain
4. **Test-Driven Development**: 829 tests with comprehensive coverage
5. **Type Safety**: Strong typing throughout (except some Streamlit integration files)
6. **Professional DI**: Enterprise-level dependency injection patterns

## File Organization Patterns

- **Tests mirror source structure**: `tests/domain/entities/test_stock_entity.py` mirrors `domain/entities/stock_entity.py`
- **Layer separation**: Each layer has its own namespace and responsibilities
- **Interface segregation**: Repository interfaces in domain, implementations in infrastructure
- **Value object centralization**: Common value objects in `shared_kernel/value_objects/`

## Current Development Status

**Phase**: Architecture Complete, Integration Phase
- ✅ **Clean Architecture**: Complete 4-layer implementation
- ✅ **Shared Kernel & DDD**: Value objects, domain events, rich entities
- ✅ **Professional DI**: IoC container with composition root
- ⚠️ **Critical Issue**: Database connection architecture needs type safety refactoring
- 📋 **Next**: Fix connection interface pattern, re-enable full type checking

## Quality Standards

- **Test Coverage**: Minimum 80% (currently 83.8% pass rate)
- **Type Checking**: Basic mode with pyright (some Streamlit files excluded)
- **Code Formatting**: Black (88 character line length)
- **Import Sorting**: isort with black profile
- **Linting**: Pylint with architectural layer-specific configurations

## Important Notes

- **Database**: SQLite-based with comprehensive schema
- **UI Framework**: Streamlit for web interface
- **Legacy Code**: `app.py` is legacy main file, clean architecture layers are primary
- **Pre-commit Hooks**: Automated quality checks on every commit
- **Documentation**: Always update ROADMAP.md, TECHNICAL_DEBT.md, and README.md with changes

## Git Workflow

- Always run `pytest`, `pylint`, `pyright`, `black`, and `isort` and fix all issues before making a commit
- When writing git commit messages, omit all references to authorship, and especially omit references to Claude
- Always update the ROADMAP.md, TECHNICAL_DEBT.md, and README.md files in the project root with the latest changes