# Use Pre-commit Hooks for Quality Enforcement

* Status: accepted
* Deciders: Development team
* Date: 2025-01-11

## Context and Problem Statement

StockBook requires consistent code quality, formatting, and test coverage across the codebase. With multiple developers contributing and our commitment to Test-Driven Development with strict coverage requirements, we need an automated way to enforce quality standards before code enters the repository. How can we ensure that all code meets our quality standards without relying on manual reviews or CI/CD pipeline failures?

## Decision Drivers

* **Early Feedback**: Catch issues before code is committed
* **Consistency**: Enforce the same standards for all developers
* **Developer Experience**: Fast feedback loop during development
* **Coverage Requirements**: Enforce layer-specific test coverage
* **Automation**: Reduce manual review burden
* **Local Verification**: Validate locally before pushing
* **Tool Integration**: Work with our existing Python toolchain

## Considered Options

* **Pre-commit Hooks**: Git hooks that run before each commit
* **CI-Only Validation**: Run all checks only in CI/CD pipeline
* **IDE Integration**: Rely on IDE plugins and configurations
* **Manual Code Reviews**: Human verification only
* **Commit-msg Hooks**: Validate after commit but before push
* **Custom Scripts**: Manual scripts developers run before committing

## Decision Outcome

Chosen option: "Pre-commit Hooks", because they provide immediate feedback at the optimal time - before code enters version control. This approach ensures consistency across all developers while maintaining a fast feedback loop. Pre-commit hooks integrate seamlessly with our Python toolchain and can enforce our layer-specific coverage requirements automatically.

### Positive Consequences

* **Immediate Feedback**: Issues caught before commit
* **Consistency**: Same rules for everyone
* **Time Savings**: No waiting for CI to find issues
* **Reduced Review Burden**: Automated checks free reviewers to focus on logic
* **Better Git History**: No commits that fail basic checks
* **Developer Learning**: Immediate feedback helps developers learn standards
* **Local Verification**: Can verify without internet/CI access

### Negative Consequences

* **Initial Setup**: Each developer must install pre-commit
* **Commit Time**: Hooks add time to commit process
* **Bypass Temptation**: Developers might use --no-verify
* **Tool Dependencies**: Requires local tool installation

## Pros and Cons of the Options

### Pre-commit Hooks

Git hooks that run automated checks before allowing commit.

* Good, because catches issues at the earliest point
* Good, because consistent across all developers
* Good, because integrates with existing tools
* Good, because customizable per project
* Good, because can enforce complex rules
* Good, because supports partial commits
* Bad, because requires local setup
* Bad, because can be bypassed

### CI-Only Validation

Run all quality checks only in continuous integration.

* Good, because centralized configuration
* Good, because can't be bypassed
* Good, because no local setup needed
* Bad, because slow feedback loop
* Bad, because wastes CI resources
* Bad, because clutters git history
* Bad, because frustrating for developers

### IDE Integration

Rely on IDE plugins and real-time checking.

* Good, because real-time feedback
* Good, because no commit delays
* Good, because great developer experience
* Bad, because IDE-specific setup
* Bad, because inconsistent across IDEs
* Bad, because easy to ignore warnings
* Bad, because not enforced

### Manual Code Reviews

Depend entirely on human reviewers.

* Good, because flexible judgment
* Good, because catches logic issues
* Bad, because inconsistent standards
* Bad, because time-consuming
* Bad, because human error
* Bad, because reviewer fatigue
* Bad, because delays merges

### Commit-msg Hooks

Validate after commit but before push.

* Good, because allows local commits
* Good, because batch validation
* Bad, because later in process
* Bad, because complex to revert
* Bad, because confusing workflow
* Bad, because still clutters local history

### Custom Scripts

Manual scripts developers run before committing.

* Good, because full control
* Good, because can be comprehensive
* Bad, because easy to forget
* Bad, because no enforcement
* Bad, because inconsistent usage
* Bad, because poor developer experience

## Implementation Details

Our pre-commit hooks implementation:

### Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
default_stages: [commit]
default_language_version:
  python: python3.11

repos:
  # Code Formatting
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11
        args: ["--line-length=88"]

  # Import Sorting
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile=black", "--line-length=88"]

  # Linting
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: ["--fix", "--exit-non-zero-on-fix"]

  # Type Checking
  - repo: https://github.com/RobertCraigie/pyright-python
    rev: v1.1.340
    hooks:
      - id: pyright
        additional_dependencies: ["pyright@1.1.340"]
        args: ["--warnings"]

  # Security Scanning
  - repo: https://github.com/pycqa/bandit
    rev: 1.7.6
    hooks:
      - id: bandit
        args: ["-r", "src", "-ll"]
        exclude: "tests/"

  # Custom Hooks
  - repo: local
    hooks:
      # Layer-specific test coverage
      - id: domain-coverage
        name: Check domain layer coverage (100%)
        entry: bash -c 'pytest tests/domain --cov=src/domain --cov-fail-under=100 --cov-report=term-missing:skip-covered'
        language: system
        pass_filenames: false
        always_run: true
        stages: [commit]

      - id: application-coverage
        name: Check application layer coverage (90%)
        entry: bash -c 'pytest tests/application --cov=src/application --cov-fail-under=90 --cov-report=term-missing:skip-covered'
        language: system
        pass_filenames: false
        always_run: true
        stages: [commit]

      - id: no-commit-to-main
        name: Prevent commits to main branch
        entry: bash -c 'if [ "$(git rev-parse --abbrev-ref HEAD)" = "main" ]; then echo "Direct commits to main branch are not allowed"; exit 1; fi'
        language: system
        pass_filenames: false
        always_run: true

      - id: no-debug-code
        name: Check for debug code
        entry: bash -c 'grep -r "import pdb\|pdb.set_trace\|breakpoint()" src/ && echo "Debug code found!" && exit 1 || exit 0'
        language: system
        pass_filenames: false

      - id: todo-format
        name: Check TODO format
        entry: bash -c 'grep -r "TODO\|FIXME" src/ | grep -v "TODO(.*):.*" && echo "TODOs must include attribution: TODO(username): description" && exit 1 || exit 0'
        language: system
        pass_filenames: false
```

### Installation and Setup

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install

# Run against all files (initial setup)
pre-commit run --all-files

# Update hooks to latest versions
pre-commit autoupdate
```

### Developer Workflow Integration

```python
# Makefile integration
.PHONY: install-dev
install-dev:
	pip install -e ".[dev]"
	pre-commit install
	@echo "Pre-commit hooks installed!"

.PHONY: test
test:
	# Run the same checks as pre-commit
	black --check src tests
	isort --check-only src tests
	ruff check src tests
	pyright src
	pytest tests/domain --cov=src/domain --cov-fail-under=100
	pytest tests/application --cov=src/application --cov-fail-under=90

.PHONY: fix
fix:
	# Auto-fix what can be fixed
	black src tests
	isort src tests
	ruff check --fix src tests
```

### Custom Hook Examples

```yaml
# Check for proper type annotations
- id: type-completeness
  name: Check type completeness
  entry: python scripts/check_type_completeness.py
  language: python
  files: \.py$
  exclude: ^tests/

# Validate architecture dependencies
- id: architecture-check
  name: Validate architecture dependencies
  entry: python scripts/check_architecture.py
  language: python
  pass_filenames: false
  always_run: true
```

### Architecture Dependency Checker

```python
# scripts/check_architecture.py
import ast
import sys
from pathlib import Path

class ArchitectureChecker(ast.NodeVisitor):
    """Verify architectural dependencies."""
    
    LAYER_RULES = {
        "domain": [],  # No dependencies
        "application": ["domain"],
        "infrastructure": ["domain", "application"],
        "presentation": ["application", "domain"],
    }
    
    def check_imports(self, file_path: Path) -> list[str]:
        """Check if file imports follow architecture rules."""
        layer = self._get_layer(file_path)
        if not layer:
            return []
        
        violations = []
        tree = ast.parse(file_path.read_text())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                imported_layer = self._get_layer_from_import(node.module)
                if imported_layer and imported_layer not in self.LAYER_RULES[layer]:
                    violations.append(
                        f"{file_path}: {layer} layer cannot import from {imported_layer}"
                    )
        
        return violations

if __name__ == "__main__":
    checker = ArchitectureChecker()
    violations = []
    
    for py_file in Path("src").rglob("*.py"):
        violations.extend(checker.check_imports(py_file))
    
    if violations:
        print("Architecture violations found:")
        for v in violations:
            print(f"  - {v}")
        sys.exit(1)
```

### Commit Message Hook

```yaml
# Enforce conventional commits
- repo: https://github.com/compilerla/conventional-pre-commit
  rev: v3.0.0
  hooks:
    - id: conventional-pre-commit
      stages: [commit-msg]
      args: ["--strict", "--force-scope"]
```

### CI/CD Integration

```yaml
# .github/workflows/quality.yml
name: Quality Checks

on: [push, pull_request]

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Run pre-commit
        run: |
          pip install pre-commit
          pre-commit run --all-files
```

### Developer Documentation

```markdown
# Development Setup

1. Install pre-commit hooks:
   ```bash
   make install-dev
   ```

2. Run checks manually:
   ```bash
   pre-commit run --all-files
   ```

3. Skip hooks in emergency (use sparingly):
   ```bash
   git commit --no-verify -m "Emergency fix"
   ```

## Hook Descriptions

- **black**: Formats Python code
- **isort**: Sorts imports
- **ruff**: Fast Python linter
- **pyright**: Type checker
- **bandit**: Security linter
- **domain-coverage**: Ensures 100% test coverage for domain layer
- **application-coverage**: Ensures 90% test coverage for application layer
```

## Links

* Supports [ADR-0005: Mandate Test-Driven Development](0005-mandate-test-driven-development.md)
* Enforces [ADR-0002: Use Clean Architecture](0002-use-clean-architecture.md)
* Complements [ADR-0006: Python FastAPI SQLAlchemy Stack](0006-python-fastapi-sqlalchemy-stack.md)
* References: pre-commit documentation (https://pre-commit.com)
* References: "Continuous Integration" by Paul Duvall