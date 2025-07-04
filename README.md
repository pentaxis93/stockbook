# StockBook

Personal stock trading tracker for managing family investments with portfolio analytics and performance monitoring.

## Overview

StockBook is a modern application built with Python to help track personal and family stock investments. It provides a clean architecture foundation for recording trades, monitoring portfolio performance, and analyzing investment history.

## Current Status 🚧

**Phase 1 Complete**: The project has a solid foundation with Domain and Application layers fully implemented following Clean Architecture and Domain-Driven Design principles. The Infrastructure and Presentation layers are planned for Phase 2.

### What's Working Now
- ✅ Rich domain model with entities and value objects
- ✅ Business logic and domain services
- ✅ Application layer with commands and DTOs
- ✅ Professional dependency injection container
- ✅ Comprehensive test suite (100% coverage on critical layers)
- ✅ Development tooling (Docker, Makefile, pre-commit hooks)

### What's Coming Next
- 🔄 Infrastructure layer (database, repositories)
- 🔄 REST API with FastAPI
- 🔄 Web UI
- 🔄 Real-time stock data integration

## Features (Planned)

- 📊 Portfolio overview dashboard
- 📝 Trade entry and management
- 📈 Performance tracking and analytics
- 💰 Profit/loss calculations
- 📅 Historical data analysis
- 👨‍👩‍👧‍👦 Multi-account support for family members
- 🔒 Secure authentication and authorization
- 📱 Responsive web interface

## Tech Stack

### Core Technologies
- **Python 3.13** - Core programming language with full type safety
- **Clean Architecture** - Layered architecture with dependency inversion
- **Domain-Driven Design** - Rich domain models with business logic
- **Test-Driven Development** - 100% test coverage on business logic

### Current Implementation
- **Domain Layer** - Entities, value objects, domain services, and repository interfaces
- **Application Layer** - Use cases, commands, and data transfer objects
- **Dependency Injection** - Professional IoC container with composition root
- **Testing** - Pytest with layer-specific coverage requirements
- **Code Quality** - Ruff for fast, comprehensive linting (replaced flake8, pylint, isort, pydocstyle, bandit)

### Planned Technologies
- **FastAPI** - Modern async web framework (Phase 2)
- **SQLite/PostgreSQL** - Database persistence (Phase 2)
- **SQLAlchemy** - ORM with unit of work pattern (Phase 2)
- **Pydantic** - Data validation and serialization
- **Docker** - Containerization for deployment

## Installation

### Prerequisites
- Python 3.13 or higher
- Git
- Docker (optional, but recommended)

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/stockbook.git
cd stockbook

# Build and run with Docker Compose
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### Option 2: Local Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/stockbook.git
cd stockbook

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install pre-commit hooks (required for development)
pre-commit install
```

## Development

### Quick Start

```bash
# Run all tests
make test

# Run quality checks (same as pre-commit hook)
make quality

# Format code
make format

# See all available commands
make help
```

### Development Workflow

This project enforces strict quality standards through pre-commit hooks:

1. **Test-Driven Development (TDD)** is mandatory
   - Write tests first
   - Implement code to make tests pass
   - Refactor while keeping tests green

2. **Type Safety** is enforced
   - All code must pass `pyright --strict`
   - Explicit type annotations required

3. **Quality Checks** run automatically
   - Format: `black` and `isort`
   - Lint: `pylint` with strict unified standards
   - Type check: `pyright` and `mypy`
   - Test: `pytest` with coverage requirements
   - Security: `bandit` and `pip-audit`

### Code Quality Standards

All code follows the **same strict quality standards** with minor allowances for legitimate test patterns:

- **Core/Production Code**: Strictest complexity and quality metrics
- **Test Code**: Same strict standards with allowances for:
  - Protected member access (testing internal state)
  - Redefined names (pytest fixtures)
  - Unused arguments (fixture side effects)
  - Attributes in setup methods

### Project Structure

```
stockbook/
├── src/                      # Source code
│   ├── domain/              # Domain layer (entities, value objects, services)
│   │   ├── entities/        # Stock, Portfolio, Transaction, etc.
│   │   ├── value_objects/   # Money, Quantity, StockSymbol, etc.
│   │   ├── services/        # Business logic services
│   │   ├── repositories/    # Repository interfaces
│   │   └── events/          # Domain events
│   └── application/         # Application layer (use cases)
│       ├── commands/        # Command objects
│       ├── dto/            # Data transfer objects
│       └── services/        # Application services
├── dependency_injection/     # IoC container and composition root
├── tests/                   # Comprehensive test suite
│   ├── domain/             # Domain layer tests (100% coverage)
│   ├── application/        # Application layer tests (100% coverage)
│   └── dependency_injection/ # DI framework tests
├── docs/                    # Documentation
│   ├── ARCHITECTURE.md     # System design and architecture
│   ├── RUFF_MIGRATION_GUIDE.md # Linting tool migration guide
│   ├── ONBOARDING.md       # New developer guide
│   └── API_DESIGN.md       # Planned API structure
├── hooks/                   # Git hooks and quality scripts
├── database/                # Database schema (SQLite)
├── docker-compose.yml       # Docker configuration
├── Makefile                # Development commands
└── requirements.txt        # Python dependencies
```

### Layer-Specific Testing

The project enforces different coverage thresholds per architectural layer:

| Layer | Required Coverage | Rationale |
|-------|-------------------|-----------|
| Domain | 100% | Core business logic must be fully tested |
| Application | 90% | Use cases need comprehensive coverage |
| Infrastructure | 100% | Data persistence is critical |
| Presentation | 100% | API contracts must be reliable |

Run layer coverage analysis:
```bash
python hooks/check-layer-coverage.py
```

## Architecture

StockBook follows Clean Architecture principles with clear separation of concerns:

```
┌─────────────────────────────────────────────────┐
│                 Presentation                    │ (Planned)
│          (FastAPI, REST API, Web UI)           │
├─────────────────────────────────────────────────┤
│                 Application                     │ ✅ Implemented
│        (Use Cases, Commands, DTOs)             │
├─────────────────────────────────────────────────┤
│                   Domain                        │ ✅ Implemented  
│    (Entities, Value Objects, Services)         │
├─────────────────────────────────────────────────┤
│               Infrastructure                    │ (Planned)
│      (Database, External Services)             │
└─────────────────────────────────────────────────┘

→ Dependencies flow inward (Dependency Inversion Principle)
```

For detailed architecture documentation, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Contributing

This is a personal project, but suggestions and feedback are welcome through issues. Please ensure:

1. All tests pass (`make test`)
2. Code passes quality checks (`make quality`)
3. Changes follow TDD approach
4. Type safety is maintained

## License

MIT License - see LICENSE file for details.

## Disclaimer

This software is for personal use only and should not be considered financial advice. Always consult with qualified financial professionals for investment decisions.