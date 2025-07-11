# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for the Stockbook project.

## What is an ADR?

An Architecture Decision Record (ADR) is a document that captures an important architectural decision made along with its context and consequences.

## ADR Index

| ADR | Status | Decision |
|-----|--------|----------|
| [0001](0001-record-architecture-decisions.md) | Accepted | Record architecture decisions |
| [0002](0002-use-clean-architecture.md) | Accepted | Use Clean Architecture |
| [0003](0003-implement-domain-driven-design.md) | Accepted | Implement Domain-Driven Design |
| [0004](0004-use-custom-dependency-injection.md) | Accepted | Use Custom Dependency Injection Container |
| [0005](0005-mandate-test-driven-development.md) | Accepted | Mandate Test-Driven Development |
| [0006](0006-python-fastapi-sqlalchemy-stack.md) | Accepted | Python FastAPI SQLAlchemy Technology Stack |
| [0007](0007-value-objects-for-type-safety.md) | Accepted | Use Value Objects for Type Safety and Domain Modeling |
| [0008](0008-repository-pattern.md) | Accepted | Use Repository Pattern for Data Access |
| [0009](0009-unit-of-work-pattern.md) | Accepted | Use Unit of Work Pattern for Transaction Management |
| [0010](0010-event-driven-architecture-foundation.md) | Accepted | Event-Driven Architecture Foundation |
| [0011](0011-use-sqlalchemy-core-over-orm.md) | Accepted | Use SQLAlchemy Core Over ORM |
| [0012](0012-command-pattern-for-application-layer.md) | Accepted | Use Command Pattern for Application Layer |
| [0013](0013-dto-pattern-for-layer-boundaries.md) | Accepted | Use DTO Pattern for Layer Boundaries |
| [0014](0014-composition-root-pattern.md) | Accepted | Use Composition Root Pattern |
| [0015](0015-pre-commit-hooks-for-quality-enforcement.md) | Accepted | Use Pre-commit Hooks for Quality Enforcement |
| [0016](0016-makefile-for-build-automation.md) | Accepted | Use Makefile for Build Automation |
| [0017](0017-docker-containerization-strategy.md) | Accepted | Docker Containerization Strategy |
| [0018](0018-aggregate-design-and-boundaries.md) | Accepted | Define Aggregate Design and Boundaries |
| [0019](0019-cors-configuration-strategy.md) | Accepted | CORS Configuration Strategy |
| [0020](0020-phased-architecture-evolution.md) | Accepted | Phased Architecture Evolution |

## Creating New ADRs

1. Copy the [template.md](template.md) file
2. Name it with the next number in sequence: `NNNN-title-with-dashes.md`
3. Fill in the sections
4. Update this index

## ADR Status

- **Draft**: The ADR is being written and discussed
- **Proposed**: The ADR is complete and ready for review
- **Accepted**: The ADR has been accepted and is in effect
- **Deprecated**: The ADR has been superseded by a newer decision
- **Superseded**: The ADR has been replaced by another ADR (include reference)