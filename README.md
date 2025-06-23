# StockBook

Personal stock trading tracker for managing family investments with portfolio analytics and performance monitoring.

## Overview

StockBook is a lightweight web application built with Python and Streamlit to help track personal and family stock investments. It provides a simple interface for recording trades, monitoring portfolio performance, and analyzing investment history.

## Features (Planned)

- 📊 Portfolio overview dashboard
- 📝 Trade entry and management
- 📈 Performance tracking
- 💰 Profit/loss calculations
- 📅 Historical data analysis
- 👨‍👩‍👧‍👦 Multi-account support for family members

## Tech Stack

- **Python** - Core programming language with type safety
- **Streamlit** - Web application framework
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
# Run the application
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

## Project Structure

```
stockbook/
├── app.py                    # Main Streamlit application (legacy)
├── domain/                   # Domain layer (entities, services, repositories)
│   ├── entities/            # Rich domain entities with business logic
│   ├── value_objects/       # Immutable value types (Money, Quantity, etc.)
│   ├── services/            # Domain services for complex business logic
│   └── repositories/        # Repository interfaces
├── application/              # Application layer (use cases, commands)
│   ├── services/            # Application services
│   └── commands/            # Command objects for operations
├── infrastructure/           # Infrastructure layer (data access, external services)
│   ├── persistence/         # Database connections and unit of work
│   └── repositories/        # Repository implementations
├── presentation/             # Presentation layer (UI, controllers, view models)
│   ├── controllers/         # Business logic controllers
│   ├── view_models/         # Data transfer objects for UI
│   ├── adapters/            # Framework adapters
│   └── coordinators/        # UI workflow coordination
├── dependency_injection/     # IoC container and composition root

├── tests/                   # Comprehensive test suite
├── config.py                # Centralized configuration management
├── requirements.txt         # Python dependencies
└── docs/                    # Documentation and roadmap
```

## Development Status

🏗️ **Architecture Complete, Integration Phase** - Clean architecture foundation is complete, now integrating with main application.

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
- Infrastructure Layer: 85% minimum (data persistence)
- Presentation Layer: 75% minimum (UI components)

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
- **Presentation layer (75%)**: UI components and user interactions

Coverage analysis runs automatically during pre-commit hooks and provides detailed reporting on which files in each layer need additional tests.

## Contributing

This is a personal project, but suggestions and feedback are welcome through issues.

## License

MIT License - see LICENSE file for details.

## Disclaimer

This software is for personal use only and should not be considered financial advice. Always consult with qualified financial professionals for investment decisions.
