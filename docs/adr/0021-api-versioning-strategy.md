# API Versioning Strategy

* Status: proposed
* Deciders: Development team
* Date: 2025-01-11

## Context and Problem Statement

As StockBook evolves, we need to establish a clear API versioning strategy that will support backward compatibility when the API reaches stability. Currently at version 0.2.0, we must decide between implementing URL-based versioning now or deferring it until the API matures.

## Decision Drivers

* Early development stage (v0.2.0) with no stable API contract yet
* Need to minimize complexity during rapid iteration phase
* Future requirement to support multiple API versions simultaneously
* Client integration patterns and developer experience
* Industry best practices for RESTful API versioning

## Considered Options

* Option 1: Implement URL-based versioning immediately (e.g., `/api/v0/stocks`)
* Option 2: Use header/metadata versioning only until v1.0.0
* Option 3: No versioning strategy until v1.0.0

## Decision Outcome

Chosen option: "Option 2: Use header/metadata versioning only until v1.0.0", because it provides version visibility without adding URL complexity during the unstable development phase. URL-based versioning will be introduced when we need to maintain multiple stable API versions.

### Positive Consequences

* Simplified routing during early development
* Version information still available via metadata and headers
* Clear transition point at v1.0.0 for URL versioning
* Reduced complexity while API is unstable
* Flexibility to change API design without URL migration

### Negative Consequences

* Early adopters may need to update integration when URL versioning is introduced
* Less explicit version visibility in URLs during development

## Pros and Cons of the Options

### Option 1: Immediate URL-based versioning

Implement versioned URLs from the start (e.g., `/api/v0/stocks`)

* Good, because provides explicit version visibility in every request
* Good, because establishes versioning pattern early
* Bad, because adds unnecessary complexity during rapid iteration
* Bad, because v0.x.x indicates unstable API, making URL versioning premature
* Bad, because requires URL migration when moving from v0 to v1

### Option 2: Header/metadata versioning until v1.0.0

Use the current approach with version in app metadata and support header-based versioning

* Good, because keeps routing simple during development
* Good, because version info still available via `/version` endpoint and OpenAPI docs
* Good, because allows header-based version negotiation if needed
* Good, because clear transition point at v1.0.0
* Bad, because less explicit than URL versioning
* Bad, because requires client migration when URL versioning is introduced

### Option 3: No versioning strategy

Defer all versioning decisions until later

* Good, because maximum simplicity
* Bad, because no version visibility for early adopters
* Bad, because harder to introduce versioning later
* Bad, because no foundation for future versioning needs

## Implementation Details

Current implementation maintains:
- Version in `src/version.py` with `__api_version__ = "v1"`
- Version exposed in FastAPI app metadata
- `/version` endpoint returning version information

Future implementation at v1.0.0:
- Introduce URL prefix using `__api_version__` from version.py
- Mount routers with version prefix (e.g., `/api/v1/stocks`)
- Maintain previous version endpoints during transition period
- Support header-based version negotiation for smooth migration

## Links

* Related to [ADR-0006](0006-python-fastapi-sqlalchemy-stack.md) - FastAPI framework choice
* Related to [ADR-0020](0020-phased-architecture-evolution.md) - Phased evolution approach