#!/bin/bash
# Generate all PlantUML diagrams

plantuml -tpng 01_c1_system_context.puml
plantuml -tsvg 01_c1_system_context.puml
plantuml -tpng 02_c2_container.puml
plantuml -tsvg 02_c2_container.puml
plantuml -tpng 05_c3_component_application.puml
plantuml -tsvg 05_c3_component_application.puml
plantuml -tpng 03_clean_architecture_overview.puml
plantuml -tsvg 03_clean_architecture_overview.puml
plantuml -tpng 11_c4_code_stock_aggregate.puml
plantuml -tsvg 11_c4_code_stock_aggregate.puml
