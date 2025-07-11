# CORS Configuration Strategy

* Status: accepted
* Deciders: Development team
* Date: 2025-01-11

## Context and Problem Statement

StockBook's API needs to be accessible from web browsers, potentially from different domains during development and production. Cross-Origin Resource Sharing (CORS) policies control which domains can access our API, what methods they can use, and what headers they can send. We need a CORS strategy that balances security with functionality, supporting both development flexibility and production security. How should we configure CORS for our FastAPI application?

## Decision Drivers

* **Security**: Prevent unauthorized cross-origin access
* **Development Experience**: Easy local development with hot reload
* **Production Safety**: Strict policies for production
* **Flexibility**: Support various client deployment scenarios
* **Standards Compliance**: Follow CORS best practices
* **Performance**: Minimize preflight requests
* **Configuration**: Environment-specific settings

## Considered Options

* **Environment-based CORS**: Different policies per environment
* **Wildcard Development**: Allow all origins in development
* **Whitelist Only**: Strict whitelist for all environments
* **Dynamic CORS**: Runtime determination of allowed origins
* **No CORS**: Proxy all requests through same origin
* **Permissive CORS**: Allow all origins always

## Decision Outcome

Chosen option: "Environment-based CORS", because it provides the optimal balance between development convenience and production security. This approach allows unrestricted access during local development while maintaining strict origin controls in production. Environment-specific configuration ensures that security policies are appropriate for each deployment context.

### Positive Consequences

* **Development Flexibility**: No CORS issues during development
* **Production Security**: Strict controls in production
* **Easy Configuration**: Environment variables control behavior
* **Clear Policies**: Explicit about what's allowed
* **Standards Compliant**: Follows CORS best practices
* **Performance**: Can optimize for known origins
* **Debugging**: Clear error messages for CORS issues

### Negative Consequences

* **Configuration Complexity**: Must manage per environment
* **Potential Mistakes**: Wrong environment settings
* **Testing Overhead**: Need to test CORS policies
* **Documentation Need**: Must document allowed origins

## Pros and Cons of the Options

### Environment-based CORS

Different CORS policies based on deployment environment.

* Good, because balances security and convenience
* Good, because appropriate for each context
* Good, because follows twelve-factor app principles
* Good, because easy to understand
* Good, because production-safe
* Good, because development-friendly
* Bad, because requires environment configuration
* Bad, because potential for misconfiguration

### Wildcard Development

Allow all origins (*) in development only.

* Good, because maximum development flexibility
* Good, because no CORS errors locally
* Good, because simple configuration
* Bad, because developers might expect same in production
* Bad, because doesn't test real CORS behavior
* Bad, because security risk if deployed wrong

### Whitelist Only

Strict whitelist of allowed origins in all environments.

* Good, because consistent behavior
* Good, because most secure
* Good, because predictable
* Bad, because painful for development
* Bad, because requires constant updates
* Bad, because blocks legitimate testing
* Bad, because slows development

### Dynamic CORS

Determine allowed origins at runtime from database/config.

* Good, because flexible without redeploy
* Good, because can update on the fly
* Good, because supports multi-tenant
* Bad, because complex implementation
* Bad, because performance overhead
* Bad, because harder to debug
* Bad, because potential security risks

### No CORS

Proxy all requests through same origin.

* Good, because avoids CORS entirely
* Good, because simple conceptually
* Good, because no preflight requests
* Bad, because requires proxy setup
* Bad, because complicates deployment
* Bad, because not always feasible
* Bad, because hides real issues

### Permissive CORS

Allow all origins in all environments.

* Good, because simple
* Good, because no configuration
* Good, because works everywhere
* Bad, because major security risk
* Bad, because allows any site access
* Bad, because not production appropriate
* Bad, because violates best practices

## Implementation Details

Our CORS configuration strategy:

### Configuration Settings

```python
# src/config/settings.py
from typing import List, Optional
from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    """Application settings with CORS configuration."""
    
    # Environment
    environment: str = "development"
    
    # CORS Settings
    cors_allow_origins: List[str] = []
    cors_allow_credentials: bool = False
    cors_allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    cors_allow_headers: List[str] = ["*"]
    cors_max_age: int = 3600  # 1 hour
    
    @validator("cors_allow_origins", pre=True)
    def parse_cors_origins(cls, v, values):
        """Parse CORS origins from environment."""
        if isinstance(v, str):
            # Support comma-separated list
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("cors_allow_origins")
    def set_cors_origins(cls, v, values):
        """Set CORS origins based on environment."""
        environment = values.get("environment", "development")
        
        if environment == "development":
            # Allow all origins in development
            return ["*"]
        elif environment == "staging":
            # Staging origins
            return [
                "https://staging.stockbook.app",
                "https://preview.stockbook.app"
            ]
        elif environment == "production":
            # Production origins only
            return [
                "https://stockbook.app",
                "https://www.stockbook.app",
                "https://app.stockbook.app"
            ]
        
        # Use provided origins if any
        return v or []
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```

### FastAPI CORS Middleware

```python
# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import Settings

def create_app(settings: Settings = None) -> FastAPI:
    """Create and configure FastAPI application."""
    
    if settings is None:
        settings = Settings()
    
    app = FastAPI(
        title="StockBook API",
        version="1.0.0"
    )
    
    # Configure CORS
    setup_cors(app, settings)
    
    return app

def setup_cors(app: FastAPI, settings: Settings) -> None:
    """Configure CORS middleware based on settings."""
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
        max_age=settings.cors_max_age,
    )
    
    # Log CORS configuration
    if settings.environment == "development":
        print("⚠️  CORS: Allowing all origins (development mode)")
    else:
        print(f"🔒 CORS: Allowing origins: {settings.cors_allow_origins}")
```

### Environment-Specific Configuration

```bash
# .env.development
ENVIRONMENT=development
# CORS automatically allows all origins

# .env.staging
ENVIRONMENT=staging
CORS_ALLOW_ORIGINS=https://staging.stockbook.app,https://preview.stockbook.app
CORS_ALLOW_CREDENTIALS=true

# .env.production
ENVIRONMENT=production
CORS_ALLOW_ORIGINS=https://stockbook.app,https://www.stockbook.app
CORS_ALLOW_CREDENTIALS=true
CORS_MAX_AGE=86400  # 24 hours for production
```

### Advanced CORS Configuration

```python
# src/middleware/cors_advanced.py
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class AdvancedCORSMiddleware(BaseHTTPMiddleware):
    """Advanced CORS handling with dynamic origin validation."""
    
    def __init__(self, app, settings: Settings):
        super().__init__(app)
        self.settings = settings
        self.allowed_origins = set(settings.cors_allow_origins)
        self.allow_patterns = self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for wildcard origins."""
        import re
        patterns = []
        
        # Support wildcard subdomains
        for origin in self.settings.cors_allow_origins:
            if "*" in origin and origin != "*":
                # Convert wildcard to regex
                pattern = origin.replace(".", r"\.")
                pattern = pattern.replace("*", r"[^.]+")
                patterns.append(re.compile(f"^{pattern}$"))
        
        return patterns
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Handle CORS preflight and actual requests."""
        
        # Get origin
        origin = request.headers.get("origin")
        
        # Handle preflight
        if request.method == "OPTIONS":
            response = Response(status_code=200)
            response = self._add_cors_headers(response, origin)
            return response
        
        # Process request
        response = await call_next(request)
        
        # Add CORS headers
        if origin:
            response = self._add_cors_headers(response, origin)
        
        return response
    
    def _is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed."""
        # Exact match
        if origin in self.allowed_origins:
            return True
        
        # Wildcard match
        if "*" in self.allowed_origins:
            return True
        
        # Pattern match
        for pattern in self.allow_patterns:
            if pattern.match(origin):
                return True
        
        return False
    
    def _add_cors_headers(self, response: Response, origin: str) -> Response:
        """Add CORS headers to response."""
        if self._is_origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = str(
                self.settings.cors_allow_credentials
            ).lower()
            response.headers["Access-Control-Allow-Methods"] = ", ".join(
                self.settings.cors_allow_methods
            )
            response.headers["Access-Control-Allow-Headers"] = ", ".join(
                self.settings.cors_allow_headers
            )
            response.headers["Access-Control-Max-Age"] = str(
                self.settings.cors_max_age
            )
        
        return response
```

### Security Headers

```python
# src/middleware/security_headers.py
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

def add_security_headers(app: FastAPI) -> None:
    """Add security headers including CORS-related ones."""
    
    @app.middleware("http")
    async def security_headers_middleware(request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy
        csp = "default-src 'self'; script-src 'self' 'unsafe-inline'"
        response.headers["Content-Security-Policy"] = csp
        
        return response
```

### Testing CORS

```python
# tests/test_cors.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_cors_preflight(client: AsyncClient):
    """Test CORS preflight request."""
    response = await client.options(
        "/api/stocks",
        headers={
            "Origin": "https://stockbook.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
    )
    
    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" in response.headers
    assert response.headers["Access-Control-Allow-Origin"] == "https://stockbook.app"

@pytest.mark.asyncio
async def test_cors_actual_request(client: AsyncClient):
    """Test CORS headers on actual request."""
    response = await client.get(
        "/api/stocks",
        headers={"Origin": "https://stockbook.app"}
    )
    
    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "https://stockbook.app"

@pytest.mark.asyncio
async def test_cors_unauthorized_origin(client: AsyncClient):
    """Test CORS with unauthorized origin."""
    response = await client.get(
        "/api/stocks",
        headers={"Origin": "https://evil.com"}
    )
    
    assert response.status_code == 200  # Request succeeds
    assert "Access-Control-Allow-Origin" not in response.headers  # But no CORS headers
```

### Documentation

```python
# src/docs/cors.md
"""
# CORS Configuration

## Development
- All origins allowed (`*`)
- Credentials allowed
- All methods allowed

## Staging
Allowed origins:
- https://staging.stockbook.app
- https://preview.stockbook.app

## Production
Allowed origins:
- https://stockbook.app
- https://www.stockbook.app
- https://app.stockbook.app

## Testing CORS
```bash
# Test preflight
curl -X OPTIONS https://api.stockbook.app/stocks \
  -H "Origin: https://stockbook.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type"

# Test actual request
curl https://api.stockbook.app/stocks \
  -H "Origin: https://stockbook.app"
```
"""
```

## Links

* Implements security for [ADR-0006: Python FastAPI SQLAlchemy Stack](0006-python-fastapi-sqlalchemy-stack.md)
* Part of [ADR-0002: Use Clean Architecture](0002-use-clean-architecture.md) presentation layer
* References: MDN CORS documentation
* References: OWASP CORS security cheat sheet