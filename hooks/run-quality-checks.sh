#!/bin/bash

# Pre-commit hook to run pytest, pylint, pyright, black, and isort
# This hook ensures code quality before allowing commits

set -e

echo "Running quality checks (formatting already handled by previous hooks)..."

# Run pylint with layer-specific configurations from pyproject.toml
# Use command-line overrides to apply layer-specific settings

echo "Running pylint with strictest rules on core business logic..."
CORE_FILES=$(find src/domain/ src/application/ src/infrastructure/ -name "*.py" 2>/dev/null || true)
if [ -n "$CORE_FILES" ]; then
    # Core business logic - strictest rules (enhanced with quality rules enabled)
    CORE_DISABLE="too-few-public-methods,too-many-public-methods,too-many-instance-attributes,unnecessary-pass,wrong-import-order,ungrouped-imports,line-too-long,too-many-positional-arguments,fixme"
    if ! PYTHONPATH=. pylint --disable="$CORE_DISABLE" \
        --allowed-redefined-builtins=id \
        --max-args=12 --max-locals=10 --max-returns=8 --max-branches=10 \
        --max-statements=30 --max-positional-arguments=8 \
        --min-similarity-lines=10 \
        --good-names=i,j,k,ex,Run,_,id \
        --docstring-min-length=10 \
        $CORE_FILES; then
        echo "❌ Pylint strict check failed on core business logic. Fix the issues before committing."
        exit 1
    fi
fi

echo "Running pylint with moderate rules on presentation layer..."
PRESENTATION_FILES=$(find src/presentation/ -name "*.py" 2>/dev/null || true)
if [ -n "$PRESENTATION_FILES" ]; then
    # Presentation layer - moderate rules (improved complexity limits)
    PRES_DISABLE="too-few-public-methods,too-many-public-methods,too-many-instance-attributes,wrong-import-order,ungrouped-imports,line-too-long,no-member,too-many-arguments,too-many-positional-arguments,too-many-locals,fixme,duplicate-code,import-outside-toplevel,broad-exception-caught,missing-class-docstring,missing-function-docstring,consider-using-join,reimported"
    if ! PYTHONPATH=. pylint --disable="$PRES_DISABLE" \
        --allowed-redefined-builtins=id \
        --max-args=10 --max-locals=15 --max-returns=8 --max-branches=15 --max-statements=40 \
        --docstring-min-length=10 \
        $PRESENTATION_FILES; then
        echo "❌ Pylint moderate check failed on presentation layer. Fix the issues before committing."
        exit 1
    fi
fi

echo "Running pylint with lenient rules on configuration files..."
CONFIG_FILES=$(find . -maxdepth 1 -name "*.py" -not -path "./tests/*" 2>/dev/null || true)
CONFIG_FILES="$CONFIG_FILES $(find dependency_injection/ -name "*.py" 2>/dev/null || true)"
if [ -n "$CONFIG_FILES" ]; then
    # Configuration files - most lenient
    CONFIG_DISABLE="too-few-public-methods,too-many-public-methods,too-many-instance-attributes,wrong-import-order,ungrouped-imports,line-too-long,no-member,missing-class-docstring,missing-function-docstring,missing-module-docstring,invalid-name,too-many-arguments,too-many-positional-arguments,too-many-locals,import-outside-toplevel,broad-exception-caught,duplicate-code,fixme,global-statement,global-variable-not-assigned,wildcard-import,unused-wildcard-import,c-extension-no-member,consider-iterating-dictionary"
    if ! PYTHONPATH=. pylint --disable="$CONFIG_DISABLE" \
        --allowed-redefined-builtins=id \
        $CONFIG_FILES; then
        echo "❌ Pylint lenient check failed on configuration files. Fix the issues before committing."
        exit 1
    fi
fi

echo "Running pylint with lenient rules on test files..."
TEST_FILES=$(find ./tests -name "*.py" 2>/dev/null || true)
if [ -n "$TEST_FILES" ]; then
    # Test files - lenient rules
    TEST_DISABLE="too-few-public-methods,too-many-public-methods,too-many-instance-attributes,wrong-import-order,ungrouped-imports,line-too-long,no-member,redefined-outer-name,attribute-defined-outside-init,duplicate-code,unused-variable,unused-argument,protected-access,singleton-comparison,pointless-statement,unnecessary-pass,broad-exception-caught,comparison-with-itself,unexpected-keyword-arg,unused-import,logging-fstring-interpolation,no-else-return,import-outside-toplevel,unnecessary-negation,missing-class-docstring,missing-function-docstring,abstract-class-instantiated,consider-using-with,too-many-arguments,too-many-positional-arguments,fixme,too-many-lines"
    if ! PYTHONPATH=. pylint --disable="$TEST_DISABLE" \
        --allowed-redefined-builtins=id \
        $TEST_FILES; then
        echo "❌ Pylint lenient check failed on test files. Fix the issues before committing."
        exit 1
    fi
fi

echo "Running pyright type checker..."
if ! pyright; then
    echo "❌ Pyright type check failed. Fix the type issues before committing."
    exit 1
fi

# Run pytest with coverage (configured in pyproject.toml)
echo "Running tests with pytest and coverage requirements..."
if ! pytest; then
    echo "❌ Tests failed or coverage below required threshold. Fix the issues before committing."
    exit 1
fi

echo "✅ All pre-commit checks passed!"
exit 0