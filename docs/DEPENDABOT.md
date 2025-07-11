# Dependabot Configuration Guide

This document explains how Dependabot is configured for the StockBook project and how to work with automated dependency updates.

## Overview

Dependabot is configured to automatically create pull requests for dependency updates, helping keep the project secure and up-to-date. The configuration is optimized to balance staying current with minimizing disruption to development.

## Configuration

The Dependabot configuration is located at `.github/dependabot.yml` and manages three package ecosystems:

### 1. Python Dependencies (pip)
- **Schedule**: Weekly on Mondays at 4:00 AM UTC
- **PR Limit**: Maximum 5 open PRs at a time
- **Grouping**: Dependencies are grouped by category to reduce PR noise:
  - **development-dependencies**: Testing and development tools (black, mypy, pytest, etc.)
  - **testing**: Test-specific dependencies
  - **linting**: Code quality tools
  - **typing**: Type checking and stubs
- **Versioning Strategy**: Increase version requirements only when necessary

### 2. GitHub Actions
- **Schedule**: Weekly on Mondays at 4:00 AM UTC  
- **PR Limit**: Maximum 5 open PRs
- **Grouping**: All actions updates are grouped together

### 3. Docker Images
- **Schedule**: Weekly on Mondays at 4:00 AM UTC
- **PR Limit**: Maximum 2 open PRs
- **Purpose**: Ready for when specific base images are used

## Working with Dependabot PRs

### Automatic Quality Checks

All Dependabot PRs automatically trigger the CI workflow which runs:
- Type checking with pyright (strict mode)
- Linting with ruff
- Security scanning
- Full test suite with 100% coverage requirement
- Import linter for architecture compliance

### Reviewing PRs

1. **Check CI Status**: Ensure all checks pass before reviewing
2. **Review Changes**: Look for breaking changes in the changelog/release notes
3. **Test Locally**: For major updates, test locally before merging
4. **Merge Strategy**: Use squash and merge to keep history clean

### Managing Updates

#### Pausing Updates
To temporarily pause Dependabot updates, comment out the configuration:
```yaml
# updates:
#   - package-ecosystem: "pip"
#     ...
```

#### Ignoring Specific Dependencies
Add ignore rules to skip problematic updates:
```yaml
ignore:
  - dependency-name: "sqlalchemy"
    versions: ["2.1.x", "2.2.x"]  # Skip specific versions
  - dependency-name: "fastapi"
    update-types: ["version-update:semver-major"]  # Skip major updates
```

#### Security Updates
Security updates are prioritized and created immediately when vulnerabilities are discovered. These should be reviewed and merged promptly.

## Best Practices

1. **Regular Review**: Check Dependabot PRs weekly to prevent backlog
2. **Group Merging**: Merge related PRs together (e.g., all linting tools)
3. **Breaking Changes**: For major version updates, review migration guides
4. **Rollback Plan**: Be prepared to revert if issues arise post-merge
5. **Communication**: Notify team members of significant updates

## Troubleshooting

### Common Issues

1. **Merge Conflicts**: Dependabot automatically rebases PRs, but manual intervention may be needed for complex conflicts
2. **Test Failures**: Review test output to determine if the failure is due to the update or existing issues
3. **Type Checking Errors**: New versions may have stricter type definitions requiring code updates

### Getting Help

- Check the [Dependabot documentation](https://docs.github.com/en/code-security/dependabot)
- Review the dependency's changelog for migration guides
- Open an issue in the repository for team discussion

## Labels

Dependabot PRs are automatically labeled with:
- `dependencies`: All dependency updates
- `python`/`github-actions`/`docker`: Ecosystem-specific
- `automated`: Indicates bot-generated PR

These labels help with filtering and automation rules.