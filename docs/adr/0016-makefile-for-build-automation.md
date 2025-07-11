# Use Makefile for Build Automation

* Status: accepted
* Deciders: Development team
* Date: 2025-01-11

## Context and Problem Statement

StockBook requires a consistent way to run common development tasks like testing, linting, building, and deployment. Developers need a simple interface to execute complex command sequences without memorizing long commands or maintaining separate scripts. We need a build automation tool that is universally available, simple to use, and provides a clear overview of available tasks. Which build automation tool should we use for our Python project?

## Decision Drivers

* **Simplicity**: Easy to understand and use
* **Universality**: Available on all development platforms
* **No Dependencies**: Should work without additional installations
* **Self-Documenting**: Easy to see available commands
* **Composability**: Commands can build on each other
* **IDE Integration**: Works well with developer tools
* **Speed**: Minimal overhead for task execution

## Considered Options

* **GNU Make**: Traditional build automation with Makefiles
* **Python Scripts**: Custom Python scripts for automation
* **Poetry Scripts**: Use Poetry's script feature
* **Just**: Modern command runner inspired by Make
* **Task**: YAML-based task runner
* **Invoke**: Python-based task execution

## Decision Outcome

Chosen option: "GNU Make", because it is universally available on Unix-like systems, requires no additional dependencies, and provides a simple, well-understood interface for task automation. While originally designed for C/C++ compilation, Make works excellently for Python projects as a task runner and provides clear documentation of available commands through `make help`.

### Positive Consequences

* **Universal Availability**: Pre-installed on Linux/macOS
* **Simple Syntax**: Easy to read and write targets
* **Self-Documenting**: `make help` shows all commands
* **Composable**: Targets can depend on other targets
* **Fast Execution**: No runtime overhead
* **IDE Support**: Excellent integration with most IDEs
* **Standard Tool**: Familiar to most developers

### Negative Consequences

* **Windows Support**: Requires WSL or Git Bash on Windows
* **Limited Features**: Not as powerful as modern task runners
* **Syntax Quirks**: Tab sensitivity and shell differences
* **Not Python-Native**: Separate syntax to learn

## Pros and Cons of the Options

### GNU Make

Traditional build tool using Makefiles.

* Good, because universally available
* Good, because no dependencies
* Good, because fast execution
* Good, because self-documenting with help
* Good, because composable targets
* Good, because IDE integration
* Bad, because Windows needs WSL
* Bad, because tab-sensitive syntax

### Python Scripts

Custom Python scripts in a scripts/ directory.

* Good, because pure Python
* Good, because full programming power
* Good, because cross-platform
* Bad, because no standard structure
* Bad, because harder to discover commands
* Bad, because more verbose
* Bad, because no built-in help
* Bad, because no dependency management

### Poetry Scripts

Use Poetry's built-in script feature.

* Good, because integrated with Poetry
* Good, because Python-native
* Good, because cross-platform
* Bad, because limited functionality
* Bad, because Poetry-specific
* Bad, because no complex workflows
* Bad, because poor discoverability

### Just

Modern command runner inspired by Make.

* Good, because better syntax than Make
* Good, because cross-platform
* Good, because designed for commands
* Bad, because requires installation
* Bad, because less familiar
* Bad, because smaller community
* Bad, because another tool to learn

### Task

YAML-based task runner.

* Good, because readable YAML syntax
* Good, because cross-platform
* Good, because good features
* Bad, because requires installation
* Bad, because YAML complexity
* Bad, because less standard
* Bad, because slower than Make

### Invoke

Python-based task execution library.

* Good, because Python-native
* Good, because powerful features
* Good, because good documentation
* Bad, because requires installation
* Bad, because more complex setup
* Bad, because Python overhead
* Bad, because less discoverable

## Implementation Details

Our Makefile implementation:

### Core Makefile Structure

```makefile
# Makefile
.PHONY: help
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Variables
PYTHON := python3.11
VENV := .venv
PYTEST := $(VENV)/bin/pytest
PRE_COMMIT := $(VENV)/bin/pre-commit

# Default target
.DEFAULT_GOAL := help

##@ Development Setup

.PHONY: install
install: ## Install all dependencies
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install poetry
	poetry install

.PHONY: install-dev
install-dev: install ## Install with development dependencies
	poetry install --with dev
	$(PRE_COMMIT) install
	@echo "✅ Development environment ready!"

##@ Code Quality

.PHONY: format
format: ## Format code with black and isort
	poetry run black src tests
	poetry run isort src tests

.PHONY: lint
lint: ## Run all linters
	poetry run ruff check src tests
	poetry run black --check src tests
	poetry run isort --check-only src tests
	poetry run pyright src

.PHONY: security
security: ## Run security checks
	poetry run bandit -r src -ll
	poetry run safety check

##@ Testing

.PHONY: test
test: ## Run all tests with coverage
	$(PYTEST) tests/ \
		--cov=src \
		--cov-report=term-missing:skip-covered \
		--cov-report=html \
		--cov-report=xml

.PHONY: test-unit
test-unit: ## Run unit tests only
	$(PYTEST) tests/unit -v

.PHONY: test-integration
test-integration: ## Run integration tests
	$(PYTEST) tests/integration -v

.PHONY: test-domain
test-domain: ## Run domain tests with 100% coverage requirement
	$(PYTEST) tests/domain \
		--cov=src/domain \
		--cov-fail-under=100 \
		--cov-report=term-missing

.PHONY: test-application
test-application: ## Run application tests with 90% coverage requirement
	$(PYTEST) tests/application \
		--cov=src/application \
		--cov-fail-under=90 \
		--cov-report=term-missing

##@ Build & Run

.PHONY: build
build: ## Build the application
	poetry build

.PHONY: run
run: ## Run the application
	poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: docker-build
docker-build: ## Build Docker image
	docker build -t stockbook:latest .

.PHONY: docker-run
docker-run: ## Run Docker container
	docker run -p 8000:8000 -e DATABASE_URL stockbook:latest

##@ Database

.PHONY: db-upgrade
db-upgrade: ## Apply database migrations
	poetry run alembic upgrade head

.PHONY: db-downgrade
db-downgrade: ## Rollback last migration
	poetry run alembic downgrade -1

.PHONY: db-migration
db-migration: ## Create new migration
	@read -p "Migration name: " name; \
	poetry run alembic revision --autogenerate -m "$$name"

##@ Documentation

.PHONY: docs
docs: ## Generate documentation
	poetry run mkdocs build

.PHONY: docs-serve
docs-serve: ## Serve documentation locally
	poetry run mkdocs serve

##@ Utility

.PHONY: clean
clean: ## Clean build artifacts
	find . -type d -name "__pycache__" -rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov coverage.xml .pytest_cache
	rm -rf dist build *.egg-info

.PHONY: requirements
requirements: ## Export requirements files
	poetry export -f requirements.txt --output requirements.txt --without-hashes
	poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes

##@ Quality Assurance

.PHONY: qa
qa: lint test security ## Run all quality checks

.PHONY: pre-commit
pre-commit: ## Run pre-commit hooks
	$(PRE_COMMIT) run --all-files

##@ Release

.PHONY: version
version: ## Show current version
	@poetry version

.PHONY: bump-patch
bump-patch: ## Bump patch version
	poetry version patch
	@echo "New version: $$(poetry version)"

.PHONY: bump-minor
bump-minor: ## Bump minor version
	poetry version minor
	@echo "New version: $$(poetry version)"

.PHONY: bump-major
bump-major: ## Bump major version
	poetry version major
	@echo "New version: $$(poetry version)"
```

### Advanced Patterns

```makefile
# Complex dependencies
.PHONY: ci
ci: clean lint test-domain test-application build ## Run full CI pipeline
	@echo "✅ CI pipeline passed!"

# Conditional execution
ifdef CI
	PYTEST_ARGS := --no-cov-on-fail --maxfail=1
else
	PYTEST_ARGS := -v
endif

# Environment-specific targets
.PHONY: dev
dev: ## Start development environment
	docker-compose -f docker-compose.dev.yml up

.PHONY: prod
prod: ## Deploy to production
	@echo "Deploying to production..."
	./scripts/deploy.sh production

# Watch mode
.PHONY: watch-test
watch-test: ## Run tests in watch mode
	$(PYTEST) tests/ --watch

# Parallel execution
.PHONY: test-parallel
test-parallel: ## Run tests in parallel
	$(PYTEST) tests/ -n auto
```

### Integration with CI/CD

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: make install-dev
      
      - name: Run quality checks
        run: make qa
      
      - name: Build application
        run: make build
```

### Developer Experience

```makefile
# Helpful shortcuts
.PHONY: t
t: test ## Shortcut for test

.PHONY: f
f: format ## Shortcut for format

.PHONY: l
l: lint ## Shortcut for lint

# Interactive commands
.PHONY: shell
shell: ## Start Python shell with app context
	poetry run python -i -c "from src.main import *"

.PHONY: db-shell
db-shell: ## Start database shell
	docker-compose exec db psql -U postgres stockbook

# Development helpers
.PHONY: todo
todo: ## Show all TODOs in codebase
	@grep -r "TODO\|FIXME" src/ tests/ || echo "No TODOs found!"

.PHONY: coverage-report
coverage-report: ## Open coverage report in browser
	open htmlcov/index.html || xdg-open htmlcov/index.html
```

### Error Handling

```makefile
# Check prerequisites
.PHONY: check-poetry
check-poetry:
	@which poetry > /dev/null || (echo "Poetry not installed. Run: pip install poetry" && exit 1)

.PHONY: check-docker
check-docker:
	@which docker > /dev/null || (echo "Docker not installed." && exit 1)

# Target with prerequisites
install: check-poetry

docker-build: check-docker
```

## Links

* Supports [ADR-0005: Mandate Test-Driven Development](0005-mandate-test-driven-development.md)
* Complements [ADR-0015: Pre-commit Hooks](0015-pre-commit-hooks-for-quality-enforcement.md)
* Works with [ADR-0006: Python FastAPI SQLAlchemy Stack](0006-python-fastapi-sqlalchemy-stack.md)
* References: GNU Make documentation
* References: "Managing Projects with GNU Make" by Robert Mecklenburg