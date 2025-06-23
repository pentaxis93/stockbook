#!/usr/bin/env python3
"""
Layer-specific test coverage checker for StockBook application.

This script analyzes test coverage on a per-layer basis, allowing different
coverage thresholds for different architectural layers (domain, application,
infrastructure, presentation).
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml
from coverage import Coverage
from coverage.results import Analysis


class LayerCoverageChecker:
    """Checks test coverage for each architectural layer."""

    def __init__(self, config_path: str = "hooks/layer-coverage.yaml"):
        """Initialize the coverage checker with configuration."""
        self.config_path = Path(config_path)
        self.project_root = Path.cwd()
        self.config = self._load_config()
        self.coverage_data_file = ".coverage"

    def _load_config(self) -> Dict:
        """Load layer coverage configuration from YAML file."""
        if not self.config_path.exists():
            # Default configuration if file doesn't exist
            return {
                "layers": {
                    "domain": {"path": "src/domain", "threshold": 100},
                    "application": {"path": "src/application", "threshold": 90},
                    "infrastructure": {"path": "src/infrastructure", "threshold": 85},
                    "presentation": {"path": "src/presentation", "threshold": 75},
                },
            }

        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _analyze_single_layer(
        self, cov: Coverage, layer_name: str, layer_config: Dict
    ) -> Optional[Dict]:
        """Analyze coverage for a single layer."""
        layer_path = self.project_root / layer_config["path"]

        if not layer_path.exists():
            print(f"⚠️  Layer path '{layer_path}' does not exist, skipping.")
            return None

        # Get all Python files in the layer
        layer_files = list(layer_path.rglob("*.py"))
        layer_files = [str(f) for f in layer_files if not f.name.startswith("test_")]

        if not layer_files:
            print(f"⚠️  No Python files found in layer '{layer_name}', skipping.")
            return None

        # Analyze coverage for layer files
        layer_statements = 0
        layer_missing = 0
        layer_excluded = 0
        file_details = []

        for file_path in layer_files:
            try:
                # Get coverage analysis data
                analysis = cov.analysis2(file_path)
                # analysis2 returns: filename, statements, excluded, missing, missing_formatted
                filename, statements, excluded, missing, missing_formatted = analysis
                statements = len(statements) if statements else 0
                missing = len(missing) if missing else 0
                excluded = len(excluded) if excluded else 0

                layer_statements += statements
                layer_missing += missing
                layer_excluded += excluded

                if statements > 0:
                    file_coverage = ((statements - missing) / statements) * 100
                    relative_path = Path(file_path).relative_to(self.project_root)
                    file_details.append(
                        {
                            "path": str(relative_path),
                            "statements": statements,
                            "missing": missing,
                            "coverage": round(file_coverage, 2),
                        }
                    )
            except Exception as e:
                print(f"⚠️  Error analyzing {file_path}: {e}")

        # Calculate layer coverage
        if layer_statements > 0:
            layer_coverage = (
                (layer_statements - layer_missing) / layer_statements
            ) * 100
        else:
            layer_coverage = 100.0

        return {
            "coverage": round(layer_coverage, 2),
            "threshold": layer_config["threshold"],
            "passed": layer_coverage >= layer_config["threshold"],
            "statements": layer_statements,
            "missing": layer_missing,
            "excluded": layer_excluded,
            "files": sorted(file_details, key=lambda x: x["coverage"]),
        }

    def analyze_layer_coverage(self) -> Dict[str, Dict]:
        """Analyze coverage for each configured layer."""
        if not Path(self.coverage_data_file).exists():
            print(f"❌ Coverage data file '{self.coverage_data_file}' not found.")
            print("   Please run pytest with coverage first.")
            sys.exit(1)

        # Load existing coverage data
        cov = Coverage(data_file=self.coverage_data_file)
        cov.load()

        results = {}

        for layer_name, layer_config in self.config["layers"].items():
            layer_result = self._analyze_single_layer(cov, layer_name, layer_config)
            if layer_result:
                results[layer_name] = layer_result

        return results

    def generate_report(self, results: Dict[str, Dict]) -> Tuple[str, bool]:
        """Generate a detailed coverage report and determine if all thresholds are met."""
        report_lines = []
        all_passed = True

        # Header
        report_lines.append("\n" + "=" * 80)
        report_lines.append("LAYER-SPECIFIC COVERAGE REPORT")
        report_lines.append("=" * 80 + "\n")

        # Layer-by-layer breakdown
        report_lines.append("Coverage by Architectural Layer:")
        report_lines.append("-" * 60)

        for layer_name, layer_data in results.items():

            status = "✅" if layer_data["passed"] else "❌"
            report_lines.append(
                f"\n{status} {layer_name.upper()} Layer: {layer_data['coverage']:.2f}% "
                f"(threshold: {layer_data['threshold']}%)"
            )
            report_lines.append(
                f"   Statements: {layer_data['statements']}, "
                f"Missing: {layer_data['missing']}, "
                f"Excluded: {layer_data['excluded']}"
            )

            if not layer_data["passed"]:
                all_passed = False
                # Show files with lowest coverage in this layer
                low_coverage_files = [
                    f
                    for f in layer_data["files"]
                    if f["coverage"] < layer_data["threshold"]
                ]
                if low_coverage_files:
                    report_lines.append(f"\n   Files below threshold in {layer_name}:")
                    for file_info in low_coverage_files[:5]:  # Show top 5
                        report_lines.append(
                            f"     - {file_info['path']}: {file_info['coverage']:.1f}% "
                            f"({file_info['missing']} lines missing)"
                        )
                    if len(low_coverage_files) > 5:
                        report_lines.append(
                            f"     ... and {len(low_coverage_files) - 5} more files"
                        )

        # Summary
        report_lines.append("\n" + "=" * 80)
        if all_passed:
            report_lines.append("✅ All coverage thresholds met! 🎉")
        else:
            report_lines.append(
                "❌ Some coverage thresholds not met. Please add more tests."
            )
        report_lines.append("=" * 80 + "\n")

        return "\n".join(report_lines), all_passed

    def save_json_report(
        self, results: Dict[str, Dict], output_path: str = "coverage-layers.json"
    ):
        """Save detailed coverage results as JSON for further processing."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"📊 Detailed coverage report saved to {output_path}")

    def run(self) -> bool:
        """Run the layer coverage check and return success status."""
        try:
            # Analyze coverage
            results = self.analyze_layer_coverage()

            # Generate and print report
            report, all_passed = self.generate_report(results)
            print(report)

            # Save detailed JSON report
            self.save_json_report(results)

            return all_passed

        except Exception as e:
            print(f"❌ Error running layer coverage check: {e}")
            import traceback

            traceback.print_exc()
            return False


def main():
    """Main entry point for the script."""
    checker = LayerCoverageChecker()
    success = checker.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
