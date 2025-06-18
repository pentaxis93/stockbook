# Audit Business Logic Command

**Command:** `audit-business-logic {argument}`

## Description
Creates a comprehensive audit document for business logic related to a specific entity or domain concept. This command systematically documents all business logic organized by architectural layer and logical sequence, providing space for human feedback on each component.

## Usage
```
audit-business-logic stock
audit-business-logic portfolio
audit-business-logic position
```

## Instructions
It is time to audit the business logic around {argument}. Create a document which documents each piece of {argument}-related business logic. Organize it logically, by architectural layer and also in a logical sequence. Do not analyze the business logic, just describe it simply. Leave demarcated space like this

```
___
```

after each method or other business logic for a human to provide feedback. The purpose of this audit is to validate each piece of business logic against the requirements, so do not add additional content or analysis beyond what is requested here.

## Output
- Creates a document named `{ARGUMENT}_BUSINESS_LOGIC_AUDIT.md` in the project root
- Documents are organized by Clean Architecture layers:
  - Domain Layer (Value Objects, Entities, Domain Services)
  - Application Layer (Application Services, Commands)
  - Presentation Layer (Controllers, Adapters)
  - Cross-Cutting Concerns (Transaction Management, Error Handling, etc.)
- Each business logic component includes:
  - Method signature and purpose
  - Brief description of what it does
  - Feedback space demarcated with `___`

## Example Output Structure
```markdown
# {Argument} Business Logic Audit

## Domain Layer

### Value Objects
#### ArgumentSymbol Value Object
**Method validation logic:**
- Validates argument symbols must be 1-5 uppercase letters only

```
___
```

### Entities
#### ArgumentEntity
**Business behavior methods:**
- `calculate_something()` - Calculates some business value

```
___
```

## Application Layer
...
```

This command helps ensure all business logic is properly reviewed and validated against requirements before implementation changes.