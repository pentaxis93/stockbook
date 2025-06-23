"""
Tests for Stock Data Transfer Object.

Following TDD approach - these tests define the expected behavior
of StockDto used for transferring data between layers.
"""

from unittest.mock import Mock

import pytest

from src.application.dto.stock_dto import StockDto


class TestStockDto:
    """Test suite for StockDto."""

    def test_create_stock_dto_with_valid_data(self) -> None:
        """Should create DTO with valid stock data."""
        dto = StockDto(
            id="stock-1",
            symbol="AAPL",
            name="Apple Inc.",
            sector="Technology",
            industry_group="Software",
            grade="A",
            notes="Excellent company",
        )

        assert dto.id == "stock-1"
        assert dto.symbol == "AAPL"
        assert dto.name == "Apple Inc."
        assert dto.sector == "Technology"
        assert dto.industry_group == "Software"
        assert dto.grade == "A"
        assert dto.notes == "Excellent company"

    def test_create_stock_dto_with_minimal_data(self) -> None:
        """Should create DTO with only required fields."""
        dto = StockDto(id=None, symbol="MSFT", name="Microsoft Corp.")

        assert dto.id is None
        assert dto.symbol == "MSFT"
        assert dto.name == "Microsoft Corp."
        assert dto.sector is None
        assert dto.industry_group is None
        assert dto.grade is None
        assert dto.notes == ""

    def test_stock_dto_validation_empty_symbol_raises_error(self) -> None:
        """Should raise ValueError for empty symbol."""
        with pytest.raises(ValueError, match="Symbol cannot be empty"):
            _ = StockDto(id=None, symbol="", name="Test Company")

    def test_stock_dto_validation_empty_name_raises_error(self) -> None:
        """Should raise ValueError for empty name."""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            _ = StockDto(id=None, symbol="TEST", name="")

    def test_stock_dto_validation_empty_id_raises_error(self) -> None:
        """Should raise ValueError for empty string ID."""
        with pytest.raises(ValueError, match="ID must be a string"):
            _ = StockDto(id="", symbol="TEST", name="Test Company")

    def test_stock_dto_from_entity_with_valid_entity(self) -> None:
        """Should create DTO from valid StockEntity."""
        # Import here to avoid circular dependency issues in test
        from src.domain.entities.stock_entity import StockEntity

        # Create mock StockEntity with spec to make isinstance check pass
        mock_entity = Mock(spec=StockEntity)
        mock_entity.id = "stock-1"
        mock_entity.symbol.value = "AAPL"
        mock_entity.company_name.value = "Apple Inc."
        mock_entity.sector.value = "Technology"
        mock_entity.industry_group.value = "Software"
        mock_entity.grade.value = "A"
        mock_entity.notes.value = "Test notes"

        # Mock the str() call on symbol
        mock_entity.symbol.__str__ = Mock(return_value="AAPL")

        # Mock the None checks
        mock_entity.sector = Mock()
        mock_entity.sector.value = "Technology"
        mock_entity.industry_group = Mock()
        mock_entity.industry_group.value = "Software"
        mock_entity.grade = Mock()
        mock_entity.grade.value = "A"

        dto = StockDto.from_entity(mock_entity)

        assert dto.id == "stock-1"
        assert dto.symbol == "AAPL"
        assert dto.name == "Apple Inc."
        assert dto.sector == "Technology"
        assert dto.industry_group == "Software"
        assert dto.grade == "A"
        assert dto.notes == "Test notes"

    def test_stock_dto_from_entity_with_none_optional_fields(self) -> None:
        """Should create DTO from entity with None optional fields."""
        # Import here to avoid circular dependency issues in test
        from src.domain.entities.stock_entity import StockEntity

        # Create mock StockEntity with None optional fields
        mock_entity = Mock(spec=StockEntity)
        mock_entity.id = "stock-1"
        mock_entity.symbol.value = "AAPL"
        mock_entity.company_name.value = "Apple Inc."
        mock_entity.sector = None
        mock_entity.industry_group = None
        mock_entity.grade = None
        mock_entity.notes.value = "Test notes"

        # Mock the str() call on symbol
        mock_entity.symbol.__str__ = Mock(return_value="AAPL")

        dto = StockDto.from_entity(mock_entity)

        assert dto.id == "stock-1"
        assert dto.symbol == "AAPL"
        assert dto.name == "Apple Inc."
        assert dto.sector is None
        assert dto.industry_group is None
        assert dto.grade is None
        assert dto.notes == "Test notes"

    def test_stock_dto_from_entity_with_invalid_type_raises_error(self) -> None:
        """Should raise TypeError for non-StockEntity object."""
        invalid_entity = {"id": "test", "symbol": "TEST"}

        with pytest.raises(TypeError, match="Expected StockEntity instance"):
            _ = StockDto.from_entity(invalid_entity)

    def test_stock_dto_equality_with_same_data(self) -> None:
        """Should be equal when data is the same."""
        dto1 = StockDto(id=None, symbol="AAPL", name="Apple Inc.", sector="Technology")
        dto2 = StockDto(id=None, symbol="AAPL", name="Apple Inc.", sector="Technology")

        assert dto1 == dto2

    def test_stock_dto_equality_with_different_data(self) -> None:
        """Should not be equal when data is different."""
        dto1 = StockDto(id=None, symbol="AAPL", name="Apple Inc.")
        dto2 = StockDto(id=None, symbol="MSFT", name="Microsoft Corp.")

        assert dto1 != dto2

    def test_stock_dto_equality_with_non_matching_types(self) -> None:
        """Should return False when compared with non-DTO objects."""
        dto = StockDto(id=None, symbol="AAPL", name="Apple Inc.")

        # Test against different types
        assert dto != "string"
        assert dto != 123
        assert dto != None
        assert dto != {"symbol": "AAPL"}

    def test_stock_dto_is_immutable(self) -> None:
        """DTO should be immutable after creation."""
        dto = StockDto(id=None, symbol="AAPL", name="Apple Inc.")

        with pytest.raises(
            Exception
        ):  # dataclass frozen=True raises FrozenInstanceError
            dto.symbol = "MSFT"  # type: ignore[misc]

        with pytest.raises(Exception):
            dto.name = "Microsoft"  # type: ignore[misc]

    def test_stock_dto_string_representation(self) -> None:
        """Should have meaningful string representation."""
        dto = StockDto(id=None, symbol="AAPL", name="Apple Inc.", grade="A")

        str_repr = str(dto)
        assert "StockDto" in str_repr
        assert "AAPL" in str_repr
        assert "Apple Inc." in str_repr

    def test_stock_dto_repr_representation(self) -> None:
        """Should have meaningful repr representation."""
        dto = StockDto(id=None, symbol="AAPL", name="Apple Inc.")

        repr_str = repr(dto)
        assert "StockDto" in repr_str
        assert "symbol" in repr_str
        assert "name" in repr_str

    def test_stock_dto_hash_consistency(self) -> None:
        """Should be hashable and work in sets/dicts."""
        dto1 = StockDto(id=None, symbol="AAPL", name="Apple Inc.")
        dto2 = StockDto(id=None, symbol="AAPL", name="Apple Inc.")

        # Should be able to use in sets
        dto_set = {dto1, dto2}
        assert len(dto_set) == 1  # Same data should result in one item

        # Should be able to use as dict keys
        dto_dict = {dto1: "value"}
        assert dto_dict[dto2] == "value"  # Same data should work as key
