# Commit Convention

This project uses a simple, consistent commit message format to maintain clear project history.

## Format

```
<type>: <description>
```

## Types

- **feat**: New feature or functionality
- **fix**: Bug fixes
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring without changing functionality
- **test**: Adding or updating tests
- **chore**: Maintenance tasks, dependencies, build changes
- **init**: Initial project setup

## Examples

```
init: initial Streamlit app setup with basic scaffolding
feat: add user authentication system
fix: resolve data loading timeout issue
docs: update README with installation instructions
refactor: extract data processing into separate module
```

## Guidelines

- Use present tense ("add" not "added")
- Keep the description concise but descriptive
- Start with lowercase letter
- No period at the end
- Aim for 50 characters or less when possible
- Omit lines like 'Generated with [Claude Code]' and 'Co-Authored-By: Claude <claude@claude.com>' from the commit message
