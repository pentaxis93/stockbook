"""
Tests for stock mappers converting between domain entities and Pydantic models.

Following TDD principles - these tests define the expected behavior
before implementation.
"""

from src.domain.entities.stock_entity import StockEntity
from src.domain.value_objects import (
    CompanyName,
    Grade,
    IndustryGroup,
    Notes,
    Sector,
    StockSymbol,
)
from src.infrastructure.web.models.stock_models import StockRequest


class TestStockEntityToResponse:
    """Test suite for converting StockEntity to StockResponse."""

    def test_entity_to_response_with_full_data(self) -> None:
        """Test converting StockEntity with all fields to StockResponse."""
        # This test will fail until we implement the mapper
        from src.infrastructure.web.mappers.stock_mappers import entity_to_response

        # Create a stock entity with all fields
        entity = StockEntity(
            id="stock-123",
            symbol=StockSymbol("AAPL"),
            company_name=CompanyName("Apple Inc."),
            sector=Sector("Technology"),
            industry_group=IndustryGroup("Software"),
            grade=Grade("A"),
            notes=Notes("High quality tech stock"),
        )

        # Convert to response
        response = entity_to_response(entity)

        # Verify all fields are correctly mapped
        assert response.id == "stock-123"
        assert response.symbol == "AAPL"
        assert response.name == "Apple Inc."
        assert response.sector == "Technology"
        assert response.industry_group == "Software"
        assert response.grade == "A"
        assert response.notes == "High quality tech stock"

    def test_entity_to_response_with_minimal_data(self) -> None:
        """Test converting StockEntity with minimal fields to StockResponse."""
        from src.infrastructure.web.mappers.stock_mappers import entity_to_response

        # Create entity with only required fields
        entity = StockEntity(
            id="stock-456",
            symbol=StockSymbol("GOOGL"),
            company_name=CompanyName("Google Inc."),
            sector=None,
            industry_group=None,
            grade=None,
            notes=Notes(""),
        )

        # Convert to response
        response = entity_to_response(entity)

        # Verify minimal fields are correctly mapped
        assert response.id == "stock-456"
        assert response.symbol == "GOOGL"
        assert response.name == "Google Inc."
        assert response.sector is None
        assert response.industry_group is None
        assert response.grade is None
        assert response.notes == ""

    def test_entity_to_response_without_id(self) -> None:
        """Test converting StockEntity without ID to StockResponse."""
        from src.infrastructure.web.mappers.stock_mappers import entity_to_response

        # Create entity without ID
        entity = StockEntity(
            symbol=StockSymbol("MSFT"),
            company_name=CompanyName("Microsoft Corp."),
            sector=Sector("Technology"),
            industry_group=None,
            grade=Grade("B"),
            notes=Notes("Good stock"),
        )

        # Convert to response
        response = entity_to_response(entity)

        # Verify ID is generated or handled appropriately
        assert (
            response.id is not None
        )  # Should have some ID (generated or from entity.id)
        assert response.symbol == "MSFT"
        assert response.name == "Microsoft Corp."
        assert response.sector == "Technology"
        assert response.industry_group is None
        assert response.grade == "B"
        assert response.notes == "Good stock"


class TestStockRequestToEntity:
    """Test suite for converting StockRequest to StockEntity."""

    def test_request_to_entity_with_full_data(self) -> None:
        """Test converting StockRequest with all fields to StockEntity."""
        # This test will fail until we implement the mapper
        from src.infrastructure.web.mappers.stock_mappers import request_to_entity

        # Create request with all fields
        request = StockRequest(
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="High quality tech stock",
        )

        # Convert to entity
        entity = request_to_entity(request)

        # Verify all fields are correctly converted to value objects
        assert entity.symbol.value == "AAPL"
        assert entity.company_name.value == "Apple Inc."
        assert entity.sector is not None
        assert entity.sector.value == "Technology"
        assert entity.industry_group is not None
        assert entity.industry_group.value == "Software"
        assert entity.grade is not None
        assert entity.grade.value == "A"
        assert entity.notes.value == "High quality tech stock"
        assert entity.id is not None  # Should have auto-generated ID
        assert len(entity.id) > 0  # Should be a valid ID

    def test_request_to_entity_with_minimal_data(self) -> None:
        """Test converting StockRequest with minimal fields to StockEntity."""
        from src.infrastructure.web.mappers.stock_mappers import request_to_entity

        # Create request with only required fields
        request = StockRequest(
            symbol="GOOGL",
            name="Google Inc.",
            sector=None,
            industry_group=None,
            grade=None,
            notes="",
        )

        # Convert to entity
        entity = request_to_entity(request)

        # Verify minimal fields are correctly converted
        assert entity.symbol.value == "GOOGL"
        assert entity.company_name.value == "Google Inc."
        assert entity.sector is None
        assert entity.industry_group is None
        assert entity.grade is None
        assert entity.notes.value == ""
        assert entity.id is not None  # Should have auto-generated ID
        assert len(entity.id) > 0  # Should be a valid ID

    def test_request_to_entity_symbol_normalization(self) -> None:
        """Test that StockRequest symbol is properly normalized in entity conversion."""
        from src.infrastructure.web.mappers.stock_mappers import request_to_entity

        # Create request with lowercase symbol
        request = StockRequest(
            symbol="msft",  # Will be normalized to uppercase
            name="Microsoft Corp.",
            sector=None,
            industry_group=None,
            grade=None,
            notes="",
        )

        # Convert to entity
        entity = request_to_entity(request)

        # Verify symbol is normalized to uppercase
        assert entity.symbol.value == "MSFT"


class TestStockEntityListToResponseList:
    """Test suite for converting list of StockEntities to StockListResponse."""

    def test_entity_list_to_response_list(self) -> None:
        """Test converting list of StockEntities to StockListResponse."""
        from src.infrastructure.web.mappers.stock_mappers import (
            entity_list_to_response_list,
        )

        # Create list of entities
        entities = [
            StockEntity(
                id="stock-1",
                symbol=StockSymbol("AAPL"),
                company_name=CompanyName("Apple Inc."),
                sector=Sector("Technology"),
                industry_group=None,
                grade=Grade("A"),
                notes=Notes("Tech stock"),
            ),
            StockEntity(
                id="stock-2",
                symbol=StockSymbol("GOOGL"),
                company_name=CompanyName("Google Inc."),
                sector=None,
                industry_group=None,
                grade=None,
                notes=Notes(""),
            ),
        ]

        # Convert to response list
        response_list = entity_list_to_response_list(entities)

        # Verify list response structure
        assert len(response_list.stocks) == 2
        assert response_list.total == 2

        # Verify first stock
        # pylint: disable=unsubscriptable-object
        first_stock = response_list.stocks[0]
        assert first_stock.id == "stock-1"
        assert first_stock.symbol == "AAPL"
        assert first_stock.name == "Apple Inc."
        assert first_stock.sector == "Technology"
        assert first_stock.grade == "A"

        # Verify second stock
        # pylint: disable=unsubscriptable-object
        second_stock = response_list.stocks[1]
        assert second_stock.id == "stock-2"
        assert second_stock.symbol == "GOOGL"
        assert second_stock.name == "Google Inc."
        assert second_stock.sector is None
        assert second_stock.grade is None

    def test_empty_entity_list_to_response_list(self) -> None:
        """Test converting empty list of StockEntities to StockListResponse."""
        from src.infrastructure.web.mappers.stock_mappers import (
            entity_list_to_response_list,
        )

        # Convert empty list
        response_list = entity_list_to_response_list([])

        # Verify empty response structure
        assert len(response_list.stocks) == 0
        assert response_list.total == 0


class TestStockRequestToEntityWithId:
    """Test suite for converting StockRequest to existing StockEntity (updates)."""

    def test_request_to_entity_with_id_for_update(self) -> None:
        """Test converting StockRequest to StockEntity with specific ID for updates."""
        from src.infrastructure.web.mappers.stock_mappers import (
            request_to_entity_with_id,
        )

        # Create request
        request = StockRequest(
            symbol="AAPL",
            name="Apple Inc. Updated",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="Updated notes",
        )

        # Convert to entity with specific ID
        entity = request_to_entity_with_id(request, "existing-stock-123")

        # Verify entity has the specified ID
        assert entity.id == "existing-stock-123"
        assert entity.symbol.value == "AAPL"
        assert entity.company_name.value == "Apple Inc. Updated"
        assert entity.sector is not None
        assert entity.sector.value == "Technology"
        assert entity.notes.value == "Updated notes"
