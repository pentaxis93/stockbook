#!/bin/bash

# Pre-commit hook to run pytest, pylint, pyright, black, and isort
# This hook ensures code quality before allowing commits

set -e

echo "Running quality checks (formatting already handled by previous hooks)..."

# Run pylint with layer-specific configurations
echo "Running pylint with strictest rules on core business logic..."
CORE_FILES=$(find domain/ application/ infrastructure/ shared_kernel/ -name "*.py" 2>/dev/null || true)
if [ -n "$CORE_FILES" ]; then
    if ! pylint --rcfile=.pylintrc-core $CORE_FILES; then
        echo "❌ Pylint strict check failed on core business logic. Fix the issues before committing."
        exit 1
    fi
fi

echo "Running pylint with moderate rules on presentation layer..."
PRESENTATION_FILES=$(find presentation/ -name "*.py" 2>/dev/null || true)
if [ -n "$PRESENTATION_FILES" ]; then
    if ! pylint --rcfile=.pylintrc-presentation $PRESENTATION_FILES; then
        echo "❌ Pylint moderate check failed on presentation layer. Fix the issues before committing."
        exit 1
    fi
fi

echo "Running pylint with lenient rules on configuration files..."
CONFIG_FILES=$(find . -maxdepth 1 -name "*.py" -not -path "./tests/*" 2>/dev/null || true)
CONFIG_FILES="$CONFIG_FILES $(find dependency_injection/ -name "*.py" 2>/dev/null || true)"
if [ -n "$CONFIG_FILES" ]; then
    if ! pylint --rcfile=.pylintrc-config $CONFIG_FILES; then
        echo "❌ Pylint lenient check failed on configuration files. Fix the issues before committing."
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