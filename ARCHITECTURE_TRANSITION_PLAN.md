# StockBook Architecture Transition Plan: Streamlit to FastAPI

## Executive Summary

The StockBook application is well-positioned for this transition thanks to its Clean Architecture implementation. The domain and application layers are completely independent of the presentation layer, making this a straightforward replacement of the presentation layer components.

## Architecture Overview

### Current State
- **Clean Architecture**: 4-layer structure (Domain, Application, Infrastructure, Presentation)
- **DI Container**: Professional IoC container with composition root
- **Presentation Layer**: Streamlit-specific adapters, controllers, and coordinators
- **Business Logic**: Fully encapsulated in domain and application layers

### Target State
- **API Layer**: FastAPI replacing Streamlit presentation layer
- **Same Architecture**: Domain, Application, and Infrastructure layers remain unchanged
- **RESTful API**: Standard HTTP endpoints for all operations
- **Future Ready**: Clean API for Flutter frontend integration

## Transition Tasks

### Phase 1: Setup and Infrastructure (2-3 days)

1. **Add FastAPI Dependencies**
   - Add to requirements.txt: `fastapi`, `uvicorn`, `python-multipart`, `httpx` (for testing)
   - Add development dependencies: `pytest-asyncio`
   - Remove Streamlit dependencies after transition

2. **Create FastAPI Application Structure**
   - Create `api/` directory at project root
   - Add subdirectories: `api/routers/`, `api/schemas/`, `api/dependencies/`, `api/middleware/`
   - Create `api/main.py` as FastAPI entry point

3. **Update Dependency Injection**
   - Create `api/dependencies/container.py` to initialize DI container for FastAPI
   - Add request-scoped dependency injection helpers
   - Ensure proper lifecycle management for database connections

### Phase 2: API Schema Design (3-4 days)

4. **Create Pydantic Schemas**
   - Create `api/schemas/stock.py` with request/response models
   - Create `api/schemas/portfolio.py`, `api/schemas/transaction.py`, etc.
   - Map from existing ViewModels and DTOs to Pydantic models
   - Add OpenAPI documentation strings

5. **Design RESTful Endpoints**
   - Document all API endpoints in `api/docs/api_specification.md`
   - Follow REST conventions: GET, POST, PUT, DELETE
   - Plan pagination, filtering, and sorting strategies

### Phase 3: Core API Implementation (5-7 days)

6. **Implement Stock Management API**
   - Create `api/routers/stocks.py`
   - Endpoints: `GET /stocks`, `GET /stocks/{id}`, `POST /stocks`, `PUT /stocks/{id}`, `DELETE /stocks/{id}`
   - Add search endpoint: `GET /stocks/search`
   - Reuse existing StockController logic

7. **Implement Portfolio Management API**
   - Create `api/routers/portfolios.py`
   - Basic CRUD operations
   - Portfolio balance endpoints
   - Position calculations

8. **Implement Transaction API**
   - Create `api/routers/transactions.py`
   - Transaction recording and updates
   - Transaction history with filtering

9. **Implement Additional APIs**
   - Targets API (`api/routers/targets.py`)
   - Journal API (`api/routers/journal.py`)
   - Analytics API (`api/routers/analytics.py`)

### Phase 4: API Features (3-4 days)

10. **Add Authentication & Authorization**
    - Implement JWT authentication
    - Create `api/auth/` module
    - Add user management endpoints
    - Secure all endpoints with proper permissions

11. **Error Handling & Validation**
    - Create `api/middleware/error_handler.py`
    - Implement global exception handling
    - Map domain exceptions to HTTP status codes
    - Add request validation middleware

12. **API Documentation & Testing**
    - Configure Swagger/OpenAPI documentation
    - Add API versioning strategy
    - Create `tests/api/` test suite
    - Write integration tests for all endpoints

### Phase 5: Advanced Features (2-3 days)

13. **Add WebSocket Support**
    - Real-time price updates
    - Portfolio value streaming
    - Live transaction notifications

14. **Implement Caching**
    - Add Redis for caching (optional)
    - Cache frequently accessed data
    - Implement cache invalidation strategies

15. **Background Tasks**
    - Add Celery or background tasks for long operations
    - Scheduled portfolio calculations
    - Daily balance snapshots

### Phase 6: Migration & Deployment (2-3 days)

16. **Create Migration Guide**
    - Document all API endpoints
    - Create Postman/Insomnia collection
    - Write developer documentation

17. **Update Configuration**
    - Create `api/config.py` for API-specific settings
    - Update `config.py` to remove Streamlit settings
    - Add environment variable support

18. **Deployment Setup**
    - Create `Dockerfile` for containerization
    - Add `docker-compose.yml` for local development
    - Create production deployment scripts
    - Setup CORS for Flutter integration

### Phase 7: Cleanup (1-2 days)

19. **Remove Streamlit Code**
    - Delete `app.py`
    - Remove `presentation/adapters/streamlit_*` files
    - Clean up Streamlit-specific dependencies
    - Update tests to remove Streamlit references

20. **Refactor Presentation Layer**
    - Keep controllers for business logic orchestration
    - Convert ViewModels to work with Pydantic
    - Update composition root to remove Streamlit registrations

## Technical Considerations

### Database Connection Management
- Use SQLAlchemy with FastAPI for better async support
- Implement connection pooling
- Add database migrations with Alembic

### Testing Strategy
- Unit tests for all API endpoints
- Integration tests with test database
- Load testing for performance validation
- API contract testing

### Security Considerations
- Input validation on all endpoints
- SQL injection prevention (already handled by repositories)
- Rate limiting
- API key management

### Performance Optimizations
- Implement pagination for list endpoints
- Add database indexes for common queries
- Use async/await for I/O operations
- Consider query optimization

## Estimated Timeline

- **Total Duration**: 18-25 days (3-5 weeks)
- **Parallel Work**: Some tasks can be done concurrently
- **Testing Buffer**: Add 20% for testing and bug fixes

## Success Criteria

1. All current functionality available via REST API
2. Comprehensive test coverage (>80%)
3. API documentation complete
4. Performance benchmarks met
5. Security audit passed
6. Zero data loss during transition

## Risk Mitigation

1. **Data Integrity**: Keep both systems running in parallel initially
2. **Testing**: Extensive testing at each phase
3. **Rollback Plan**: Maintain Streamlit code in separate branch
4. **Documentation**: Document all decisions and changes

This plan leverages the existing Clean Architecture to make the transition smooth and low-risk. The domain and application layers remain untouched, ensuring business logic integrity throughout the process.