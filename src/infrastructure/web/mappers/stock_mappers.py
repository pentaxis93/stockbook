"""
Stock mappers for converting between domain entities and Pydantic models.

These mappers handle the transformation between:
- StockEntity (domain) ↔ StockRequest/StockResponse (presentation)
- Value objects ↔ primitive types
"""

from typing import List

from src.domain.entities.stock_entity import StockEntity
from src.domain.value_objects import (
    CompanyName,
    Grade,
    IndustryGroup,
    Notes,
    Sector,
    StockSymbol,
)
from src.infrastructure.web.models.stock_models import (
    StockListResponse,
    StockRequest,
    StockResponse,
)


def entity_to_response(entity: StockEntity) -> StockResponse:
    """
    Convert StockEntity to StockResponse.

    Args:
        entity: Domain stock entity

    Returns:
        StockResponse: Pydantic response model
    """
    return StockResponse(
        id=entity.id or "",  # Provide empty string if no ID
        symbol=entity.symbol.value,
        name=entity.company_name.value,
        sector=entity.sector.value if entity.sector else None,
        industry_group=entity.industry_group.value if entity.industry_group else None,
        grade=entity.grade.value if entity.grade else None,
        notes=entity.notes.value,
    )


def request_to_entity(request: StockRequest) -> StockEntity:
    """
    Convert StockRequest to StockEntity.

    Args:
        request: Pydantic request model

    Returns:
        StockEntity: Domain entity
    """
    # Convert primitive types to value objects
    symbol = StockSymbol(request.symbol)
    company_name = CompanyName(request.name)

    # Handle optional fields
    sector = Sector(request.sector) if request.sector else None
    industry_group = (
        IndustryGroup(request.industry_group) if request.industry_group else None
    )
    grade = Grade(request.grade) if request.grade else None
    notes = Notes(request.notes or "")

    return StockEntity(
        symbol=symbol,
        company_name=company_name,
        sector=sector,
        industry_group=industry_group,
        grade=grade,
        notes=notes,
        id=None,  # Requests don't have IDs
    )


def request_to_entity_with_id(request: StockRequest, entity_id: str) -> StockEntity:
    """
    Convert StockRequest to StockEntity with specific ID (for updates).

    Args:
        request: Pydantic request model
        entity_id: ID to assign to the entity

    Returns:
        StockEntity: Domain entity with specified ID
    """
    # Convert primitive types to value objects
    symbol = StockSymbol(request.symbol)
    company_name = CompanyName(request.name)

    # Handle optional fields
    sector = Sector(request.sector) if request.sector else None
    industry_group = (
        IndustryGroup(request.industry_group) if request.industry_group else None
    )
    grade = Grade(request.grade) if request.grade else None
    notes = Notes(request.notes or "")

    return StockEntity(
        symbol=symbol,
        company_name=company_name,
        sector=sector,
        industry_group=industry_group,
        grade=grade,
        notes=notes,
        id=entity_id,
    )


def entity_list_to_response_list(entities: List[StockEntity]) -> StockListResponse:
    """
    Convert list of StockEntities to StockListResponse.

    Args:
        entities: List of domain stock entities

    Returns:
        StockListResponse: Pydantic list response model
    """
    stocks = [entity_to_response(entity) for entity in entities]
    return StockListResponse(
        stocks=stocks,
        total=len(entities),
    )
