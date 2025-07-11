#!/usr/bin/env python3
"""Domain Model Diagram Generator for StockBook.

This script analyzes the domain layer to generate entity relationship diagrams
and aggregate boundary visualizations.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

# Project root is 3 levels up from this script
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DOMAIN_ROOT = PROJECT_ROOT / "src" / "domain"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "architecture" / "diagrams"


class DomainAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze domain classes and their relationships."""

    def __init__(self) -> None:
        """Initialize the analyzer."""
        self.entities: dict[str, dict[str, Any]] = {}
        self.value_objects: dict[str, dict[str, Any]] = {}
        self.current_class: str | None = None
        self.current_type: str | None = None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions to extract entities and value objects."""
        self.current_class = node.name

        # Determine if it's an entity or value object based on inheritance or location
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "Entity":
                self.current_type = "entity"
                self.entities[node.name] = {
                    "attributes": [],
                    "methods": [],
                    "relationships": [],
                }
                break

        # If not determined by inheritance, check by naming convention
        if self.current_type is None:
            if "Entity" in node.name or node.name in [
                "Stock",
                "Portfolio",
                "Transaction",
                "Position",
                "Target",
                "JournalEntry",
            ]:
                self.current_type = "entity"
                self.entities[node.name] = {
                    "attributes": [],
                    "methods": [],
                    "relationships": [],
                }
            else:
                self.current_type = "value_object"
                self.value_objects[node.name] = {
                    "attributes": [],
                    "methods": [],
                }

        self.generic_visit(node)
        self.current_class = None
        self.current_type = None

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Visit annotated assignments to extract attributes."""
        if self.current_class and isinstance(node.target, ast.Name):
            attr_name = node.target.id
            attr_type = ast.unparse(node.annotation) if node.annotation else "Any"

            if self.current_type == "entity" and self.current_class in self.entities:
                self.entities[self.current_class]["attributes"].append(
                    {
                        "name": attr_name,
                        "type": attr_type,
                    },
                )

                # Check for relationships
                if attr_type in self.entities or "list[" in attr_type.lower():
                    self.entities[self.current_class]["relationships"].append(
                        {
                            "target": attr_type.replace("list[", "").replace("]", ""),
                            "type": "has_many"
                            if "list[" in attr_type.lower()
                            else "has_one",
                        },
                    )
            elif (
                self.current_type == "value_object"
                and self.current_class in self.value_objects
            ):
                self.value_objects[self.current_class]["attributes"].append(
                    {
                        "name": attr_name,
                        "type": attr_type,
                    },
                )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions to extract methods."""
        if self.current_class and not node.name.startswith("_"):
            method_info = {
                "name": node.name,
                "params": [arg.arg for arg in node.args.args if arg.arg != "self"],
            }

            if self.current_type == "entity" and self.current_class in self.entities:
                self.entities[self.current_class]["methods"].append(method_info)
            elif (
                self.current_type == "value_object"
                and self.current_class in self.value_objects
            ):
                self.value_objects[self.current_class]["methods"].append(method_info)


def analyze_domain_models() -> tuple[dict[str, Any], dict[str, Any]]:
    """Analyze all domain models in the domain layer."""
    analyzer = DomainAnalyzer()

    # Analyze entities
    entities_path = DOMAIN_ROOT / "entities"
    if entities_path.exists():
        for py_file in entities_path.glob("*.py"):
            if py_file.name != "__init__.py":
                content = py_file.read_text()
                tree = ast.parse(content)
                analyzer.visit(tree)

    # Analyze value objects
    vo_path = DOMAIN_ROOT / "value_objects"
    if vo_path.exists():
        for py_file in vo_path.glob("*.py"):
            if py_file.name != "__init__.py":
                content = py_file.read_text()
                tree = ast.parse(content)
                analyzer.visit(tree)

    return analyzer.entities, analyzer.value_objects


def generate_entity_relationship_diagram(
    entities: dict[str, Any],
    value_objects: dict[str, Any],
) -> str:
    """Generate entity relationship diagram."""
    lines = ["@startuml 08_domain_entity_relationships"]
    lines.append("!define ENTITY(name,desc) class name <<Entity>> #LightBlue")
    lines.append(
        "!define VALUE_OBJECT(name,desc) class name <<Value Object>> #LightGreen",
    )
    lines.append(
        "!define AGGREGATE_ROOT(name,desc) class name <<Aggregate Root>> #LightCoral",
    )
    lines.append("")
    lines.append("title StockBook Domain Model - Entity Relationships")
    lines.append("")

    # Define aggregate roots
    aggregate_roots = [
        "Stock",
        "Portfolio",
        "Transaction",
        "Position",
        "Target",
        "JournalEntry",
    ]

    # Add entities
    for entity_name, entity_data in entities.items():
        if entity_name in aggregate_roots:
            lines.append(f'AGGREGATE_ROOT({entity_name}, "Aggregate Root") {{')
        else:
            lines.append(f'ENTITY({entity_name}, "Entity") {{')

        # Add attributes
        for attr in entity_data["attributes"][:5]:  # Limit to first 5 attributes
            lines.append(f"  - {attr['name']}: {attr['type']}")

        if len(entity_data["attributes"]) > 5:
            lines.append(f"  ... +{len(entity_data['attributes']) - 5} more attributes")

        # Add key methods
        lines.append("  --")
        for method in entity_data["methods"][:3]:  # Limit to first 3 methods
            params = ", ".join(method["params"])
            lines.append(f"  + {method['name']}({params})")

        if len(entity_data["methods"]) > 3:
            lines.append(f"  ... +{len(entity_data['methods']) - 3} more methods")

        lines.append("}")
        lines.append("")

    # Add key value objects
    key_value_objects = [
        "Money",
        "StockSymbol",
        "Quantity",
        "Grade",
        "Notes",
        "PortfolioName",
    ]
    for vo_name, vo_data in value_objects.items():
        if vo_name in key_value_objects:
            lines.append(f'VALUE_OBJECT({vo_name}, "Value Object") {{')
            for attr in vo_data["attributes"][:3]:
                lines.append(f"  - {attr['name']}: {attr['type']}")
            lines.append("}")
            lines.append("")

    # Add relationships
    lines.append("' Relationships")
    lines.append("Stock --> StockSymbol : has")
    lines.append("Stock --> Grade : has")
    lines.append("Portfolio --> PortfolioName : has")
    lines.append("Portfolio --> Position : contains *")
    lines.append("Position --> Stock : references")
    lines.append("Position --> Quantity : has")
    lines.append("Transaction --> Money : has")
    lines.append("Transaction --> Quantity : has")
    lines.append("Transaction --> Portfolio : belongs to")
    lines.append("Target --> Stock : for")
    lines.append("JournalEntry --> Portfolio : for")
    lines.append("")
    lines.append("@enduml")

    return "\n".join(lines)


def generate_aggregate_boundaries_diagram() -> str:
    """Generate aggregate boundaries diagram."""
    return """@startuml 09_domain_aggregate_boundaries

title StockBook Domain Model - Aggregate Boundaries

package "Stock Aggregate" <<Aggregate>> #DDDDDD {
    class Stock <<Aggregate Root>> #LightCoral {
        - id: UUID
        - symbol: StockSymbol
        - company_name: CompanyName
        - grade: Grade
    }

    class StockSymbol <<Value Object>> #LightGreen {
        - value: str
    }

    class Grade <<Value Object>> #LightGreen {
        - value: str
    }
}

package "Portfolio Aggregate" <<Aggregate>> #DDDDDD {
    class Portfolio <<Aggregate Root>> #LightCoral {
        - id: UUID
        - name: PortfolioName
        - owner: str
        - is_active: bool
    }

    class Position <<Entity>> #LightBlue {
        - id: UUID
        - stock_id: UUID
        - quantity: Quantity
        - average_price: Money
    }

    class PortfolioBalance <<Entity>> #LightBlue {
        - portfolio_id: UUID
        - balance: Money
        - as_of_date: datetime
    }
}

package "Transaction Aggregate" <<Aggregate>> #DDDDDD {
    class Transaction <<Aggregate Root>> #LightCoral {
        - id: UUID
        - portfolio_id: UUID
        - stock_id: UUID
        - type: TransactionType
        - quantity: Quantity
        - price: Money
    }
}

package "Target Aggregate" <<Aggregate>> #DDDDDD {
    class Target <<Aggregate Root>> #LightCoral {
        - id: UUID
        - stock_id: UUID
        - price: Money
        - status: TargetStatus
    }
}

package "Journal Aggregate" <<Aggregate>> #DDDDDD {
    class JournalEntry <<Aggregate Root>> #LightCoral {
        - id: UUID
        - portfolio_id: UUID
        - content: JournalContent
        - entry_date: datetime
    }
}

note top : Each aggregate maintains its own consistency boundary

note right of "Stock Aggregate" : Stock information is referenced by ID from other aggregates

note left of "Portfolio Aggregate" : Portfolio is the main aggregate for tracking investments

@enduml
"""


def generate_value_objects_diagram(value_objects: dict[str, Any]) -> str:
    """Generate value objects hierarchy diagram."""
    lines = ["@startuml 10_domain_value_objects"]
    lines.append("!define VALUE_OBJECT(name) class name <<Value Object>> #LightGreen")
    lines.append("")
    lines.append("title StockBook Domain Model - Value Objects")
    lines.append("")

    # Base value object classes
    lines.append("abstract class BaseValueObject {")
    lines.append("  {abstract} + validate()")
    lines.append("  + __eq__()")
    lines.append("  + __hash__()")
    lines.append("}")
    lines.append("")

    lines.append("abstract class BaseNumericValueObject {")
    lines.append("  - value: Decimal")
    lines.append("  + validate()")
    lines.append("}")
    lines.append("")

    lines.append("abstract class BaseTextValueObject {")
    lines.append("  - value: str")
    lines.append("  + validate()")
    lines.append("}")
    lines.append("")

    # Concrete value objects
    numeric_vos = ["Money", "Quantity"]
    text_vos = [
        "StockSymbol",
        "CompanyName",
        "Notes",
        "PortfolioName",
        "JournalContent",
    ]
    enum_vos = ["Grade", "TransactionType", "Sector", "IndustryGroup", "TargetStatus"]

    for vo in numeric_vos:
        lines.append(f"VALUE_OBJECT({vo}) {{")
        lines.append("  - value: Decimal")
        lines.append("  + validate()")
        lines.append("}")
        lines.append("")

    for vo in text_vos:
        lines.append(f"VALUE_OBJECT({vo}) {{")
        lines.append("  - value: str")
        lines.append("  + validate()")
        lines.append("}")
        lines.append("")

    for vo in enum_vos:
        lines.append(f"VALUE_OBJECT({vo}) {{")
        lines.append("  - value: str")
        lines.append("  + from_string()")
        lines.append("  + is_valid()")
        lines.append("}")
        lines.append("")

    # Inheritance relationships
    lines.append("BaseValueObject <|-- BaseNumericValueObject")
    lines.append("BaseValueObject <|-- BaseTextValueObject")
    lines.append("")

    for vo in numeric_vos:
        lines.append(f"BaseNumericValueObject <|-- {vo}")

    for vo in text_vos:
        lines.append(f"BaseTextValueObject <|-- {vo}")

    for vo in enum_vos:
        lines.append(f"BaseValueObject <|-- {vo}")

    lines.append("")
    lines.append("@enduml")

    return "\n".join(lines)


def main() -> None:
    """Generate all domain model diagrams."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Analyze domain models
    entities, value_objects = analyze_domain_models()

    # Generate diagrams
    diagrams = {
        "08_domain_entity_relationships.puml": generate_entity_relationship_diagram(
            entities,
            value_objects,
        ),
        "09_domain_aggregate_boundaries.puml": generate_aggregate_boundaries_diagram(),
        "10_domain_value_objects.puml": generate_value_objects_diagram(value_objects),
    }

    # Write diagram files
    for filename, content in diagrams.items():
        output_path = OUTPUT_DIR / filename
        output_path.write_text(content)


if __name__ == "__main__":
    main()
