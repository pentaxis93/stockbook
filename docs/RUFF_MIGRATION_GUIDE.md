# Ruff Migration Guide

## Overview

We have successfully migrated from multiple linting tools (flake8, pylint, pydocstyle, bandit, isort) to Ruff, a fast and comprehensive linter written in Rust. This guide documents the migration process and any differences developers should be aware of.

## What Changed

### Tools Replaced
- **flake8** → Ruff (E, W, F codes)
- **pylint** → Ruff (PLC, PLE, PLR, PLW codes)
- **isort** → Ruff (I codes)
- **pydocstyle** → Ruff (D codes)
- **bandit** → Ruff (S codes)
- **flake8-cognitive-complexity** → Ruff (C901 for McCabe complexity)

### Tools Kept
- **black** - Still used for code formatting (Ruff doesn't replace formatters)
- **pytest** - Still used for testing
- **mypy** - Still used for type checking
- **pyright** - Still used for strict type checking
- **import-linter** - Still used for architecture validation
- **docstr-coverage** - Still used for docstring coverage metrics

## Configuration

All Ruff configuration is now in `pyproject.toml` under `[tool.ruff]` sections:
- `[tool.ruff]` - General settings
- `[tool.ruff.lint]` - Linting rules selection and ignores
- `[tool.ruff.lint.pylint]` - Pylint-compatible settings
- `[tool.ruff.lint.mccabe]` - Complexity settings
- `[tool.ruff.lint.pydocstyle]` - Docstring style
- `[tool.ruff.lint.isort]` - Import sorting
- `[tool.ruff.lint.per-file-ignores]` - Layer-specific rules

## Key Differences

### 1. Rule Code Changes
Some rules have different codes in Ruff:
- Cognitive complexity → Not directly supported (use C901 McCabe complexity)
- `too-many-instance-attributes` → Not available in Ruff
- `too-few-public-methods` → Not available in Ruff
- `unnecessary-pass` → PIE790 (currently ignored)
- `protected-access` → Not a specific rule in Ruff

### 2. Import Sorting
- Ruff's isort implementation doesn't use "profile" setting
- Configure individual settings instead of using `profile = "black"`
- Import fixes are included with `ruff check --fix`

### 3. Security Checks
- Bandit's security checks are available as S-prefixed rules
- Some security rules like S101 (assert-used) are ignored in tests
- Use `ruff check --select S` to run only security checks

### 4. Performance
- Ruff is approximately 1000x faster than pylint
- Quality checks that took minutes now complete in seconds
- Pre-commit hooks run much faster

## Auto-Fix Configuration

Ruff is configured to apply both safe and unsafe fixes automatically:

1. **In Configuration** (`pyproject.toml`):
   ```toml
   [tool.ruff]
   unsafe-fixes = true  # Enables unsafe fixes
   ```

2. **In Pre-commit Hooks**: Auto-fixes (including unsafe) are applied on every commit
3. **In Makefile**: Multiple targets for different fix levels

## Common Commands

### Basic Linting
```bash
# Run all checks
make lint
# or
python -m ruff check .

# Run with automatic fixes (includes unsafe fixes)
make lint-fix
# or
python -m ruff check --fix --unsafe-fixes .

# Run with safe fixes only
make lint-fix-safe
# or
python -m ruff check --fix .

# Format code (includes Ruff fixes + Black formatting)
make format

# Check specific directory
python -m ruff check src/domain/
```

### Specific Checks
```bash
# Security checks only
make security-ruff
# or
python -m ruff check --select S src/

# Complexity checks only
make complexity
# or
python -m ruff check --select C901 src/

# Docstring checks only
make docstrings-style
# or
python -m ruff check --select D src/
```

### Formatting Workflow
```bash
# Format and fix imports
make format
# This runs:
# 1. ruff check --fix (fixes imports and other issues)
# 2. black . (formats code)
```

## Handling New Issues

When running Ruff for the first time, you may see new issues that weren't caught before:

1. **UP006/UP007/UP035** - Python version upgrade suggestions
   - These suggest modern Python syntax (e.g., `list` instead of `List`)
   - Currently ignored to maintain compatibility
   - Can be gradually adopted

2. **RUF rules** - Ruff-specific best practices
   - RUF100: Remove unused `noqa` directives
   - RUF022: Sort `__all__` definitions
   - Generally good practices to adopt

3. **A002** - Shadowing Python builtins
   - More strict than pylint's implementation
   - `id` parameter is flagged (was allowed in pylint config)

## Suppressing Violations

### Inline Suppression
```python
# Same as before, use noqa comments
result = eval(user_input)  # noqa: S307
```

### File/Directory Level
Configure in `pyproject.toml` under `[tool.ruff.lint.per-file-ignores]`:
```toml
"tests/*" = ["S101", "D"]  # Ignore assert-used and docstrings in tests
```

## Auto-Fix Results

After enabling unsafe fixes and removing Python upgrade ignores:
- **Initial issues**: 675
- **Auto-fixed**: 609 (90%)
- **Remaining**: 66

Most auto-fixes were:
- Python syntax upgrades (`List` → `list`, `Union` → `|`, etc.)
- Import optimizations
- Type annotation modernization
- Minor style improvements

## Migration Checklist

- [x] Updated requirements.txt (added ruff, removed old tools)
- [x] Updated pyproject.toml with Ruff configuration
- [x] Updated .pre-commit-config.yaml to use Ruff
- [x] Updated Makefile commands to use Ruff
- [x] Removed old config files (.flake8)
- [x] Tested on codebase to verify equivalent checking
- [x] Enabled auto-fix with unsafe fixes
- [x] Applied auto-fixes to modernize code

## Benefits Realized

1. **Simplicity**: One tool instead of five
2. **Speed**: ~1000x faster linting
3. **Consistency**: Single configuration file
4. **Maintenance**: Fewer dependencies to manage
5. **Developer Experience**: Faster feedback loops

## Future Considerations

1. **Python Syntax Upgrades**: Consider enabling UP rules gradually
2. **Preview Rules**: Some rules like PLR0904 require `--preview` flag
3. **Cognitive Complexity**: Currently using McCabe (C901) as a proxy
4. **Custom Rules**: Ruff doesn't support plugins, all rules are built-in

## Troubleshooting

### Issue: "Unknown rule selector"
- Check if the rule exists in Ruff with `ruff rule <code>`
- Some pylint rules don't have Ruff equivalents

### Issue: Import sorting differs
- Ruff's isort implementation may sort slightly differently
- Use `ruff check --fix` to automatically fix

### Issue: Pre-commit hooks fail
- Run `pre-commit install` to update hooks
- Clear cache with `pre-commit clean`

## Resources

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Ruff Rules Reference](https://docs.astral.sh/ruff/rules/)
- [Ruff Configuration](https://docs.astral.sh/ruff/configuration/)