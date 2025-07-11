#!/usr/bin/env python3
"""Clean Architecture Layers Visualization Generator for StockBook.

This script analyzes the project structure and import-linter contracts
to generate visualizations of the clean architecture layers and their dependencies.
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

# Project root is 3 levels up from this script
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"
SRC_ROOT = PROJECT_ROOT / "src"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "architecture" / "diagrams"


def load_import_linter_contracts() -> list[dict[str, Any]]:
    """Load import-linter contracts from pyproject.toml."""
    with open(PYPROJECT_PATH, "rb") as f:
        config = tomllib.load(f)

    contracts = []
    if (
        "tool" in config
        and "importlinter" in config["tool"]
        and "contracts" in config["tool"]["importlinter"]
    ):
        contracts = config["tool"]["importlinter"]["contracts"]

    return contracts


def analyze_layer_structure() -> dict[str, dict[str, Any]]:
    """Analyze the src directory to understand layer structure."""
    layers = {
        "domain": {
            "modules": [],
            "description": "Core business logic and domain models",
            "color": "#FFE6E6",  # Light red
        },
        "application": {
            "modules": [],
            "description": "Use cases and application services",
            "color": "#E6F3FF",  # Light blue
        },
        "infrastructure": {
            "modules": [],
            "description": "External concerns and implementations",
            "color": "#E6FFE6",  # Light green
        },
        "presentation": {
            "modules": [],
            "description": "User interface and API endpoints",
            "color": "#FFFFE6",  # Light yellow
        },
    }

    for layer_name, layer_info in layers.items():
        layer_path = SRC_ROOT / layer_name
        if layer_path.exists():
            for item in layer_path.iterdir():
                if item.is_dir() and not item.name.startswith("__"):
                    layer_info["modules"].append(item.name)

    return layers


def generate_onion_architecture_diagram(layers: dict[str, dict[str, Any]]) -> str:
    """Generate the onion architecture diagram."""
    return """@startuml 04_clean_architecture_onion

!define DOMAIN_COLOR #FFE6E6
!define APPLICATION_COLOR #E6F3FF
!define INFRASTRUCTURE_COLOR #E6FFE6
!define PRESENTATION_COLOR #FFFFE6

skinparam backgroundColor #FEFEFE
skinparam shadowing false

title StockBook - Clean Architecture (Onion View)

' Center: Domain Layer (innermost)
storage "Domain Layer" as domain <<Layer>> DOMAIN_COLOR {
  rectangle "Entities" as entities
  rectangle "Value Objects" as values
  rectangle "Domain Services" as dservices
  rectangle "Repository\\nInterfaces" as repos
  rectangle "Domain Events" as events
}

' Application Layer (surrounding domain)
cloud "Application Layer" as application <<Layer>> APPLICATION_COLOR {
  rectangle "Use Cases" as usecases
  rectangle "Commands" as commands
  rectangle "Application\\nServices" as aservices
  rectangle "DTOs" as dtos
}

' Infrastructure Layer
database "Infrastructure Layer" as infrastructure <<Layer>> INFRASTRUCTURE_COLOR {
  rectangle "Repository\\nImplementations" as repoimpl
  rectangle "Database\\nPersistence" as db
  rectangle "External\\nServices" as external
  rectangle "Unit of Work" as uow
}

' Presentation Layer (outermost)
package "Presentation Layer" as presentation <<Layer>> PRESENTATION_COLOR {
  rectangle "REST API\\n(FastAPI)" as api
  rectangle "Request/Response\\nModels" as models
  rectangle "Exception\\nHandlers" as handlers
  rectangle "Middleware" as middleware
}

' Layout hints for concentric arrangement
domain -[hidden]- application
application -[hidden]- infrastructure
infrastructure -[hidden]- presentation

' Dependency arrows (pointing inward)
presentation ..> infrastructure : depends on
infrastructure ..> application : depends on
application ..> domain : depends on

note bottom
  **Onion Architecture Principles:**
  • Dependencies point inward only
  • Inner layers are independent
  • Domain is the core (no dependencies)
  • Outer layers depend on inner layers
end note

@enduml
"""


def generate_layered_architecture_diagram(contracts: list[dict[str, Any]]) -> str:
    """Generate layered architecture diagram with forbidden dependencies."""
    # Find the layered architecture contract
    for contract in contracts:
        if contract.get("name") == "Layered architecture":
            break

    # Extract forbidden dependencies from contracts
    forbidden_deps = []
    for contract in contracts:
        if contract.get("type") == "forbidden":
            source = contract.get("source_modules", [])
            forbidden = contract.get("forbidden_modules", [])
            if source and forbidden:
                forbidden_deps.append((source[0], forbidden[0]))

    return """@startuml 06_clean_architecture_layers

skinparam packageBorderColor #333333
skinparam packageBorderThickness 2

title StockBook - Layered Architecture with Dependencies

package "Presentation Layer" <<Layer>> #FFFFE6 {
}
note right of "Presentation Layer" : FastAPI routers, models, middleware

package "Infrastructure Layer" <<Layer>> #E6FFE6 {
}
note right of "Infrastructure Layer" : SQLAlchemy repos, persistence, external services

package "Application Layer" <<Layer>> #E6F3FF {
}
note right of "Application Layer" : Use cases, commands, app services, DTOs

package "Domain Layer" <<Layer>> #FFE6E6 {
}
note right of "Domain Layer" : Entities, value objects, domain services, interfaces

' Allowed dependencies (solid arrows)
"Presentation Layer" -[#00AA00,thickness=2]-> "Application Layer" : uses
"Presentation Layer" -[#00AA00,thickness=2]-> "Infrastructure Layer" : uses (DI)
"Infrastructure Layer" -[#00AA00,thickness=2]-> "Application Layer" : implements interfaces
"Infrastructure Layer" -[#00AA00,thickness=2]-> "Domain Layer" : implements interfaces
"Application Layer" -[#00AA00,thickness=2]-> "Domain Layer" : uses

' Forbidden dependencies (dashed red arrows with X)
"Application Layer" -[#FF0000,dashed,thickness=2]-> "Infrastructure Layer" : <color:red>✗</color>
"Application Layer" -[#FF0000,dashed,thickness=2]-> "Presentation Layer" : <color:red>✗</color>
"Domain Layer" -[#FF0000,dashed,thickness=2]-> "Application Layer" : <color:red>✗</color>
"Domain Layer" -[#FF0000,dashed,thickness=2]-> "Infrastructure Layer" : <color:red>✗</color>
"Domain Layer" -[#FF0000,dashed,thickness=2]-> "Presentation Layer" : <color:red>✗</color>

legend right
  **Legend:**
  <color:green>→ Allowed dependency</color>
  <color:red>⇢ Forbidden dependency</color>

  **Dependency Injection:**
  Infrastructure implements
  domain interfaces
endlegend

@enduml
"""


def generate_module_dependencies_diagram(layers: dict[str, dict[str, Any]]) -> str:
    """Generate detailed module dependencies diagram."""
    lines = ["@startuml 07_module_dependencies"]
    lines.append("!define MODULE(name,layer,color) rectangle name <<layer>> #color")
    lines.append("")
    lines.append("title StockBook - Module Dependencies")
    lines.append("")

    # Add modules for each layer
    for layer_name, layer_info in layers.items():
        lines.append(
            f"package \"{layer_name.capitalize()} Layer\" {layer_info['color']} {{",
        )
        for module in layer_info["modules"]:
            lines.append(f"  MODULE({layer_name}.{module}, {layer_name}, white)")
        lines.append("}")
        lines.append("")

    # Add key dependencies
    lines.append("' Key Dependencies")
    lines.append("presentation.web -[thickness=2]-> application.services : uses")
    lines.append("presentation.web -[thickness=2]-> application.dto : uses")
    lines.append("application.services -[thickness=2]-> domain.entities : uses")
    lines.append(
        "application.services -[thickness=2]-> domain.repositories : uses interfaces",
    )
    lines.append(
        "infrastructure.repositories -[thickness=2]..> domain.repositories : implements",
    )
    lines.append(
        "infrastructure.persistence -[thickness=2]-> domain.entities : persists",
    )
    lines.append("")

    # Add notes
    lines.append(
        'note top of "Domain Layer" : Core business logic - no external dependencies',
    )
    lines.append('note bottom of "Infrastructure Layer" : Implements domain interfaces')
    lines.append("")
    lines.append("@enduml")

    return "\n".join(lines)


def generate_dependency_injection_diagram() -> str:
    """Generate dependency injection and composition root diagram."""
    return """@startuml 12_dependency_injection
!define COMPONENT(name,type,color) class name <<type>> #color

title StockBook - Dependency Injection Flow

package "Presentation Layer" #FFFFE6 {
  COMPONENT(FastAPIApp, "Entry Point", white) {
    + lifespan()
    + setup_routes()
  }

  COMPONENT(StockRouter, "Router", white) {
    + get_stocks()
    + create_stock()
  }
}

package "Dependency Injection" #F0F0F0 {
  COMPONENT(CompositionRoot, "DI Container", white) {
    + setup()
    + get_stock_service()
    + get_unit_of_work()
  }

  COMPONENT(ServiceProvider, "Provider", white) {
    + provide_singleton()
    + provide_scoped()
  }
}

package "Application Layer" #E6F3FF {
  COMPONENT(IStockApplicationService, "Interface", white)
  COMPONENT(StockApplicationService, "Implementation", white) {
    - unit_of_work: IUnitOfWork
    + create_stock()
    + get_all_stocks()
  }
}

package "Domain Layer" #FFE6E6 {
  COMPONENT(IStockRepository, "Interface", white)
  COMPONENT(IUnitOfWork, "Interface", white)
}

package "Infrastructure Layer" #E6FFE6 {
  COMPONENT(SqlAlchemyStockRepository, "Implementation", white)
  COMPONENT(SqlAlchemyUnitOfWork, "Implementation", white)
}

' Dependency flow
FastAPIApp --> CompositionRoot : initializes
StockRouter --> CompositionRoot : requests dependencies
CompositionRoot --> ServiceProvider : uses

ServiceProvider ..> StockApplicationService : creates
ServiceProvider ..> SqlAlchemyUnitOfWork : creates
ServiceProvider ..> SqlAlchemyStockRepository : creates

StockApplicationService ..|> IStockApplicationService : implements
SqlAlchemyStockRepository ..|> IStockRepository : implements
SqlAlchemyUnitOfWork ..|> IUnitOfWork : implements

StockRouter --> IStockApplicationService : depends on
StockApplicationService --> IUnitOfWork : depends on
SqlAlchemyUnitOfWork --> IStockRepository : provides

note right of CompositionRoot
  Composition Root Pattern:
  - Central configuration
  - Wire dependencies
  - Manage lifetimes
end note

@enduml
"""


def main() -> None:
    """Generate all clean architecture layer diagrams."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load configuration and analyze structure
    contracts = load_import_linter_contracts()
    layers = analyze_layer_structure()

    # Generate diagrams
    diagrams = {
        "04_clean_architecture_onion.puml": generate_onion_architecture_diagram(layers),
        "06_clean_architecture_layers.puml": generate_layered_architecture_diagram(
            contracts,
        ),
        "07_module_dependencies.puml": generate_module_dependencies_diagram(layers),
        "12_dependency_injection.puml": generate_dependency_injection_diagram(),
    }

    # Write diagram files
    for filename, content in diagrams.items():
        output_path = OUTPUT_DIR / filename
        output_path.write_text(content)

    for _layer_name, _layer_info in layers.items():
        pass


if __name__ == "__main__":
    main()
