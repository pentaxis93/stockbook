#!/bin/bash

# Pre-commit hook to run pytest, pylint, pyright, black, and isort
# This hook ensures code quality before allowing commits
# Optimized for parallel execution and caching

set -e

# Track background processes for parallel execution
declare -a PYLINT_PIDS=()
declare -a PYLINT_RESULTS=()

echo "Running quality checks (formatting already handled by previous hooks)..."
echo "Using parallel execution for faster processing..."

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

# Discover files once for all pylint checks (optimization)
echo "Discovering Python files for analysis..."
CORE_FILES=$(find src/domain/ src/application/ src/infrastructure/ -name "*.py" 2>/dev/null | tr '\n' ' ' || true)
PRESENTATION_FILES=$(find src/presentation/ -name "*.py" 2>/dev/null | tr '\n' ' ' || true)
CONFIG_FILES="$(find . -maxdepth 1 -name "*.py" -not -path "./tests/*" 2>/dev/null | tr '\n' ' ' || true) $(find dependency_injection/ -name "*.py" 2>/dev/null | tr '\n' ' ' || true)"  
TEST_FILES=$(find ./tests -name "*.py" 2>/dev/null | tr '\n' ' ' || true)

# Start all pylint checks in parallel
echo "Starting parallel pylint analysis..."

# Core business logic - strictest rules
CORE_DISABLE="too-few-public-methods,too-many-public-methods,too-many-instance-attributes,unnecessary-pass,wrong-import-order,ungrouped-imports,line-too-long,too-many-positional-arguments,fixme"
CORE_ARGS="--allowed-redefined-builtins=id --max-args=12 --max-locals=10 --max-returns=8 --max-branches=10 --max-statements=30 --max-positional-arguments=8 --min-similarity-lines=10 --good-names=i,j,k,ex,Run,_,id --docstring-min-length=10"
run_pylint_check "core" "$CORE_FILES" "$CORE_DISABLE" "$CORE_ARGS"

# Presentation layer - moderate rules  
PRES_DISABLE="too-few-public-methods,too-many-public-methods,too-many-instance-attributes,wrong-import-order,ungrouped-imports,line-too-long,no-member,too-many-arguments,too-many-positional-arguments,too-many-locals,fixme,duplicate-code,import-outside-toplevel,broad-exception-caught,missing-class-docstring,missing-function-docstring,consider-using-join,reimported"
PRES_ARGS="--allowed-redefined-builtins=id --max-args=10 --max-locals=15 --max-returns=8 --max-branches=15 --max-statements=40 --docstring-min-length=10"
run_pylint_check "presentation" "$PRESENTATION_FILES" "$PRES_DISABLE" "$PRES_ARGS"

# Configuration files - most lenient
CONFIG_DISABLE="too-few-public-methods,too-many-public-methods,too-many-instance-attributes,wrong-import-order,ungrouped-imports,line-too-long,no-member,missing-class-docstring,missing-function-docstring,missing-module-docstring,invalid-name,too-many-arguments,too-many-positional-arguments,too-many-locals,import-outside-toplevel,broad-exception-caught,duplicate-code,fixme,global-statement,global-variable-not-assigned,wildcard-import,unused-wildcard-import,c-extension-no-member,consider-iterating-dictionary"
CONFIG_ARGS="--allowed-redefined-builtins=id"
run_pylint_check "config" "$CONFIG_FILES" "$CONFIG_DISABLE" "$CONFIG_ARGS"

# Test files - lenient rules
TEST_DISABLE="too-few-public-methods,too-many-public-methods,too-many-instance-attributes,wrong-import-order,ungrouped-imports,line-too-long,no-member,redefined-outer-name,attribute-defined-outside-init,duplicate-code,unused-variable,unused-argument,protected-access,singleton-comparison,pointless-statement,unnecessary-pass,broad-exception-caught,comparison-with-itself,unexpected-keyword-arg,unused-import,logging-fstring-interpolation,no-else-return,import-outside-toplevel,unnecessary-negation,missing-class-docstring,missing-function-docstring,abstract-class-instantiated,consider-using-with,too-many-arguments,too-many-positional-arguments,fixme,too-many-lines"
TEST_ARGS="--allowed-redefined-builtins=id"
run_pylint_check "tests" "$TEST_FILES" "$TEST_DISABLE" "$TEST_ARGS"

# Start pyright and pytest in parallel with pylint
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

echo "Starting pytest with parallel execution..."
PYTEST_TEMP="/tmp/pytest_$$"
{
    if pytest -n auto > "$PYTEST_TEMP" 2>&1; then
        echo "✅ Tests passed with required coverage" >> "$PYTEST_TEMP"
        echo "0" > "${PYTEST_TEMP}.exit"
    else
        echo "❌ Tests failed or coverage below required threshold. Fix the issues before committing." >> "$PYTEST_TEMP"
        echo "1" > "${PYTEST_TEMP}.exit"
    fi
} &
PYTEST_PID=$!

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

# Wait for pytest and display results
echo "Waiting for pytest to complete..."
wait $PYTEST_PID
cat "$PYTEST_TEMP"
PYTEST_EXIT=$(cat "${PYTEST_TEMP}.exit")
rm -f "$PYTEST_TEMP" "${PYTEST_TEMP}.exit"

# Check all results
if [ "$HAS_PYLINT_ERRORS" = "1" ] || [ "$PYRIGHT_EXIT" != "0" ] || [ "$PYTEST_EXIT" != "0" ]; then
    echo "❌ One or more quality checks failed. Please fix the issues before committing."
    exit 1
fi

echo "✅ All pre-commit checks passed!"
exit 0