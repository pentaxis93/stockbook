#!/usr/bin/env python3
"""C4 Architecture Model Generator for StockBook.

This script generates C4 model diagrams (Context, Container, Component, Code)
for the StockBook architecture using PlantUML.
"""

from __future__ import annotations

from pathlib import Path

# Project root is 3 levels up from this script
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
SRC_ROOT = PROJECT_ROOT / "src"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "architecture" / "diagrams"


def ensure_output_dir() -> None:
    """Ensure the output directory exists."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def analyze_module_structure() -> dict[str, list[str]]:
    """Analyze the src directory structure to understand modules."""
    modules: dict[str, list[str]] = {
        "domain": [],
        "application": [],
        "infrastructure": [],
        "presentation": [],
    }

    for layer in modules:
        layer_path = SRC_ROOT / layer
        if layer_path.exists():
            for item in layer_path.rglob("*.py"):
                if "__pycache__" not in str(item) and item.name != "__init__.py":
                    relative_path = item.relative_to(layer_path)
                    modules[layer].append(str(relative_path))

    return modules


def generate_system_context_diagram() -> str:
    """Generate C4 System Context diagram."""
    return """@startuml 01_c1_system_context
skinparam backgroundColor #FEFEFE

title StockBook - System Context

actor "Family Member" as user
rectangle "StockBook" as stockbook #4A90E2 {
  [Personal stock trading tracker]
}

rectangle "Market Data Provider" as market_data #E6E6E6 {
  [Stock prices & market info]
}

rectangle "Stock Broker" as broker #E6E6E6 {
  [Executes trades]
}

user --> stockbook : Uses (HTTPS)
stockbook --> market_data : Fetches market data (API)
broker --> user : Executes trades

@enduml
"""


def generate_container_diagram() -> str:
    """Generate C4 Container diagram showing the main architectural layers."""
    return """@startuml 02_c2_container
skinparam backgroundColor #FEFEFE

title StockBook - C2 Container Diagram (Clean Architecture Layers)

actor "Family Member" as user

rectangle "StockBook System" {
    component "Web Application (FastAPI)" as web_app #FFFFE6
    component "Application Layer (Python)" as app_layer #E6F3FF
    component "Domain Layer (Python)" as domain_layer #FFE6E6
    component "Infrastructure Layer (SQLAlchemy)" as infra_layer #E6FFE6
    database "Database (SQLite/PostgreSQL)" as db #F0F0F0
}

user --> web_app : Uses (HTTPS)
web_app --> app_layer : Uses
app_layer --> domain_layer : Uses
app_layer --> infra_layer : Uses repository interfaces
infra_layer --> db : Reads/Writes
infra_layer ..> domain_layer : Implements interfaces

@enduml
"""


def generate_component_diagram(_modules: dict[str, list[str]]) -> str:
    """Generate C4 Component diagram for the Application layer."""
    return """@startuml 05_c3_component_application
skinparam backgroundColor #FEFEFE

title StockBook - Application Layer Components

package "Application Layer" #E6F3FF {
    component "Stock Application Service" as stock_service
    component "Commands" as commands
    component "DTOs" as dto
    component "Service Interfaces" as interfaces
}

component "Domain Layer" as domain #FFE6E6
component "Presentation Layer" as presentation #FFFFE6
component "Infrastructure Layer" as infrastructure #E6FFE6

presentation --> stock_service : Uses
stock_service --> commands : Executes
stock_service --> dto : Returns
stock_service --> domain : Uses
stock_service ..> interfaces : Implements
infrastructure ..> interfaces : Implements

@enduml
"""


def generate_clean_architecture_diagram() -> str:
    """Generate Clean Architecture onion diagram."""
    return """@startuml 03_clean_architecture_overview
!define RECTANGLE class

skinparam backgroundColor #FEFEFE
skinparam rectangleBorderColor #000000
skinparam rectangleBackgroundColor #FFFFCC

title StockBook Clean Architecture Overview

package "Domain Layer (Core)" #LightBlue {
    RECTANGLE Entities {
        + Stock
        + Portfolio
        + Transaction
        + Position
    }

    RECTANGLE "Value Objects" {
        + Money
        + StockSymbol
        + Quantity
        + Grade
    }

    RECTANGLE "Domain Services" {
        + PortfolioCalculationService
        + RiskAssessmentService
    }

    RECTANGLE "Repository Interfaces" {
        + IStockRepository
        + IPortfolioRepository
        + ITransactionRepository
    }
}

package "Application Layer" #LightGreen {
    RECTANGLE "Application Services" {
        + StockApplicationService
    }

    RECTANGLE Commands {
        + CreateStockCommand
        + UpdateStockCommand
    }

    RECTANGLE DTOs {
        + StockDto
    }
}

package "Infrastructure Layer" #LightCoral {
    RECTANGLE "Repository Implementations" {
        + SqlAlchemyStockRepository
        + SqlAlchemyPositionRepository
    }

    RECTANGLE Persistence {
        + Database Tables
        + Unit of Work
        + Database Factory
    }
}

package "Presentation Layer" #LightYellow {
    RECTANGLE "Web API" {
        + FastAPI Routers
        + Request/Response Models
        + Exception Handlers
    }
}

note right of "Domain Layer (Core)"
  * No external dependencies
  * Pure business logic
  * Framework agnostic
end note

note left of "Infrastructure Layer"
  * Implements domain interfaces
  * External service integrations
  * Database access
end note

Presentation -[hidden]down-> Application
Application -[hidden]down-> Infrastructure
Infrastructure -[hidden]down-> Domain

@enduml
"""


def generate_code_diagram() -> str:
    """Generate C4 Code-level diagram for a specific aggregate."""
    return """@startuml 11_c4_code_stock_aggregate
skinparam backgroundColor #FEFEFE
skinparam classAttributeIconSize 0

title StockBook - C4 Code Level (Stock Aggregate)

package "Stock Aggregate" {
    class Stock {
        - id: UUID
        - symbol: StockSymbol
        - company_name: CompanyName
        - sector: Sector
        - industry_group: IndustryGroup
        - grade: Grade
        - notes: Notes
        + update_grade(grade: Grade)
        + update_notes(notes: Notes)
    }

    class StockSymbol {
        - value: str
        + validate()
    }

    class CompanyName {
        - value: str
        + validate()
    }

    class Grade {
        - value: str
        + from_string()
        + is_valid()
    }

    class Sector {
        - value: str
        + validate()
    }

    class IndustryGroup {
        - value: str
        + validate_with_sector()
    }
}

Stock --> StockSymbol : has
Stock --> CompanyName : has
Stock --> Grade : has
Stock --> Sector : has
Stock --> IndustryGroup : has

note right of Stock
  Aggregate Root
  - Ensures consistency
  - Business rules
end note

note bottom of StockSymbol
  Value Objects
  - Immutable
  - Self-validating
end note

@enduml
"""


def main() -> None:
    """Generate all C4 architecture diagrams."""
    ensure_output_dir()

    # Analyze module structure
    modules = analyze_module_structure()

    # Generate diagrams
    diagrams = {
        "01_c1_system_context.puml": generate_system_context_diagram(),
        "02_c2_container.puml": generate_container_diagram(),
        "05_c3_component_application.puml": generate_component_diagram(modules),
        "03_clean_architecture_overview.puml": generate_clean_architecture_diagram(),
        "11_c4_code_stock_aggregate.puml": generate_code_diagram(),
    }

    # Write diagram files
    for filename, content in diagrams.items():
        output_path = OUTPUT_DIR / filename
        output_path.write_text(content)

    # Generate PlantUML command file for batch processing
    plantuml_commands = OUTPUT_DIR / "generate_all.sh"
    with plantuml_commands.open("w") as f:
        f.write("#!/bin/bash\n")
        f.write("# Generate all PlantUML diagrams\n\n")
        for filename in diagrams:
            f.write(f"plantuml -tpng {filename}\n")
            f.write(f"plantuml -tsvg {filename}\n")

    plantuml_commands.chmod(0o755)


if __name__ == "__main__":
    main()
