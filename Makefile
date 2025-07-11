# StockBook Makefile - Build, test, and maintain the project

# Python interpreter and package manager
PYTHON := python3
PIP := pip

# Colors for output
GREEN := \033[0;32m
RED := \033[0;31m
BLUE := \033[0;34m
YELLOW := \033[1;33m
NC := \033[0m # No Color

# Default target: run tests and quality checks
.PHONY: all
all: test ## Default target: run all tests and quality checks

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

.PHONY: test
test: ## Run all tests, quality checks, and coverage (blocks on any failure)
	@echo "$(BLUE)Running all tests and quality checks...$(NC)"
	$(PYTHON) scripts/test_all.py

.PHONY: run
run: ## Run the development server with auto-reload
	@echo "$(BLUE)Starting development server...$(NC)"
	uvicorn src.presentation.web.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: docs-arch
docs-arch: ## Generate architecture diagrams from code
	@echo "$(BLUE)Generating architecture diagrams...$(NC)"
	@$(PYTHON) docs/architecture/models/generate_all.py
	@echo "$(GREEN)✓ Architecture diagrams generated$(NC)"
	@echo "View diagrams at: file://$(PWD)/docs/architecture/diagrams/viewer.html"

.PHONY: clean
clean: ## Remove generated files and caches
	@echo "$(BLUE)Cleaning up generated files...$(NC)"
	# Python bytecode and caches
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	# Build artifacts
	rm -rf build/ dist/ 2>/dev/null || true
	# Test and coverage reports
	rm -rf .pytest_cache/ htmlcov/ 2>/dev/null || true
	rm -rf .mypy_cache/ .ruff_cache/ 2>/dev/null || true
	# IDE and editor files
	find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	find . -type f -name "*~" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"