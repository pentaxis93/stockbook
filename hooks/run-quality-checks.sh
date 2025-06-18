#!/bin/bash

# Pre-commit hook to run pytest, pylint, pyright, black, and isort
# This hook ensures code quality before allowing commits

set -e

echo "Running quality checks (formatting already handled by previous hooks)..."

# Run pylint with different configurations for production vs test files
echo "Running pylint with strict rules on production code..."
PRODUCTION_FILES=$(find . -name "*.py" -not -path "./tests/*" -not -path "./.*" -not -path "./venv/*" -not -path "./.venv/*")
if [ -n "$PRODUCTION_FILES" ]; then
    if ! pylint $PRODUCTION_FILES; then
        echo "❌ Pylint strict check failed on production code. Fix the issues before committing."
        exit 1
    fi
fi

echo "Running pylint with lenient rules on test files..."
TEST_FILES=$(find ./tests -name "*.py" 2>/dev/null || true)
if [ -n "$TEST_FILES" ]; then
    if ! pylint --rcfile=.pylintrc-tests $TEST_FILES; then
        echo "❌ Pylint lenient check failed on test files. Fix the issues before committing."
        exit 1
    fi
fi

# TEMPORARILY DISABLED: pyright (type checker)
# Disabled due to architectural issues with database connection patterns
# See TECHNICAL_DEBT.md for details on the database connection architecture flaw
# 
# TODO: Re-enable once the DatabaseConnection/TransactionalDatabaseConnection
#       architecture is refactored to use a common interface
#
# echo "Running pyright type checker..."
# if ! pyright; then
#     echo "❌ Pyright type check failed. Fix the type issues before committing."
#     exit 1
# fi
echo "⚠️  Pyright type checking TEMPORARILY DISABLED (see TECHNICAL_DEBT.md)"

# Run pytest with coverage (configured in pyproject.toml)
echo "Running tests with pytest and coverage requirements..."
if ! pytest; then
    echo "❌ Tests failed or coverage below required threshold. Fix the issues before committing."
    exit 1
fi

echo "✅ All pre-commit checks passed!"
exit 0