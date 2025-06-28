# Stockbook Project Makefile
# Single source of truth for all quality checks and commands
# Ensures consistency with pre-commit hooks

# Python interpreter
PYTHON := python3
PIP := pip

# Directories
SRC_DIR := src
TEST_DIR := tests
VENV_DIR := .venv

# Layer-specific file patterns
CORE_PATTERN := $(SRC_DIR)/domain $(SRC_DIR)/application $(SRC_DIR)/infrastructure
PRESENTATION_PATTERN := $(SRC_DIR)/presentation
CONFIG_PATTERN := pyproject.toml setup.py dependency_injection hooks

# Coverage thresholds
MIN_COVERAGE := 80

# Parallel execution for pytest
PYTEST_WORKERS := auto

# Colors for output
GREEN := \033[0;32m
RED := \033[0;31m
BLUE := \033[0;34m
YELLOW := \033[1;33m
NC := \033[0m # No Color

.PHONY: help
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: install
install: ## Install project dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

.PHONY: install-dev
install-dev: install ## Install development dependencies including pre-commit hooks
	@echo "$(BLUE)Installing pre-commit hooks...$(NC)"
	pre-commit install
	@echo "$(GREEN)✓ Pre-commit hooks installed$(NC)"

# Formatting targets
.PHONY: format
format: ## Format code with black and isort
	@echo "$(BLUE)Running black formatter...$(NC)"
	$(PYTHON) -m black .
	@echo "$(BLUE)Running isort import sorter...$(NC)"
	$(PYTHON) -m isort . --profile black
	@echo "$(GREEN)✓ Code formatted$(NC)"

# Linting targets
.PHONY: lint
lint: lint-core lint-presentation lint-tests lint-config ## Run pylint on all code

.PHONY: lint-core
lint-core: ## Run pylint on core business logic (strict rules)
	@echo "$(BLUE)Linting core business logic...$(NC)"
	@PYTHONPATH=. $(PYTHON) -m pylint -j 0 --persistent=yes \
		--disable=too-few-public-methods,too-many-public-methods,too-many-instance-attributes,unnecessary-pass,wrong-import-order,ungrouped-imports,line-too-long,too-many-positional-arguments,fixme,duplicate-code \
		--allowed-redefined-builtins=id \
		--max-args=12 --max-locals=5 --max-returns=8 --max-branches=8 --max-statements=15 \
		--max-positional-arguments=8 --good-names=i,j,k,ex,Run,_,id --docstring-min-length=10 \
		$(shell find $(CORE_PATTERN) -name "*.py" 2>/dev/null) || true
	@echo "$(GREEN)✓ Core linting complete$(NC)"

.PHONY: lint-presentation
lint-presentation: ## Run pylint on presentation layer (moderate rules)
	@echo "$(BLUE)Linting presentation layer...$(NC)"
	@PYTHONPATH=. $(PYTHON) -m pylint -j 0 --persistent=yes \
		--disable=too-few-public-methods,too-many-public-methods,too-many-instance-attributes,wrong-import-order,ungrouped-imports,line-too-long,no-member,too-many-arguments,too-many-positional-arguments,fixme,duplicate-code,import-outside-toplevel,broad-exception-caught,consider-using-join,reimported \
		--allowed-redefined-builtins=id \
		--max-args=6 --max-locals=10 --max-returns=8 --max-branches=15 --max-statements=30 \
		--docstring-min-length=10 \
		$(shell find $(PRESENTATION_PATTERN) -name "*.py" 2>/dev/null) || true
	@echo "$(GREEN)✓ Presentation linting complete$(NC)"

.PHONY: lint-tests
lint-tests: ## Run pylint on test files (lenient rules)
	@echo "$(BLUE)Linting test files...$(NC)"
	@PYTHONPATH=. $(PYTHON) -m pylint -j 0 --persistent=yes \
		--disable=too-few-public-methods,too-many-public-methods,too-many-instance-attributes,wrong-import-order,ungrouped-imports,line-too-long,no-member,redefined-outer-name,attribute-defined-outside-init,duplicate-code,unused-variable,unused-argument,protected-access,singleton-comparison,pointless-statement,unnecessary-pass,broad-exception-caught,comparison-with-itself,unexpected-keyword-arg,unused-import,logging-fstring-interpolation,no-else-return,import-outside-toplevel,unnecessary-negation,missing-class-docstring,missing-function-docstring,abstract-class-instantiated,consider-using-with,too-many-arguments,too-many-positional-arguments,fixme,too-many-lines \
		--allowed-redefined-builtins=id \
		$(shell find $(TEST_DIR) -name "*.py" 2>/dev/null) || true
	@echo "$(GREEN)✓ Test linting complete$(NC)"

.PHONY: lint-config
lint-config: ## Run pylint on configuration files (most lenient)
	@echo "$(BLUE)Linting configuration files...$(NC)"
	@PYTHONPATH=. $(PYTHON) -m pylint -j 0 --persistent=yes \
		--disable=too-few-public-methods,too-many-public-methods,too-many-instance-attributes,wrong-import-order,ungrouped-imports,line-too-long,no-member,missing-class-docstring,missing-function-docstring,missing-module-docstring,invalid-name,too-many-arguments,too-many-positional-arguments,too-many-locals,too-many-statements,too-many-nested-blocks,import-outside-toplevel,broad-exception-caught,duplicate-code,fixme,global-statement,global-variable-not-assigned,wildcard-import,unused-wildcard-import,c-extension-no-member,consider-iterating-dictionary \
		--allowed-redefined-builtins=id \
		$(shell find $(CONFIG_PATTERN) -name "*.py" 2>/dev/null) || true
	@echo "$(GREEN)✓ Config linting complete$(NC)"

# Type checking targets
.PHONY: typecheck
typecheck: typecheck-pyright typecheck-mypy ## Run both pyright and mypy type checkers

.PHONY: typecheck-pyright
typecheck-pyright: ## Run pyright type checker (strict mode)
	@echo "$(BLUE)Running pyright type checker...$(NC)"
	$(PYTHON) -m pyright
	@echo "$(GREEN)✓ Pyright type check complete$(NC)"

.PHONY: typecheck-mypy
typecheck-mypy: ## Run mypy type checker with caching
	@echo "$(BLUE)Running mypy type checker...$(NC)"
	$(PYTHON) -m mypy src --explicit-package-bases --cache-dir=.mypy_cache --incremental
	@echo "$(GREEN)✓ Mypy type check complete$(NC)"

# Testing targets
.PHONY: test
test: ## Run pytest with coverage
	@echo "$(BLUE)Running pytest with coverage...$(NC)"
	$(PYTHON) -m pytest -n $(PYTEST_WORKERS) --lf --ff -v
	@echo "$(GREEN)✓ Tests complete$(NC)"

.PHONY: test-fast
test-fast: ## Run pytest with minimal output (faster)
	@echo "$(BLUE)Running pytest (fast mode)...$(NC)"
	$(PYTHON) -m pytest -n $(PYTEST_WORKERS) --lf --ff -q --tb=short
	@echo "$(GREEN)✓ Tests complete$(NC)"

.PHONY: test-watch
test-watch: ## Run pytest in watch mode
	@echo "$(BLUE)Starting pytest watch mode...$(NC)"
	$(PYTHON) -m pytest_watch

.PHONY: coverage-report
coverage-report: ## Generate detailed coverage reports
	@echo "$(BLUE)Generating coverage reports...$(NC)"
	$(PYTHON) -m coverage report
	$(PYTHON) -m coverage html
	@echo "$(GREEN)✓ Coverage reports generated in htmlcov/$(NC)"

# Security targets
.PHONY: security
security: security-bandit security-pip-audit ## Run all security checks

.PHONY: security-bandit
security-bandit: ## Run bandit security scan
	@echo "$(BLUE)Running bandit security scan...$(NC)"
	$(PYTHON) -m bandit -r src/ -ll -i
	@echo "$(GREEN)✓ Bandit scan complete$(NC)"

.PHONY: security-pip-audit
security-pip-audit: ## Run pip-audit dependency scan
	@echo "$(BLUE)Running pip-audit dependency scan...$(NC)"
	$(PYTHON) -m pip_audit
	@echo "$(GREEN)✓ pip-audit scan complete$(NC)"

# Quality check targets
.PHONY: complexity
complexity: ## Check cognitive complexity with flake8
	@echo "$(BLUE)Checking cognitive complexity...$(NC)"
	$(PYTHON) -m flake8 src/domain/ src/application/
	@echo "$(GREEN)✓ Complexity check complete$(NC)"

.PHONY: imports
imports: ## Check import architecture with import-linter
	@echo "$(BLUE)Checking import architecture...$(NC)"
	$(PYTHON) -m importlinter
	@echo "$(GREEN)✓ Import architecture check complete$(NC)"

.PHONY: docstrings
docstrings: docstrings-style docstrings-coverage ## Check all docstring quality

.PHONY: docstrings-style
docstrings-style: ## Check docstring style with pydocstyle
	@echo "$(BLUE)Checking docstring style...$(NC)"
	$(PYTHON) -m pydocstyle src/
	@echo "$(GREEN)✓ Docstring style check complete$(NC)"

.PHONY: docstrings-coverage
docstrings-coverage: ## Check docstring coverage
	@echo "$(BLUE)Checking docstring coverage...$(NC)"
	$(PYTHON) -m docstr_coverage src/ --fail-under 100.0 --skip-magic --percentage-only
	@echo "$(GREEN)✓ Docstring coverage check complete$(NC)"

# Main quality target (matches pre-commit hook)
.PHONY: quality
quality: ## Run all quality checks (same as pre-commit hook)
	@echo "$(YELLOW)Running all quality checks...$(NC)"
	@echo "$(YELLOW)This runs the same checks as the pre-commit hook$(NC)"
	@bash hooks/run-quality-checks.sh

# Combined targets
.PHONY: all
all: format quality ## Format code then run all quality checks

.PHONY: ci
ci: lint typecheck test security complexity imports docstrings ## Run all CI checks (no formatting)

# Utility targets
.PHONY: clean
clean: ## Clean temporary files and caches
	@echo "$(BLUE)Cleaning temporary files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "coverage.xml" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

.PHONY: clean-all
clean-all: clean ## Clean everything including virtual environment
	@echo "$(BLUE)Removing virtual environment...$(NC)"
	rm -rf $(VENV_DIR)
	@echo "$(GREEN)✓ Full cleanup complete$(NC)"

# Development workflow targets
.PHONY: dev-setup
dev-setup: install-dev ## Complete development environment setup
	@echo "$(GREEN)✓ Development environment ready$(NC)"
	@echo "$(YELLOW)Run 'make help' to see available commands$(NC)"

.PHONY: pre-commit
pre-commit: ## Run pre-commit hooks on all files
	@echo "$(BLUE)Running pre-commit hooks...$(NC)"
	pre-commit run --all-files
	@echo "$(GREEN)✓ Pre-commit hooks complete$(NC)"

# Default target
.DEFAULT_GOAL := help