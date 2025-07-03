#!/bin/bash

# Pre-commit hook to run quality checks using the Makefile
# This ensures consistency between pre-commit hooks and CI/CD pipeline
# All quality check logic is defined in the Makefile for a single source of truth

set -e

# Change to the repository root directory
cd "$(git rev-parse --show-toplevel)"

echo "Running quality checks via Makefile..."
echo "This ensures consistency with CI/CD pipeline..."

# Run the parallel quality checks defined in Makefile
make quality-parallel

# Exit with the make command's exit code
exit $?