# Docker Containerization Strategy

* Status: accepted
* Deciders: Development team
* Date: 2025-01-11

## Context and Problem Statement

StockBook needs a consistent way to package and deploy the application across different environments (development, staging, production). We need to ensure that the application runs the same way regardless of the host system, with all dependencies properly isolated. Container technology provides a solution, but we need to decide on our containerization strategy, including image optimization, security considerations, and development workflow. How should we containerize our Python FastAPI application?

## Decision Drivers

* **Consistency**: Same behavior across all environments
* **Security**: Minimize attack surface and vulnerabilities
* **Performance**: Fast builds and small image sizes
* **Developer Experience**: Easy local development with containers
* **Production Readiness**: Optimized for deployment
* **Dependency Management**: Clear and reproducible dependencies
* **Multi-stage Benefits**: Separate build and runtime environments

## Considered Options

* **Multi-stage Docker**: Separate build and runtime stages
* **Single-stage Docker**: Simple Dockerfile with everything
* **Docker Compose Only**: Use compose for all environments
* **Buildpacks**: Use Cloud Native Buildpacks
* **Distroless Images**: Google's distroless base images
* **Alpine-based**: Minimal Alpine Linux images

## Decision Outcome

Chosen option: "Multi-stage Docker", because it provides the best balance of security, performance, and maintainability. Multi-stage builds allow us to separate build dependencies from runtime dependencies, resulting in smaller, more secure images. This approach also enables better caching and faster builds while maintaining a clear separation of concerns.

### Positive Consequences

* **Smaller Images**: Only runtime dependencies in final image
* **Better Security**: Fewer attack vectors in production
* **Build Caching**: Efficient layer caching
* **Clear Separation**: Build tools separate from runtime
* **Flexibility**: Different base images for different stages
* **Standards Compliance**: Follows Docker best practices
* **CI/CD Friendly**: Works well with automated pipelines

### Negative Consequences

* **Complexity**: More complex than single-stage
* **Debugging**: Harder to debug multi-stage issues
* **Learning Curve**: Requires understanding of stages
* **Build Time**: Initial builds might be longer

## Pros and Cons of the Options

### Multi-stage Docker

Use multiple FROM statements for different build stages.

* Good, because smallest final images
* Good, because separates concerns
* Good, because better security
* Good, because efficient caching
* Good, because flexible base images
* Good, because production optimized
* Bad, because more complex
* Bad, because requires more Docker knowledge

### Single-stage Docker

Simple Dockerfile with all steps in one stage.

* Good, because simple to understand
* Good, because easy to debug
* Good, because quick to write
* Bad, because larger images
* Bad, because includes build tools
* Bad, because security concerns
* Bad, because slower deploys

### Docker Compose Only

Rely entirely on docker-compose for builds.

* Good, because integrated with services
* Good, because good for development
* Bad, because not for production
* Bad, because compose-specific
* Bad, because limited build options
* Bad, because not CI/CD friendly

### Buildpacks

Use Cloud Native Buildpacks for automatic builds.

* Good, because automatic detection
* Good, because follows standards
* Good, because security updates
* Bad, because less control
* Bad, because black box builds
* Bad, because limited customization
* Bad, because vendor lock-in risk

### Distroless Images

Use Google's distroless images for runtime.

* Good, because minimal attack surface
* Good, because very small
* Good, because no shell
* Bad, because hard to debug
* Bad, because limited tooling
* Bad, because Python support issues
* Bad, because restrictive

### Alpine-based

Use Alpine Linux as base image.

* Good, because very small
* Good, because has package manager
* Good, because popular choice
* Bad, because musl libc issues
* Bad, because Python wheels problems
* Bad, because compilation needed
* Bad, because compatibility issues

## Implementation Details

Our Docker containerization strategy:

### Production Dockerfile

```dockerfile
# Dockerfile
# Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root --only main

# Copy application code
COPY src ./src

# Build application
RUN poetry build

# Runtime stage
FROM python:3.11-slim as runtime

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application from builder
COPY --from=builder /app/src ./src

# Copy entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Default command
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Development Dockerfile

```dockerfile
# Dockerfile.dev
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.7.1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==$POETRY_VERSION

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install all dependencies (including dev)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy application code (done by volume mount in dev)
# COPY . .

# Expose port
EXPOSE 8000

# Run with hot reload
CMD ["uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose for Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app
      - /app/.venv  # Exclude virtualenv from mount
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/stockbook
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    networks:
      - stockbook-network

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=stockbook
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - stockbook-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - stockbook-network

  pgadmin:
    image: dpage/pgadmin4
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@stockbook.local
      - PGADMIN_DEFAULT_PASSWORD=admin
    ports:
      - "5050:80"
    depends_on:
      - db
    networks:
      - stockbook-network

volumes:
  postgres_data:

networks:
  stockbook-network:
    driver: bridge
```

### Entrypoint Script

```bash
#!/bin/sh
# docker/entrypoint.sh

echo "Starting StockBook..."

# Wait for database
if [ -n "$DATABASE_URL" ]; then
    echo "Waiting for database..."
    while ! pg_isready -h ${DATABASE_HOST:-db} -p ${DATABASE_PORT:-5432}; do
        sleep 1
    done
    echo "Database is ready!"
    
    # Run migrations
    echo "Running database migrations..."
    alembic upgrade head
fi

# Execute the main command
exec "$@"
```

### Security Hardening

```dockerfile
# Additional security measures
FROM python:3.11-slim as runtime

# Security updates
RUN apt-get update && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# Remove unnecessary tools
RUN apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /usr/share/doc/* \
    && rm -rf /usr/share/man/* \
    && rm -rf /var/cache/apt/*

# Set security options
RUN echo "appuser:x:1000:1000::/app:/bin/false" >> /etc/passwd \
    && echo "appuser:x:1000:" >> /etc/group

# Disable shell access
RUN rm /bin/sh && ln -s /bin/false /bin/sh

# Set file permissions
RUN chmod -R 755 /app \
    && find /app -type f -exec chmod 644 {} \;
```

### Build Optimization

```dockerfile
# .dockerignore
**/__pycache__
**/*.pyc
**/*.pyo
**/*.pyd
.Python
.venv/
venv/
ENV/
env/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
htmlcov/
.pytest_cache/
coverage.xml
*.cover
*.log
.git
.gitignore
.mypy_cache
.hypothesis
.dockerignore
Dockerfile*
docker-compose*.yml
.github/
.vscode/
.idea/
*.md
tests/
docs/
```

### CI/CD Integration

```yaml
# .github/workflows/docker.yml
name: Docker Build

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to DockerHub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            stockbook/app:latest
            stockbook/app:${{ github.sha }}
          cache-from: type=registry,ref=stockbook/app:buildcache
          cache-to: type=registry,ref=stockbook/app:buildcache,mode=max
```

### Production Deployment

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    image: stockbook/app:latest
    restart: always
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - SENTRY_DSN=${SENTRY_DSN}
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## Links

* Supports [ADR-0006: Python FastAPI SQLAlchemy Stack](0006-python-fastapi-sqlalchemy-stack.md)
* Complements [ADR-0016: Makefile for Build Automation](0016-makefile-for-build-automation.md)
* Enables cloud deployment strategies
* References: Docker best practices documentation
* References: "Docker Deep Dive" by Nigel Poulton