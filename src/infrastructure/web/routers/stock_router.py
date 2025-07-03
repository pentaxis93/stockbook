"""
Stock router for FastAPI endpoints.

Handles HTTP requests related to stock operations and delegates
to the application layer for business logic.
"""

import logging
from typing import Annotated, Callable, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.application.services.stock_application_service import StockApplicationService
from src.infrastructure.web.models.stock_models import StockListResponse, StockResponse

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(
    prefix="/stocks",
    tags=["stocks"],
    responses={404: {"description": "Not found"}},
)


# Dependency injection placeholder - will be set by main app
_service_factory: Optional[Callable[[], StockApplicationService]] = None
"""Factory function for creating StockApplicationService instances."""


def set_service_factory(factory: Callable[[], StockApplicationService]) -> None:
    """Set the service factory for dependency injection."""
    global _service_factory
    _service_factory = factory


def get_stock_service() -> StockApplicationService:
    """
    Dependency function to get StockApplicationService instance.

    Returns:
        StockApplicationService instance

    Raises:
        RuntimeError: If service factory not configured
    """
    if _service_factory is None:
        raise RuntimeError("Service factory not configured")
    return _service_factory()


@router.get("", response_model=StockListResponse)
async def get_stocks(
    symbol: Annotated[
        Optional[str], Query(description="Filter by stock symbol (partial match)")
    ] = None,
    sector: Annotated[Optional[str], Query(description="Filter by sector")] = None,
    service: StockApplicationService = Depends(get_stock_service),
) -> StockListResponse:
    """
    Get list of stocks with optional filtering.

    Query parameters:
    - symbol: Filter by stock symbol (partial match, case-insensitive)
    - sector: Filter by sector

    Returns:
        StockListResponse containing filtered stocks and total count
    """
    try:
        # Check if we have any non-empty filters
        has_filters = False

        # Clean up filter values - empty strings should be None
        if symbol is not None and symbol.strip():
            symbol = symbol.strip()
            has_filters = True
        else:
            symbol = None

        if sector is not None and sector.strip():
            sector = sector.strip()
            has_filters = True
        else:
            sector = None

        # Use appropriate service method based on filters
        if has_filters:
            # Use search_stocks with filters
            # Note: sector parameter maps to industry_filter in the service
            stock_dtos = service.search_stocks(
                symbol_filter=symbol,
                name_filter=None,  # Not exposed in API
                industry_filter=sector,  # Sector maps to industry_filter
            )
        else:
            # No filters - get all stocks
            stock_dtos = service.get_all_stocks()

        # Convert DTOs to response model
        return StockListResponse.from_dto_list(stock_dtos)

    except Exception as e:
        logger.error(f"Error retrieving stocks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve stocks",
        ) from e


@router.get("/{stock_id}", response_model=StockResponse)
async def get_stock_by_id(
    stock_id: str,
    service: StockApplicationService = Depends(get_stock_service),
) -> StockResponse:
    """
    Get a specific stock by its ID.

    Args:
        stock_id: The unique identifier of the stock

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
            logger.warning(f"Stock with ID {stock_id} not found")
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
        logger.error(f"Error retrieving stock {stock_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve stock",
        ) from e
