"""Stock router for FastAPI endpoints.

Handles HTTP requests related to stock operations and delegates
to the application layer for business logic.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from src.application.services.stock_application_service import StockApplicationService
from src.presentation.web.middleware import handle_stock_errors
from src.presentation.web.models.stock_models import (
    StockListResponse,
    StockRequest,
    StockResponse,
    StockUpdateRequest,
)

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(
    prefix="/stocks",
    tags=["stocks"],
    responses={404: {"description": "Not found"}},
)


# Service dependency is retrieved from app state via FastAPI's dependency injection


def get_stock_service(request: Request) -> StockApplicationService:
    """Dependency function to get StockApplicationService instance from app state.

    Args:
        request: FastAPI request object containing app state

    Returns:
        StockApplicationService instance

    Raises:
        RuntimeError: If DI container not configured in app state
    """
    if not hasattr(request.app.state, "di_container"):
        raise RuntimeError("DI container not configured in app state")
    service: StockApplicationService = request.app.state.di_container.resolve(
        StockApplicationService
    )
    return service


# Module-level singleton for dependency injection to satisfy B008
stock_service_dependency = Depends(get_stock_service)


@router.get("", response_model=StockListResponse)
@handle_stock_errors
async def get_stocks(
    symbol: Annotated[
        str | None, Query(description="Filter by stock symbol (partial match)")
    ] = None,
    service: StockApplicationService = stock_service_dependency,
) -> StockListResponse:
    """Get list of stocks with optional filtering.

    Query parameters:
    - symbol: Filter by stock symbol (partial match, case-insensitive)

    Returns:
        StockListResponse containing filtered stocks and total count
    """
    # Check if we have any non-empty filters
    has_filters = False

    # Clean up filter values - empty strings should be None
    if symbol is not None and symbol.strip():
        symbol = symbol.strip()
        has_filters = True
    else:
        symbol = None

    # Use appropriate service method based on filters
    if has_filters:
        # Use search_stocks with filters
        stock_dtos = service.search_stocks(
            symbol_filter=symbol,
            name_filter=None,  # Not exposed in API
            industry_filter=None,  # Not exposed in API
        )
    else:
        # No filters - get all stocks
        stock_dtos = service.get_all_stocks()

    # Convert DTOs to response model
    return StockListResponse.from_dto_list(stock_dtos)


@router.get("/{stock_id}", response_model=StockResponse)
async def get_stock_by_id(
    stock_id: str,
    service: StockApplicationService = stock_service_dependency,
) -> StockResponse:
    """Get a specific stock by its ID.

    Args:
        stock_id: The unique identifier of the stock
        service: Stock application service dependency

    Returns:
        StockResponse containing the stock information

    Raises:
        HTTPException: 404 if stock not found, 500 for server errors
    """
    try:
        # Get stock from service
        stock_dto = service.get_stock_by_id(stock_id)

        # Check if stock exists
        if stock_dto is None:
            logger.warning("Stock with ID %s not found", stock_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stock with ID {stock_id} not found",
            )

        # Convert DTO to response model
        return StockResponse.from_dto(stock_dto)

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error("Error retrieving stock %s: %s", stock_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve stock",
        ) from e


@router.post("", response_model=StockResponse, status_code=status.HTTP_201_CREATED)
@handle_stock_errors
async def create_stock(
    stock_request: StockRequest,
    service: StockApplicationService = stock_service_dependency,
) -> StockResponse:
    """Create a new stock.

    Request body:
    - symbol: Stock ticker symbol (required, 1-5 letters)
    - name: Company name (required, max 200 chars)
    - sector: Business sector (optional)
    - industry_group: Industry group (optional, requires sector)
    - grade: Stock grade (optional, A/B/C/D/F)
    - notes: Additional notes (optional)

    Returns:
        StockResponse with 201 Created status

    Raises:
        HTTPException: 422 for validation errors, 400 for duplicates, 500 for
            server errors
    """
    # Convert request to command
    command = stock_request.to_command()

    # Call application service
    stock_dto = service.create_stock(command)

    # Convert DTO to response
    return StockResponse.from_dto(stock_dto)


@router.put("/{stock_id}", response_model=StockResponse)
@handle_stock_errors
async def update_stock(
    stock_id: str,
    stock_update: StockUpdateRequest,
    service: StockApplicationService = stock_service_dependency,
) -> StockResponse:
    """Update an existing stock.

    Path parameters:
    - stock_id: The unique identifier of the stock

    Request body (all fields optional):
    - symbol: New stock ticker symbol (1-5 letters)
    - name: New company name (max 200 chars)
    - sector: New business sector
    - industry_group: New industry group (requires sector)
    - grade: New stock grade (A/B/C/D/F)
    - notes: New additional notes

    Returns:
        StockResponse with updated stock data

    Raises:
        HTTPException: 404 if stock not found, 400 for duplicate symbol,
                      422 for validation errors, 500 for server errors
    """
    # Convert request to command
    command = stock_update.to_command(stock_id)

    # Call application service
    stock_dto = service.update_stock(command)

    # Convert DTO to response
    return StockResponse.from_dto(stock_dto)
