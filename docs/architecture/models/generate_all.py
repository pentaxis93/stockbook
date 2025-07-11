#!/usr/bin/env python3
"""Master script to generate all architecture documentation.

This script orchestrates the generation of all architecture diagrams
and can be integrated into CI/CD pipelines.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# Scripts to run in order
GENERATOR_SCRIPTS = [
    "c4_model.py",
    "domain_model.py",
    "layers_model.py",
]

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
MODELS_DIR = Path(__file__).parent
OUTPUT_DIR = PROJECT_ROOT / "docs" / "architecture" / "diagrams"


def run_generator(script_name: str) -> bool:
    """Run a generator script and return success status."""
    script_path = MODELS_DIR / script_name

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            check=True,
        )
        if result.stderr:
            pass
        return True
    except subprocess.CalledProcessError:
        return False


def check_plantuml() -> bool:
    """Check if PlantUML is available."""
    try:
        result = subprocess.run(
            ["plantuml", "-version"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def render_diagrams() -> bool:
    """Render PlantUML diagrams to PNG and SVG."""
    if not check_plantuml():
        return False

    puml_files = list(OUTPUT_DIR.glob("*.puml"))
    if not puml_files:
        return False

    success = True
    for puml_file in puml_files:
        # Render PNG
        png_result = subprocess.run(
            ["plantuml", "-tpng", str(puml_file)],
            capture_output=True,
            text=True,
            check=False,
        )
        if png_result.returncode != 0:
            success = False
        else:
            pass

        # Render SVG
        svg_result = subprocess.run(
            ["plantuml", "-tsvg", str(puml_file)],
            capture_output=True,
            text=True,
            check=False,
        )
        if svg_result.returncode != 0:
            success = False
        else:
            pass

    return success


def generate_index_html() -> None:
    """Generate an index.html file for easy diagram viewing."""
    index_path = OUTPUT_DIR / "index.html"

    # Find all generated diagrams
    png_files = sorted(OUTPUT_DIR.glob("*.png"))
    sorted(OUTPUT_DIR.glob("*.svg"))

    # If no PNG files exist, copy the viewer.html instead
    if not png_files:
        viewer_path = OUTPUT_DIR / "viewer.html"
        if viewer_path.exists():
            import shutil

            shutil.copy(viewer_path, index_path)
            return

    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StockBook Architecture Diagrams</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1, h2 {
            color: #2c3e50;
        }
        .diagram-section {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .diagram-title {
            font-size: 1.5em;
            margin-bottom: 10px;
            color: #34495e;
        }
        .diagram-container {
            text-align: center;
            margin: 20px 0;
        }
        .diagram-container img {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .format-links {
            margin-top: 10px;
        }
        .format-links a {
            margin: 0 10px;
            color: #3498db;
            text-decoration: none;
        }
        .format-links a:hover {
            text-decoration: underline;
        }
        .toc {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .toc ul {
            list-style-type: none;
            padding-left: 0;
        }
        .toc li {
            margin: 5px 0;
        }
        .toc a {
            color: #3498db;
            text-decoration: none;
        }
        .toc a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>StockBook Architecture Diagrams</h1>

    <div class="toc">
        <h2>Table of Contents</h2>
        <ul>
"""

    # Add TOC entries
    for png_file in png_files:
        diagram_name = png_file.stem.replace("_", " ").title()
        html_content += (
            f'            <li><a href="#{png_file.stem}">{diagram_name}</a></li>\n'
        )

    html_content += """        </ul>
    </div>
"""

    # Add diagram sections
    for png_file in png_files:
        diagram_name = png_file.stem.replace("_", " ").title()
        svg_file = OUTPUT_DIR / f"{png_file.stem}.svg"
        puml_file = OUTPUT_DIR / f"{png_file.stem}.puml"

        html_content += f"""
    <div class="diagram-section" id="{png_file.stem}">
        <h2 class="diagram-title">{diagram_name}</h2>
        <div class="diagram-container">
            <img src="{png_file.name}" alt="{diagram_name}">
        </div>
        <div class="format-links">
            <strong>Download:</strong>
            <a href="{png_file.name}" download>PNG</a>
"""

        if svg_file.exists():
            html_content += f'            <a href="{svg_file.name}" download>SVG</a>\n'

        if puml_file.exists():
            html_content += (
                f'            <a href="{puml_file.name}" download>PlantUML Source</a>\n'
            )

        html_content += """        </div>
    </div>
"""

    html_content += """
    <footer style="text-align: center; margin-top: 50px; color: #7f8c8d;">
        <p>Generated by StockBook Architecture Documentation</p>
    </footer>
</body>
</html>
"""

    index_path.write_text(html_content)


def main() -> int:
    """Main entry point."""
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Run all generators
    all_success = True
    for script in GENERATOR_SCRIPTS:
        if not run_generator(script):
            all_success = False

    if not all_success:
        return 1

    # Try to render diagrams
    render_success = render_diagrams()

    # Generate index.html
    generate_index_html()

    # Summary

    if render_success:
        pass
    else:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
