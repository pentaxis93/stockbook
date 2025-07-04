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

# Coverage thresholds
MIN_COVERAGE := 100

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
format: ## Format code with black and fix imports with ruff (includes unsafe fixes)
	@echo "$(BLUE)Running ruff import sorting and fixes (with unsafe fixes)...$(NC)"
	$(PYTHON) -m ruff check --fix --unsafe-fixes .
	@echo "$(BLUE)Running black formatter...$(NC)"
	$(PYTHON) -m black .
	@echo "$(GREEN)✓ Code formatted$(NC)"

# Linting targets
.PHONY: lint
lint: ## Run ruff linter on all code
	@echo "$(BLUE)Running ruff linter...$(NC)"
	$(PYTHON) -m ruff check .
	@echo "$(GREEN)✓ Linting complete$(NC)"

.PHONY: lint-fix
lint-fix: ## Run ruff linter with automatic fixes (includes unsafe fixes)
	@echo "$(BLUE)Running ruff linter with fixes (including unsafe)...$(NC)"
	$(PYTHON) -m ruff check --fix --unsafe-fixes .
	@echo "$(GREEN)✓ Linting and fixes complete$(NC)"

.PHONY: lint-fix-safe
lint-fix-safe: ## Run ruff linter with safe fixes only
	@echo "$(BLUE)Running ruff linter with safe fixes only...$(NC)"
	$(PYTHON) -m ruff check --fix .
	@echo "$(GREEN)✓ Linting and safe fixes complete$(NC)"

# Legacy layer-specific targets (now all use ruff)
.PHONY: lint-production
lint-production: lint ## Alias for lint (ruff handles all layers)

.PHONY: lint-domain
lint-domain: ## Lint domain layer (using ruff)
	@echo "$(BLUE)Linting domain layer...$(NC)"
	$(PYTHON) -m ruff check $(SRC_DIR)/domain
	@echo "$(GREEN)✓ Domain layer linting complete$(NC)"

.PHONY: lint-application
lint-application: ## Lint application layer (using ruff)
	@echo "$(BLUE)Linting application layer...$(NC)"
	$(PYTHON) -m ruff check $(SRC_DIR)/application
	@echo "$(GREEN)✓ Application layer linting complete$(NC)"

.PHONY: lint-infrastructure
lint-infrastructure: ## Lint infrastructure layer (using ruff)
	@echo "$(BLUE)Linting infrastructure layer...$(NC)"
	$(PYTHON) -m ruff check $(SRC_DIR)/infrastructure
	@echo "$(GREEN)✓ Infrastructure layer linting complete$(NC)"

.PHONY: lint-presentation
lint-presentation: ## Lint presentation layer (using ruff)
	@echo "$(BLUE)Linting presentation layer...$(NC)"
	$(PYTHON) -m ruff check $(SRC_DIR)/presentation
	@echo "$(GREEN)✓ Presentation layer linting complete$(NC)"

.PHONY: lint-di
lint-di: ## Lint dependency injection (using ruff)
	@echo "$(BLUE)Linting dependency injection...$(NC)"
	$(PYTHON) -m ruff check dependency_injection hooks
	@echo "$(GREEN)✓ Dependency injection linting complete$(NC)"

.PHONY: lint-tests
lint-tests: ## Run ruff on test files
	@echo "$(BLUE)Linting test files...$(NC)"
	$(PYTHON) -m ruff check $(TEST_DIR)
	@echo "$(GREEN)✓ Test linting complete$(NC)"

# Type checking targets
.PHONY: typecheck
typecheck: ## Run pyright type checker (strict mode)
	@echo "$(BLUE)Running pyright type checker...$(NC)"
	$(PYTHON) -m pyright
	@echo "$(GREEN)✓ Type check complete$(NC)"

# Testing targets
.PHONY: test
test: ## Run pytest with coverage
	@echo "$(BLUE)Running pytest with coverage...$(NC)"
	$(PYTHON) -m pytest -n $(PYTEST_WORKERS) --lf --ff -v --cov-fail-under=$(MIN_COVERAGE)
	@echo "$(GREEN)✓ Tests complete$(NC)"

.PHONY: test-fast
test-fast: ## Run pytest with minimal output (faster)
	@echo "$(BLUE)Running pytest (fast mode)...$(NC)"
	$(PYTHON) -m pytest -n $(PYTEST_WORKERS) --lf --ff -q --tb=short --cov-fail-under=$(MIN_COVERAGE)
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
security: security-ruff security-pip-audit ## Run all security checks

.PHONY: security-ruff
security-ruff: ## Run ruff security checks (replaces bandit)
	@echo "$(BLUE)Running ruff security scan...$(NC)"
	$(PYTHON) -m ruff check --select S src/
	@echo "$(GREEN)✓ Security scan complete$(NC)"

.PHONY: security-pip-audit
security-pip-audit: ## Run pip-audit dependency scan
	@echo "$(BLUE)Running pip-audit dependency scan...$(NC)"
	$(PYTHON) -m pip_audit
	@echo "$(GREEN)✓ pip-audit scan complete$(NC)"

# Quality check targets
.PHONY: complexity
complexity: ## Check complexity with ruff (replaces flake8)
	@echo "$(BLUE)Checking code complexity...$(NC)"
	$(PYTHON) -m ruff check --select C901 src/
	@echo "$(GREEN)✓ Complexity check complete$(NC)"

.PHONY: imports
imports: ## Check import architecture with import-linter
	@echo "$(BLUE)Checking import architecture...$(NC)"
	lint-imports
	@echo "$(GREEN)✓ Import architecture check complete$(NC)"

.PHONY: docstrings
docstrings: docstrings-style docstrings-coverage ## Check all docstring quality

.PHONY: docstrings-style
docstrings-style: ## Check docstring style with ruff (replaces pydocstyle)
	@echo "$(BLUE)Checking docstring style...$(NC)"
	$(PYTHON) -m ruff check src/
	@echo "$(GREEN)✓ Docstring style check complete$(NC)"

.PHONY: docstrings-coverage
docstrings-coverage: ## Check docstring coverage
	@echo "$(BLUE)Checking docstring coverage...$(NC)"
	docstr-coverage src/ --fail-under 100.0 --skip-magic --percentage-only
	@echo "$(GREEN)✓ Docstring coverage check complete$(NC)"

# Main quality target (matches pre-commit hook)
.PHONY: quality
quality: quality-parallel ## Run all quality checks including tests and coverage (same as pre-commit hook)

# Parallel quality checks target for maximum performance
.PHONY: quality-parallel
quality-parallel: ## Run all quality checks in parallel for faster execution
	@echo "$(YELLOW)Running all quality checks in parallel...$(NC)"
	@echo "$(BLUE)Starting parallel execution of quality checks...$(NC)"
	@rm -f .quality-*.status 2>/dev/null || true
	@failed=0; \
	( $(MAKE) -s lint || echo $$? > .quality-lint.status ) 2>&1 | sed 's/^/[LINT] /' & \
	( $(MAKE) -s typecheck || echo $$? > .quality-typecheck.status ) 2>&1 | sed 's/^/[TYPECHECK] /' & \
	( $(MAKE) -s test-fast || echo $$? > .quality-pytest.status ) 2>&1 | sed 's/^/[PYTEST] /' & \
	( $(MAKE) -s complexity || echo $$? > .quality-complexity.status ) 2>&1 | sed 's/^/[COMPLEXITY] /' & \
	( $(MAKE) -s imports || echo $$? > .quality-imports.status ) 2>&1 | sed 's/^/[IMPORTS] /' & \
	( $(MAKE) -s docstrings-style || echo $$? > .quality-docstyle.status ) 2>&1 | sed 's/^/[DOCSTYLE] /' & \
	( $(MAKE) -s docstrings-coverage || echo $$? > .quality-doccov.status ) 2>&1 | sed 's/^/[DOCCOV] /' & \
	( $(MAKE) -s security-ruff || echo $$? > .quality-security.status ) 2>&1 | sed 's/^/[SECURITY] /' & \
	( $(MAKE) -s security-pip-audit || echo $$? > .quality-pip-audit.status ) 2>&1 | sed 's/^/[PIP-AUDIT] /' & \
	wait; \
	for status_file in .quality-*.status; do \
		if [ -f "$$status_file" ]; then \
			failed=1; \
			break; \
		fi; \
	done; \
	rm -f .quality-*.status 2>/dev/null || true; \
	if [ $$failed -eq 1 ]; then \
		echo "$(RED)❌ One or more quality checks failed$(NC)"; \
		exit 1; \
	else \
		echo "$(GREEN)✅ All quality checks passed!$(NC)"; \
	fi

# Combined targets
.PHONY: all
all: format quality ## Format code then run all quality checks

.PHONY: check
check: quality ## Alias for quality - runs all quality checks, tests, and coverage

.PHONY: validate
validate: quality ## Alias for quality - runs all quality checks, tests, and coverage

.PHONY: ci
ci: lint typecheck test security-ruff security-pip-audit complexity imports docstrings ## Run all CI checks (no formatting)

# Utility targets
.PHONY: clean
clean: ## Clean temporary files and caches
	@echo "$(BLUE)Cleaning temporary files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
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