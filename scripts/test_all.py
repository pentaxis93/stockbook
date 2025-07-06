#!/usr/bin/env python3
"""Unified quality check script for the project."""

import subprocess
import sys


# Color codes for output
GREEN = "\033[0;32m"
RED = "\033[0;31m"
BLUE = "\033[0;34m"
YELLOW = "\033[1;33m"
NC = "\033[0m"  # No Color


def run_command(cmd: list[str], description: str) -> tuple[int, str]:
    """Run a command and return its exit code and output."""
    print(f"\n{BLUE}[{description}] Running...{NC}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print(f"{GREEN}[{description}] ✓ Passed{NC}")
        else:
            print(f"{RED}[{description}] ✗ Failed{NC}")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
        return result.returncode, result.stdout + result.stderr
    except Exception as e:
        print(f"{RED}[{description}] ✗ Error: {e}{NC}")
        return 1, str(e)


def main() -> None:
    """Run all quality checks."""
    print(f"{YELLOW}Running all quality checks...{NC}")

    # Define all checks in order
    checks = [
        # Format and fix first
        (
            ["python", "-m", "ruff", "check", "--fix", "--unsafe-fixes", "."],
            "Ruff Auto-fix",
        ),
        (["python", "-m", "ruff", "format", "."], "Ruff Format"),
        # Then check
        (["python", "-m", "ruff", "check", "."], "Ruff Lint"),
        (["python", "-m", "pyright"], "Type Check"),
        (
            ["pytest"],
            "Tests & Coverage",
        ),
        (["python", "-m", "ruff", "check", "--select", "C901", "src/"], "Complexity"),
        (["lint-imports"], "Import Architecture"),
        (
            [
                "docstr-coverage",
                "src/",
                "--fail-under",
                "100.0",
                "--skip-magic",
                "--percentage-only",
            ],
            "Docstring Coverage",
        ),
        (["python", "-m", "ruff", "check", "--select", "S", "src/"], "Security (Ruff)"),
        (["python", "-m", "pip_audit"], "Security (Dependencies)"),
    ]

    # Run all checks
    failed = False
    for cmd, description in checks:
        exit_code, _ = run_command(cmd, description)
        if exit_code != 0:
            failed = True

    # Final result
    print()
    if failed:
        print(f"{RED}❌ One or more quality checks failed{NC}")
        sys.exit(1)
    else:
        print(f"{GREEN}✅ All quality checks passed!{NC}")
        sys.exit(0)


if __name__ == "__main__":
    main()
