#!/usr/bin/env python3
"""Unified quality check script for the project."""

import logging
import re
import subprocess
import sys
import time

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


def _extract_pytest_metrics(output: str) -> str:
    """Extract pytest test count metrics."""
    match = re.search(r"(\d+) passed", output)
    if not match:
        return ""

    passed = match.group(1)
    parts = [f"{passed} passed"]

    failed_match = re.search(r"(\d+) failed", output)
    if failed_match:
        parts.append(f"{failed_match.group(1)} failed")

    skipped_match = re.search(r"(\d+) skipped", output)
    if skipped_match:
        parts.append(f"{skipped_match.group(1)} skipped")

    return ", ".join(parts)


def _extract_ruff_metrics(cmd: list[str], output: str) -> str:
    """Extract ruff linting metrics."""
    if "--fix" in cmd:
        match = re.search(r"Fixed (\d+) error", output)
        if match:
            return f"fixed {match.group(1)} issues"
        if "All checks passed" in output or not output.strip():
            return "no issues found"
    else:
        match = re.search(r"Found (\d+) error", output)
        if match:
            return f"{match.group(1)} issues"
    return ""


def _extract_coverage_metrics(output: str) -> str:
    """Extract coverage percentage."""
    match = re.search(r"(\d+\.?\d*)%", output)
    if match:
        return f"{match.group(1)}% coverage"
    return ""


def _extract_pyright_metrics(output: str) -> str:
    """Extract pyright type checking metrics."""
    if "0 errors" in output:
        match = re.search(r"(\d+) files", output)
        if match:
            return f"{match.group(1)} files, no errors"
    else:
        error_match = re.search(r"(\d+) errors?", output)
        if error_match:
            return f"{error_match.group(1)} errors"
    return ""


def _extract_pip_audit_metrics(output: str) -> str:
    """Extract pip audit vulnerability metrics."""
    if "No known vulnerabilities" in output:
        return "no vulnerabilities"
    match = re.search(r"(\d+) vulnerabilit", output)
    if match:
        return f"{match.group(1)} vulnerabilities"
    return ""


def extract_metrics(cmd: list[str], output: str) -> str:
    """Extract key metrics from command output."""
    if "pytest" in cmd:
        return _extract_pytest_metrics(output)

    if "ruff" in cmd and "check" in cmd:
        return _extract_ruff_metrics(cmd, output)

    if "docstr-coverage" in cmd:
        return _extract_coverage_metrics(output)

    if "pyright" in cmd:
        return _extract_pyright_metrics(output)

    if "pip_audit" in cmd:
        return _extract_pip_audit_metrics(output)

    return ""


def run_command(
    cmd: list[str],
    description: str,
    current: int,
    total: int,
) -> tuple[int, str]:
    """Run a command and return its exit code and output."""
    logger.info("\n%s[%d/%d] %s: Running...%s", BLUE, current, total, description, NC)

    start_time = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        elapsed = time.time() - start_time

        output = result.stdout + result.stderr
        metrics = extract_metrics(cmd, output)

        if result.returncode == 0:
            status_msg = "%s[%d/%d] %s: ✓ Passed (%.1fs)%s"
            args = [GREEN, current, total, description, elapsed, NC]
            if metrics:
                status_msg += " - %s"
                args.append(metrics)
            logger.info(status_msg, *args)
        else:
            logger.error(
                "%s[%d/%d] %s: ✗ Failed (%.1fs)%s",
                RED,
                current,
                total,
                description,
                elapsed,
                NC,
            )
            # Extract error summary instead of dumping all output
            if "error" in output.lower():
                lines = output.strip().split("\n")
                # Get first 3 error lines
                error_lines = [line for line in lines if "error" in line.lower()]
                error_lines = error_lines[:3]
                for line in error_lines:
                    logger.error("  %s", line.strip())
            else:
                # If no clear error pattern, show first few lines
                lines = output.strip().split("\n")[:5]
                for line in lines:
                    if line.strip():
                        logger.error("  %s", line.strip())
    except (subprocess.SubprocessError, OSError) as e:
        elapsed = time.time() - start_time
        logger.exception(
            "%s[%d/%d] %s: ✗ Error (%.1fs)%s",
            RED,
            current,
            total,
            description,
            elapsed,
            NC,
        )
        return 1, str(e)
    else:
        return result.returncode, output


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
    total_checks = len(checks)
    for i, (cmd, description) in enumerate(checks, 1):
        exit_code, _ = run_command(cmd, description, i, total_checks)
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
