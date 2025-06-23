# StockBook

Personal stock trading tracker for managing family investments with portfolio analytics and performance monitoring.

## Overview

StockBook is a modern web application built with Python and FastAPI to help track personal and family stock investments. It provides a RESTful API for recording trades, monitoring portfolio performance, and analyzing investment history.

## Features (Planned)

- 📊 Portfolio overview dashboard
- 📝 Trade entry and management
- 📈 Performance tracking
- 💰 Profit/loss calculations
- 📅 Historical data analysis
- 👨‍👩‍👧‍👦 Multi-account support for family members

## Tech Stack

- **Python** - Core programming language with type safety
- **FastAPI** - Modern async web framework with automatic OpenAPI documentation
- **Pydantic** - Data validation and serialization with comprehensive type checking
- **SQLite** - Local database for data persistence
- **Clean Architecture** - Layered architecture with dependency inversion
- **Domain-Driven Design** - Rich domain models and business logic
- **Dependency Injection** - Professional IoC container for testability
- **Test-Driven Development** - Comprehensive test coverage with TDD approach

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/stockbook.git
cd stockbook

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### After cloning the repo:
```bash
pre-commit install
```

## Usage

```bash
# Run the FastAPI application
uvicorn src.infrastructure.web.main:app --reload

# Or run with development settings
python -m uvicorn src.infrastructure.web.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Base URL**: `http://localhost:8000`
- **Interactive API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative API Docs**: `http://localhost:8000/redoc` (ReDoc)

### Available Endpoints

- `GET /health` - Health check endpoint
- `GET /stocks` - List all stocks
- `POST /stocks` - Create a new stock
- `GET /stocks/{stock_id}` - Get stock by ID
- `PUT /stocks/{stock_id}` - Update stock by ID
- `DELETE /stocks/{stock_id}` - Delete stock by ID

## Project Structure

```
stockbook/
├── src/                      # Source code following clean architecture
│   ├── domain/              # Domain layer (entities, services, repositories)
│   │   ├── entities/        # Rich domain entities with business logic
│   │   ├── value_objects/   # Immutable value types (Money, Quantity, etc.)
│   │   ├── services/        # Domain services for complex business logic
│   │   └── repositories/    # Repository interfaces
│   ├── application/         # Application layer (use cases, commands)
│   │   ├── services/        # Application services
│   │   ├── commands/        # Command objects for operations
│   │   └── dto/            # Data transfer objects
│   ├── infrastructure/      # Infrastructure layer (data access, external services)
│   │   ├── persistence/     # Database connections and unit of work
│   │   ├── repositories/    # Repository implementations
│   │   └── web/            # FastAPI application and API routes
│   │       ├── main.py     # FastAPI application entry point
│   │       ├── models/     # Pydantic models for API
│   │       ├── routers/    # API route handlers
│   │       └── mappers/    # Data mapping between layers
│   └── presentation/        # Presentation layer (API controllers, view models)
│       ├── controllers/     # Business logic controllers
│       ├── view_models/     # Data transfer objects for API
│       ├── adapters/        # Framework adapters
│       └── coordinators/    # API workflow coordination
├── dependency_injection/     # IoC container and composition root
├── tests/                   # Comprehensive test suite
│   ├── integration/         # Full-stack integration tests
│   ├── domain/             # Domain layer tests
│   ├── application/        # Application layer tests
│   ├── infrastructure/     # Infrastructure layer tests
│   └── presentation/       # Presentation layer tests
├── config.py                # Centralized configuration management
├── requirements.txt         # Python dependencies
└── docs/                    # Documentation and roadmap
```

## Development Status

🚀 **FastAPI Migration Complete** - Modern REST API with comprehensive test coverage and clean architecture.

### Completed Architecture (Phase 0) ✅

**Clean Architecture Implementation**
- Complete 4-layer architecture (Domain, Application, Infrastructure, Presentation)
- Professional dependency injection with IoC container and composition root
- Rich domain models with business logic and invariants
- Repository pattern with clean separation of concerns
- Comprehensive error handling and validation

**Domain-Driven Design**
- Rich domain layer with value objects (Money, Quantity) and business rules
- Domain events infrastructure for event-driven architecture
- Domain services for portfolio calculation, stock validation, and risk assessment
- Clean single-context approach with consolidated domain components

**Legacy Foundation (Phase 1)**
- Database schema with 6 tables and relationships  
- Pydantic models with comprehensive validation
- Database operations with full CRUD functionality
- Centralized configuration management
- UI component library and navigation framework

### Current Phase: Integration & Feature Development

**Test Coverage**: Comprehensive test suite with layer-specific coverage enforcement:
- Domain Layer: 100% minimum (business logic) - **ACHIEVED**
- Application Layer: 90% minimum (use cases) - **ACHIEVED (100%)**
- Infrastructure Layer: 100% minimum (data persistence) - **ACHIEVED**
- Presentation Layer: 100% minimum (API components) - **ACHIEVED**

**Architecture Compliance**: 100% clean architecture principles
**Code Quality**: Strict linting (pylint 10/10), type-safe (pyright standard mode), comprehensive error handling

## Development

### Layer-Specific Test Coverage

This project enforces different test coverage thresholds for each architectural layer:

```bash
# Run layer coverage analysis
python hooks/check-layer-coverage.py

# View layer coverage configuration
cat hooks/layer-coverage.yaml
```

The coverage thresholds reflect the criticality of each layer:
- **Domain layer (100%)**: Contains core business logic and rules
- **Application layer (90%)**: Orchestrates use cases and workflows  
- **Infrastructure layer (100%)**: Handles data persistence and external services
- **Presentation layer (100%)**: API components and request/response handling

Coverage analysis runs automatically during pre-commit hooks and provides detailed reporting on which files in each layer need additional tests.

## Contributing

This is a personal project, but suggestions and feedback are welcome through issues.

## License

MIT License - see LICENSE file for details.

## Disclaimer

This software is for personal use only and should not be considered financial advice. Always consult with qualified financial professionals for investment decisions.
