# StockBook Architecture Documentation

This directory contains auto-generated architecture diagrams and documentation for the StockBook project.

## Overview

StockBook follows Clean Architecture principles with Domain-Driven Design (DDD). The architecture documentation is automatically generated from the codebase to ensure it stays synchronized with the actual implementation.

## Directory Structure

```
docs/architecture/
├── diagrams/          # Generated diagram files (*.puml, *.png, *.svg)
├── models/            # Python scripts that analyze code and generate diagrams
│   ├── c4_model.py    # C4 architecture model generator
│   ├── domain_model.py # Domain entity relationship generator
│   └── layers_model.py # Clean architecture layers visualizer
├── templates/         # PlantUML style templates
│   └── stockbook_style.puml # Common styling for diagrams
└── README.md          # This file
```

## Generated Diagrams

The diagrams are numbered and organized in a logical sequence that tells the complete architectural story from top to bottom:

### Overview - Big Picture (01-04)
1. **C1 System Context** (`01_c1_system_context`): Shows StockBook in its environment with external systems
2. **C2 Container** (`02_c2_container`): Displays the main technical building blocks and architectural layers
3. **Clean Architecture Overview** (`03_clean_architecture_overview`): Shows all layers and their key components
4. **Clean Architecture Onion** (`04_clean_architecture_onion`): Concentric view showing dependency rule

### Component Level - Zooming In (05-07)
5. **C3 Component Application** (`05_c3_component_application`): Details the Application layer components
6. **Clean Architecture Layers** (`06_clean_architecture_layers`): Shows allowed and forbidden dependencies
7. **Module Dependencies** (`07_module_dependencies`): Detailed module-level relationships

### Domain Model - Core Business (08-10)
8. **Domain Entity Relationships** (`08_domain_entity_relationships`): Core domain relationships
9. **Domain Aggregate Boundaries** (`09_domain_aggregate_boundaries`): DDD aggregate consistency boundaries
10. **Domain Value Objects** (`10_domain_value_objects`): Value object hierarchy

### Implementation Details (11-12)
11. **C4 Code Level** (`11_c4_code_stock_aggregate`): Code-level view of Stock aggregate
12. **Dependency Injection** (`12_dependency_injection`): How DI wires everything together

## Usage

### Generate Diagrams

To generate all architecture diagrams:

```bash
make docs-arch
```

This will:
1. Run all Python model generators
2. Create PlantUML diagram files (*.puml) in `diagrams/`
3. Generate a shell script to render PNG/SVG files

### Render Images

To render the PlantUML files to PNG/SVG:

1. Install PlantUML (requires Java):
   ```bash
   # Ubuntu/Debian
   sudo apt-get install plantuml
   
   # macOS
   brew install plantuml
   ```

2. Run the generated script:
   ```bash
   cd docs/architecture/diagrams
   ./generate_all.sh
   ```

### View Documentation

To serve the documentation locally:

```bash
make docs-serve
```

This starts a local HTTP server at http://localhost:8080

## Architecture Principles

### Clean Architecture Layers

1. **Domain Layer** (Core)
   - Entities, Value Objects, Domain Services
   - Repository Interfaces, Domain Events
   - No external dependencies

2. **Application Layer**
   - Use Cases, Commands, Application Services
   - DTOs for data transfer
   - Depends only on Domain

3. **Infrastructure Layer**
   - Repository Implementations
   - Database Persistence (SQLAlchemy)
   - External Service Integrations
   - Implements Domain interfaces

4. **Presentation Layer**
   - REST API (FastAPI)
   - Request/Response Models
   - Exception Handlers, Middleware
   - Depends on Application and Infrastructure (via DI)

### Key Design Patterns

- **Repository Pattern**: Abstract data access behind interfaces
- **Unit of Work**: Manage database transactions
- **Command Pattern**: Encapsulate operations as commands
- **Value Objects**: Immutable domain concepts
- **Aggregate Pattern**: Consistency boundaries in domain
- **Dependency Injection**: Inversion of control for flexibility

## Extending the Documentation

### Adding New Diagram Types

1. Create a new generator script in `models/`:
   ```python
   # models/new_diagram.py
   def generate_new_diagram() -> str:
       return """@startuml
       ' Your PlantUML code here
       @enduml"""
   ```

2. Update the Makefile to include your generator:
   ```makefile
   docs-arch:
       @$(PYTHON) docs/architecture/models/new_diagram.py
   ```

### Customizing Styles

Edit `templates/stockbook_style.puml` to modify colors, fonts, and styling across all diagrams.

## Dependencies

- Python 3.11+
- PlantUML (for rendering diagrams)
- Java (required by PlantUML)
- graphviz (optional, for additional diagram types)

## CI/CD Integration

The architecture documentation can be integrated into CI/CD:

1. Generate diagrams on each merge to main
2. Publish to GitHub Pages or documentation site
3. Include in code review for architecture changes

## Troubleshooting

### PlantUML Not Found
Install PlantUML and ensure it's in your PATH:
```bash
which plantuml
```

### Java Not Found
PlantUML requires Java. Install OpenJDK:
```bash
sudo apt-get install default-jre  # Ubuntu/Debian
brew install openjdk              # macOS
```

### Permission Denied
Make the generated script executable:
```bash
chmod +x docs/architecture/diagrams/generate_all.sh
```

## References

- [C4 Model](https://c4model.com/)
- [PlantUML](https://plantuml.com/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)