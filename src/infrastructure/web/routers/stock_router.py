"""
Stock router for FastAPI endpoints.

Provides RESTful API endpoints for stock operations, handling
HTTP requests/responses and coordinating with application services.
"""

from typing import Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from dependency_injection.composition_root import CompositionRoot
from dependency_injection.di_container import DIContainer
from src.application.commands.stock_commands import CreateStockCommand
from src.application.services.stock_application_service import StockApplicationService
from src.domain.services.exceptions import DomainServiceError
from src.infrastructure.web.mappers.stock_mappers import (
    entity_list_to_response_list,
)
from src.infrastructure.web.models.stock_models import (
    StockListResponse,
    StockRequest,
    StockResponse,
)

# Create router instance
router = APIRouter(prefix="/stocks", tags=["stocks"])

# Global container instance for dependency injection
_container: Optional[DIContainer] = None


def get_container() -> DIContainer:
    """Get the configured dependency injection container."""
    global _container
    if _container is None:
        _container = CompositionRoot.configure()
    return _container


def get_stock_service() -> StockApplicationService:
    """
    Dependency to get stock application service.

    Returns:
        StockApplicationService: Configured stock service instance
    """
    container = get_container()
    return container.resolve(StockApplicationService)


def reset_container() -> None:
    """Reset the container for testing purposes."""
    global _container
    _container = None


@router.get("", response_model=StockListResponse)
async def get_stocks(
    symbol: Optional[str] = Query(None, description="Filter by stock symbol"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    grade: Optional[str] = Query(None, description="Filter by grade"),
    stock_service: StockApplicationService = Depends(get_stock_service),
) -> StockListResponse:
    """
    Get list of stocks with optional filtering.

    Args:
        symbol: Optional stock symbol filter
        sector: Optional sector filter
        grade: Optional grade filter
        stock_service: Injected stock application service

    Returns:
        StockListResponse: List of stocks matching filters

    Raises:
        HTTPException: If service operation fails
    """
    try:
        # Create search request based on query parameters
        search_request = {}
        if symbol:
            search_request["symbol"] = symbol
        if sector:
            search_request["sector"] = sector
        if grade:
            search_request["grade"] = grade

        # Get stocks from service
        if search_request:
            # Use search if filters provided
            # For now, get all stocks - search implementation can be added later
            result = stock_service.get_all_stocks()
        else:
            result = stock_service.get_all_stocks()

        # Convert DTO list to API response
        # result is List[StockDto] from the application service
        if result:
            # Convert DTOs to entities for the mapper
            from src.domain.entities.stock_entity import StockEntity
            from src.domain.value_objects import (
                CompanyName,
                Grade,
                IndustryGroup,
                Notes,
                Sector,
                StockSymbol,
            )

            entities: list[StockEntity] = []
            for dto in result:
                entity = StockEntity(
                    id=dto.id,
                    symbol=StockSymbol(dto.symbol),
                    company_name=CompanyName(dto.name),
                    sector=Sector(dto.sector) if dto.sector else None,
                    industry_group=(
                        IndustryGroup(dto.industry_group)
                        if dto.industry_group
                        else None
                    ),
                    grade=Grade(dto.grade) if dto.grade else None,
                    notes=Notes(dto.notes) if dto.notes else Notes(""),
                )
                entities.append(entity)

            return entity_list_to_response_list(entities)
        else:
            return StockListResponse(stocks=[], total=0)

    except DomainServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": str(e), "code": "DOMAIN_ERROR"},
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error", "code": "INTERNAL_ERROR"},
        ) from e


@router.post("", response_model=StockResponse, status_code=status.HTTP_201_CREATED)
async def create_stock(
    stock_request: StockRequest,
    stock_service: StockApplicationService = Depends(get_stock_service),
) -> Union[StockResponse, JSONResponse]:
    """
    Create a new stock.

    Args:
        stock_request: Stock creation request data
        stock_service: Injected stock application service

    Returns:
        StockResponse: Created stock data

    Raises:
        HTTPException: If validation fails or stock already exists
    """
    try:
        # Create command from API request
        command = CreateStockCommand(
            symbol=stock_request.symbol,
            name=stock_request.name,
            sector=stock_request.sector,
            industry_group=stock_request.industry_group,
            grade=stock_request.grade,
            notes=stock_request.notes or "",
        )

        # Create stock through application service
        stock_dto = stock_service.create_stock(command)

        # Convert DTO directly to API response
        response = StockResponse(
            id=stock_dto.id or "",  # Provide empty string if no ID
            symbol=stock_dto.symbol,
            name=stock_dto.name,
            sector=stock_dto.sector,
            industry_group=stock_dto.industry_group,
            grade=stock_dto.grade,
            notes=stock_dto.notes,
        )

        return response

    except ValueError as e:
        # Handle validation errors from value objects and business logic
        error_message = str(e).lower()
        if "already exists" in error_message:
            # This is a business rule violation, not a validation error
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": str(e),
                    "code": "DUPLICATE_STOCK",
                },
            )
        else:
            # This is a true validation error
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"message": str(e), "code": "VALIDATION_ERROR"},
            ) from e
    except DomainServiceError as e:
        # Handle domain service errors (like duplicate stock)
        if "already exists" in str(e).lower():
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message": str(e),
                    "code": "DUPLICATE_STOCK",
                },
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": str(e), "code": "DOMAIN_ERROR"},
            ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error", "code": "INTERNAL_ERROR"},
        ) from e
