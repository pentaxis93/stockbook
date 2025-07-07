#!/usr/bin/env python3
"""Unified quality check script for the project."""

import logging
import subprocess
import sys

# Color codes for output
GREEN = "\033[0;32m"
RED = "\033[0;31m"
BLUE = "\033[0;34m"
YELLOW = "\033[1;33m"
NC = "\033[0m"  # No Color


# Configure logging with color support
class ColoredFormatter(logging.Formatter):
    """Custom formatter that preserves color codes."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record without stripping color codes."""
        return record.getMessage()


# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(ColoredFormatter())
logger.addHandler(handler)


def run_command(cmd: list[str], description: str) -> tuple[int, str]:
    """Run a command and return its exit code and output."""
    logger.info("\n%s[%s] Running...%s", BLUE, description, NC)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            logger.info("%s[%s] ✓ Passed%s", GREEN, description, NC)
        else:
            logger.error("%s[%s] ✗ Failed%s", RED, description, NC)
            if result.stdout:
                logger.error(result.stdout)
            if result.stderr:
                logger.error(result.stderr)
        return result.returncode, result.stdout + result.stderr
    except Exception as e:
        logger.error("%s[%s] ✗ Error: %s%s", RED, description, e, NC)
        return 1, str(e)


def main() -> None:
    """Run all quality checks."""
    logger.info("%sRunning all quality checks...%s", YELLOW, NC)

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
    logger.info("")
    if failed:
        logger.error("%s❌ One or more quality checks failed%s", RED, NC)
        sys.exit(1)
    else:
        logger.info("%s✅ All quality checks passed!%s", GREEN, NC)
        sys.exit(0)


if __name__ == "__main__":
    main()
