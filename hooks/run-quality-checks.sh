#!/bin/bash

# Pre-commit hook to run pytest, pylint, pyright, mypy, black, and isort
# This hook ensures maximum code quality before allowing commits
# Optimized for parallel execution, caching, and incremental processing

set -e

# Track background processes for parallel execution
declare -a PYLINT_PIDS=()
declare -a PYLINT_RESULTS=()

echo "Running quality checks (formatting already handled by previous hooks)..."
echo "Using parallel execution and incremental processing for faster performance..."

# Get list of changed files for incremental processing
CHANGED_FILES=$(git diff --cached --name-only --diff-filter=ACMR | grep '\.py$' || true)
if [ -z "$CHANGED_FILES" ]; then
    # If no staged files, check all files (for --all-files runs)
    CHANGED_FILES=$(find . -name "*.py" -not -path "./.venv/*" -not -path "./venv/*" -not -path "./.git/*" | head -20)
fi

echo "Processing $(echo "$CHANGED_FILES" | wc -w) Python files..."

# Function to run pylint check in background
run_pylint_check() {
    local layer_name="$1"
    local files="$2"
    local disable_rules="$3"
    local extra_args="$4"
    local temp_file="/tmp/pylint_${layer_name}_$$"
    
    {
        # Early exit if no files to check
        if [ -z "$files" ] || [ "$files" = " " ]; then
            echo "⏭️  No files found for $layer_name layer, skipping..." > "$temp_file"
            echo "0" > "${temp_file}.exit"
            return 0
        fi
        
        # Count files for progress indication
        file_count=$(echo "$files" | wc -w)
        echo "🔍 Running pylint on $layer_name layer ($file_count files)..." > "$temp_file"
        
        # Run pylint with optimizations
        if PYTHONPATH=. pylint -j 0 --persistent=yes --disable="$disable_rules" $extra_args $files >> "$temp_file" 2>&1; then
            echo "✅ Pylint $layer_name check passed" >> "$temp_file"
            echo "0" > "${temp_file}.exit"
        else
            echo "❌ Pylint $layer_name check failed. Fix the issues before committing." >> "$temp_file"
            echo "1" > "${temp_file}.exit"
        fi
    } &
    
    local pid=$!
    PYLINT_PIDS+=("$pid")
    PYLINT_RESULTS+=("$temp_file")
    
    return 0
}

# Filter changed files by layer for incremental processing
echo "Categorizing changed files by layer..."
CORE_FILES=""
PRESENTATION_FILES=""
CONFIG_FILES=""
TEST_FILES=""

for file in $CHANGED_FILES; do
    if [[ "$file" == src/domain/* ]] || [[ "$file" == src/application/* ]] || [[ "$file" == src/infrastructure/* ]]; then
        CORE_FILES="$CORE_FILES $file"
    elif [[ "$file" == src/presentation/* ]]; then
        PRESENTATION_FILES="$PRESENTATION_FILES $file"
    elif [[ "$file" == tests/* ]]; then
        TEST_FILES="$TEST_FILES $file"
    else
        CONFIG_FILES="$CONFIG_FILES $file"
    fi
done

# Trim whitespace
CORE_FILES=$(echo "$CORE_FILES" | xargs)
PRESENTATION_FILES=$(echo "$PRESENTATION_FILES" | xargs)
CONFIG_FILES=$(echo "$CONFIG_FILES" | xargs)
TEST_FILES=$(echo "$TEST_FILES" | xargs)

# Start all pylint checks in parallel
echo "Starting parallel pylint analysis..."

# Core business logic - strictest rules (optimized for speed)
CORE_DISABLE="too-few-public-methods,too-many-public-methods,too-many-instance-attributes,unnecessary-pass,wrong-import-order,ungrouped-imports,line-too-long,too-many-positional-arguments,fixme,duplicate-code"
CORE_ARGS="--allowed-redefined-builtins=id --max-args=12 --max-locals=5 --max-returns=8 --max-branches=8 --max-statements=15 --max-positional-arguments=8 --good-names=i,j,k,ex,Run,_,id --docstring-min-length=10"
run_pylint_check "core" "$CORE_FILES" "$CORE_DISABLE" "$CORE_ARGS"

# Presentation layer - moderate rules  
PRES_DISABLE="too-few-public-methods,too-many-public-methods,too-many-instance-attributes,wrong-import-order,ungrouped-imports,line-too-long,no-member,too-many-arguments,too-many-positional-arguments,fixme,duplicate-code,import-outside-toplevel,broad-exception-caught,consider-using-join,reimported"
PRES_ARGS="--allowed-redefined-builtins=id --max-args=6 --max-locals=10 --max-returns=8 --max-branches=15 --max-statements=30 --docstring-min-length=10"
run_pylint_check "presentation" "$PRESENTATION_FILES" "$PRES_DISABLE" "$PRES_ARGS"

# Configuration files - most lenient
CONFIG_DISABLE="too-few-public-methods,too-many-public-methods,too-many-instance-attributes,wrong-import-order,ungrouped-imports,line-too-long,no-member,missing-class-docstring,missing-function-docstring,missing-module-docstring,invalid-name,too-many-arguments,too-many-positional-arguments,too-many-locals,import-outside-toplevel,broad-exception-caught,duplicate-code,fixme,global-statement,global-variable-not-assigned,wildcard-import,unused-wildcard-import,c-extension-no-member,consider-iterating-dictionary"
CONFIG_ARGS="--allowed-redefined-builtins=id"
run_pylint_check "config" "$CONFIG_FILES" "$CONFIG_DISABLE" "$CONFIG_ARGS"

# Test files - lenient rules
TEST_DISABLE="too-few-public-methods,too-many-public-methods,too-many-instance-attributes,wrong-import-order,ungrouped-imports,line-too-long,no-member,redefined-outer-name,attribute-defined-outside-init,duplicate-code,unused-variable,unused-argument,protected-access,singleton-comparison,pointless-statement,unnecessary-pass,broad-exception-caught,comparison-with-itself,unexpected-keyword-arg,unused-import,logging-fstring-interpolation,no-else-return,import-outside-toplevel,unnecessary-negation,missing-class-docstring,missing-function-docstring,abstract-class-instantiated,consider-using-with,too-many-arguments,too-many-positional-arguments,fixme,too-many-lines"
TEST_ARGS="--allowed-redefined-builtins=id"
run_pylint_check "tests" "$TEST_FILES" "$TEST_DISABLE" "$TEST_ARGS"

# Start pyright, mypy, and pytest in parallel with pylint
echo "Starting pyright type checker in parallel..."
PYRIGHT_TEMP="/tmp/pyright_$$"
{
    if pyright > "$PYRIGHT_TEMP" 2>&1; then
        echo "✅ Pyright type check passed" >> "$PYRIGHT_TEMP"
        echo "0" > "${PYRIGHT_TEMP}.exit"
    else
        echo "❌ Pyright type check failed. Fix the type issues before committing." >> "$PYRIGHT_TEMP"
        echo "1" > "${PYRIGHT_TEMP}.exit"
    fi
} &
PYRIGHT_PID=$!

echo "Starting mypy type checker with caching in parallel..."
MYPY_TEMP="/tmp/mypy_$$"
{
    if mypy src --explicit-package-bases --cache-dir=.mypy_cache --incremental > "$MYPY_TEMP" 2>&1; then
        echo "✅ Mypy type check passed" >> "$MYPY_TEMP"
        echo "0" > "${MYPY_TEMP}.exit"
    else
        echo "❌ Mypy type check failed. Fix the type issues before committing." >> "$MYPY_TEMP"
        echo "1" > "${MYPY_TEMP}.exit"
    fi
} &
MYPY_PID=$!

echo "Starting pytest with parallel execution and caching..."
PYTEST_TEMP="/tmp/pytest_$$"
{
    if pytest -n auto --lf --ff > "$PYTEST_TEMP" 2>&1; then
        echo "✅ Tests passed with required coverage" >> "$PYTEST_TEMP"
        echo "0" > "${PYTEST_TEMP}.exit"
    else
        echo "❌ Tests failed or coverage below required threshold. Fix the issues before committing." >> "$PYTEST_TEMP"
        echo "1" > "${PYTEST_TEMP}.exit"
    fi
} &
PYTEST_PID=$!

echo "Starting flake8 cognitive complexity analysis..."
FLAKE8_TEMP="/tmp/flake8_$$"
{
    if flake8 src/domain/ src/application/ > "$FLAKE8_TEMP" 2>&1; then
        echo "✅ Flake8 cognitive complexity check passed" >> "$FLAKE8_TEMP"
        echo "0" > "${FLAKE8_TEMP}.exit"
    else
        echo "❌ Flake8 cognitive complexity check failed. Consider refactoring complex functions." >> "$FLAKE8_TEMP"
        echo "1" > "${FLAKE8_TEMP}.exit"
    fi
} &
FLAKE8_PID=$!

echo "Starting import-linter architectural constraint analysis..."
IMPORTLINTER_TEMP="/tmp/importlinter_$$"
{
    if lint-imports > "$IMPORTLINTER_TEMP" 2>&1; then
        echo "✅ Import-linter architectural constraints check passed" >> "$IMPORTLINTER_TEMP"
        echo "0" > "${IMPORTLINTER_TEMP}.exit"
    else
        echo "❌ Import-linter found architectural violations. Refactor to improve layer separation." >> "$IMPORTLINTER_TEMP"
        echo "1" > "${IMPORTLINTER_TEMP}.exit"
    fi
} &
IMPORTLINTER_PID=$!

echo "Starting pydocstyle docstring quality analysis..."
PYDOCSTYLE_TEMP="/tmp/pydocstyle_$$"
{
    if pydocstyle src/ > "$PYDOCSTYLE_TEMP" 2>&1; then
        echo "✅ Pydocstyle docstring quality check passed" >> "$PYDOCSTYLE_TEMP"
        echo "0" > "${PYDOCSTYLE_TEMP}.exit"
    else
        echo "❌ Pydocstyle found docstring quality issues. Improve docstring formatting and completeness." >> "$PYDOCSTYLE_TEMP"
        echo "1" > "${PYDOCSTYLE_TEMP}.exit"
    fi
} &
PYDOCSTYLE_PID=$!

echo "Starting docstr-coverage docstring coverage analysis..."
DOCSTRCOVERAGE_TEMP="/tmp/docstrcoverage_$$"
{
    if docstr-coverage src/ --fail-under 100.0 --skip-magic --percentage-only > "$DOCSTRCOVERAGE_TEMP" 2>&1; then
        echo "✅ Docstr-coverage docstring coverage check passed ($(cat "$DOCSTRCOVERAGE_TEMP")%)" >> "$DOCSTRCOVERAGE_TEMP"
        echo "0" > "${DOCSTRCOVERAGE_TEMP}.exit"
    else
        echo "❌ Docstr-coverage found insufficient docstring coverage. Add missing docstrings to meet 100% threshold." >> "$DOCSTRCOVERAGE_TEMP"
        echo "1" > "${DOCSTRCOVERAGE_TEMP}.exit"
    fi
} &
DOCSTRCOVERAGE_PID=$!

echo "Running security checks..."
BANDIT_TEMP="/tmp/bandit_$$"
{
    if bandit -r src/ -ll -i > "$BANDIT_TEMP" 2>&1; then
        echo "✅ Bandit security scan passed" >> "$BANDIT_TEMP"
        echo "0" > "${BANDIT_TEMP}.exit"
    else
        echo "❌ Bandit security scan found issues. Review security vulnerabilities." >> "$BANDIT_TEMP"
        echo "1" > "${BANDIT_TEMP}.exit"
    fi
} &
BANDIT_PID=$!


PIPAUDIT_TEMP="/tmp/pipaudit_$$"  
{
    if pip-audit > "$PIPAUDIT_TEMP" 2>&1; then
        echo "✅ pip-audit security scan passed" >> "$PIPAUDIT_TEMP"
        echo "0" > "${PIPAUDIT_TEMP}.exit"
    else
        echo "❌ pip-audit found security issues. Review dependencies." >> "$PIPAUDIT_TEMP"
        echo "1" > "${PIPAUDIT_TEMP}.exit"
    fi
} &
PIPAUDIT_PID=$!

# Wait for all pylint processes to complete with progress indication
echo "⏳ Waiting for pylint analysis to complete..."
HAS_PYLINT_ERRORS=0
COMPLETED_COUNT=0
TOTAL_PYLINT_CHECKS=${#PYLINT_PIDS[@]}

for i in "${!PYLINT_PIDS[@]}"; do
    wait "${PYLINT_PIDS[$i]}"
    result_file="${PYLINT_RESULTS[$i]}"
    
    COMPLETED_COUNT=$((COMPLETED_COUNT + 1))
    echo "📊 Pylint progress: $COMPLETED_COUNT/$TOTAL_PYLINT_CHECKS completed"
    
    # Display output
    cat "$result_file"
    
    # Check exit code
    if [ -f "${result_file}.exit" ]; then
        exit_code=$(cat "${result_file}.exit")
        if [ "$exit_code" != "0" ]; then
            HAS_PYLINT_ERRORS=1
        fi
    fi
    
    # Clean up temp files
    rm -f "$result_file" "${result_file}.exit"
done

# Wait for pyright and display results
echo "Waiting for pyright to complete..."
wait $PYRIGHT_PID
cat "$PYRIGHT_TEMP"
PYRIGHT_EXIT=$(cat "${PYRIGHT_TEMP}.exit")
rm -f "$PYRIGHT_TEMP" "${PYRIGHT_TEMP}.exit"

# Wait for mypy and display results
echo "Waiting for mypy to complete..."
wait $MYPY_PID
cat "$MYPY_TEMP"
MYPY_EXIT=$(cat "${MYPY_TEMP}.exit")
rm -f "$MYPY_TEMP" "${MYPY_TEMP}.exit"

# Wait for pytest and display results
echo "Waiting for pytest to complete..."
wait $PYTEST_PID
cat "$PYTEST_TEMP"
PYTEST_EXIT=$(cat "${PYTEST_TEMP}.exit")
rm -f "$PYTEST_TEMP" "${PYTEST_TEMP}.exit"

# Wait for flake8 and display results
echo "Waiting for flake8 cognitive complexity analysis to complete..."
wait $FLAKE8_PID
cat "$FLAKE8_TEMP"
FLAKE8_EXIT=$(cat "${FLAKE8_TEMP}.exit")
rm -f "$FLAKE8_TEMP" "${FLAKE8_TEMP}.exit"

# Wait for import-linter and display results
echo "Waiting for import-linter architectural analysis to complete..."
wait $IMPORTLINTER_PID
cat "$IMPORTLINTER_TEMP"
IMPORTLINTER_EXIT=$(cat "${IMPORTLINTER_TEMP}.exit")
rm -f "$IMPORTLINTER_TEMP" "${IMPORTLINTER_TEMP}.exit"

# Wait for pydocstyle and display results
echo "Waiting for pydocstyle docstring quality analysis to complete..."
wait $PYDOCSTYLE_PID
cat "$PYDOCSTYLE_TEMP"
PYDOCSTYLE_EXIT=$(cat "${PYDOCSTYLE_TEMP}.exit")
rm -f "$PYDOCSTYLE_TEMP" "${PYDOCSTYLE_TEMP}.exit"

# Wait for docstr-coverage and display results
echo "Waiting for docstr-coverage docstring coverage analysis to complete..."
wait $DOCSTRCOVERAGE_PID
cat "$DOCSTRCOVERAGE_TEMP"
DOCSTRCOVERAGE_EXIT=$(cat "${DOCSTRCOVERAGE_TEMP}.exit")
rm -f "$DOCSTRCOVERAGE_TEMP" "${DOCSTRCOVERAGE_TEMP}.exit"

# Wait for security tools and display results
echo "Waiting for bandit security scan to complete..."
wait $BANDIT_PID
cat "$BANDIT_TEMP"
BANDIT_EXIT=$(cat "${BANDIT_TEMP}.exit")
rm -f "$BANDIT_TEMP" "${BANDIT_TEMP}.exit"


echo "Waiting for pip-audit security scan to complete..."
wait $PIPAUDIT_PID
cat "$PIPAUDIT_TEMP"
PIPAUDIT_EXIT=$(cat "${PIPAUDIT_TEMP}.exit")
rm -f "$PIPAUDIT_TEMP" "${PIPAUDIT_TEMP}.exit"

# Check all results
if [ "$HAS_PYLINT_ERRORS" = "1" ] || [ "$PYRIGHT_EXIT" != "0" ] || [ "$MYPY_EXIT" != "0" ] || [ "$PYTEST_EXIT" != "0" ] || [ "$FLAKE8_EXIT" != "0" ] || [ "$IMPORTLINTER_EXIT" != "0" ] || [ "$PYDOCSTYLE_EXIT" != "0" ] || [ "$DOCSTRCOVERAGE_EXIT" != "0" ] || [ "$BANDIT_EXIT" != "0" ] || [ "$PIPAUDIT_EXIT" != "0" ]; then
    echo "❌ One or more quality checks failed. Please fix the issues before committing."
    exit 1
fi

echo "✅ All pre-commit checks passed!"
exit 0