"""Tests for stock-specific domain exceptions."""

from src.domain.exceptions.base import (
    AlreadyExistsError,
    BusinessRuleViolationError,
    NotFoundError,
)
from src.domain.exceptions.stock import (
    InvalidStockGradeError,
    InvalidStockSymbolError,
    StockAlreadyExistsError,
    StockNotFoundError,
)


class TestStockNotFoundError:
    """Test cases for StockNotFoundError."""

    def test_stock_not_found_inherits_from_not_found_error(self) -> None:
        """Test that StockNotFoundError inherits from NotFoundError."""
        exception = StockNotFoundError(identifier="AAPL")
        assert isinstance(exception, NotFoundError)
        assert isinstance(exception, Exception)

    def test_stock_not_found_with_symbol(self) -> None:
        """Test StockNotFoundError with stock symbol."""
        exception = StockNotFoundError(identifier="AAPL")
        assert exception.entity_type == "Stock"
        assert exception.identifier == "AAPL"
        assert str(exception) == "Stock with identifier 'AAPL' not found"

    def test_stock_not_found_with_id(self) -> None:
        """Test StockNotFoundError with stock ID."""
        stock_id = "550e8400-e29b-41d4-a716-446655440000"
        exception = StockNotFoundError(identifier=stock_id)
        assert exception.entity_type == "Stock"
        assert exception.identifier == stock_id
        assert str(exception) == f"Stock with identifier '{stock_id}' not found"


class TestStockAlreadyExistsError:
    """Test cases for StockAlreadyExistsError."""

    def test_stock_already_exists_inherits_from_already_exists_error(self) -> None:
        """Test that StockAlreadyExistsError inherits from AlreadyExistsError."""
        exception = StockAlreadyExistsError(symbol="AAPL")
        assert isinstance(exception, AlreadyExistsError)
        assert isinstance(exception, Exception)

    def test_stock_already_exists_with_symbol(self) -> None:
        """Test StockAlreadyExistsError with stock symbol."""
        exception = StockAlreadyExistsError(symbol="GOOGL")
        assert exception.entity_type == "Stock"
        assert exception.identifier == "GOOGL"
        assert str(exception) == "Stock with identifier 'GOOGL' already exists"

    def test_stock_already_exists_stores_symbol(self) -> None:
        """Test StockAlreadyExistsError stores symbol as attribute."""
        symbol = "MSFT"
        exception = StockAlreadyExistsError(symbol=symbol)
        assert exception.symbol == symbol


class TestInvalidStockSymbolError:
    """Test cases for InvalidStockSymbolError."""

    def test_invalid_stock_symbol_inherits_from_business_rule_violation(self) -> None:
        """Test InvalidStockSymbolError inherits from BusinessRuleViolationError."""
        exception = InvalidStockSymbolError(symbol="")
        assert isinstance(exception, BusinessRuleViolationError)
        assert isinstance(exception, Exception)

    def test_invalid_stock_symbol_empty(self) -> None:
        """Test InvalidStockSymbolError with empty symbol."""
        exception = InvalidStockSymbolError(symbol="")
        assert exception.rule == "valid_stock_symbol"
        assert exception.symbol == ""
        expected_context = {
            "symbol": "",
            "reason": "Symbol cannot be empty",
        }
        assert exception.context == expected_context
        expected_msg = (
            "Business rule 'valid_stock_symbol' violated. "
            "Context: {'symbol': '', 'reason': 'Symbol cannot be empty'}"
        )
        assert str(exception) == expected_msg

    def test_invalid_stock_symbol_too_long(self) -> None:
        """Test InvalidStockSymbolError with symbol that's too long."""
        long_symbol = "VERYLONGSYMBOL"
        exception = InvalidStockSymbolError(
            symbol=long_symbol,
            reason="Symbol exceeds maximum length of 5 characters",
        )
        assert exception.rule == "valid_stock_symbol"
        assert exception.symbol == long_symbol
        expected_context = {
            "symbol": long_symbol,
            "reason": "Symbol exceeds maximum length of 5 characters",
        }
        assert exception.context == expected_context

    def test_invalid_stock_symbol_invalid_characters(self) -> None:
        """Test InvalidStockSymbolError with invalid characters."""
        invalid_symbol = "AA@PL"
        exception = InvalidStockSymbolError(
            symbol=invalid_symbol,
            reason="Symbol contains invalid characters",
        )
        assert exception.symbol == invalid_symbol
        assert exception.context is not None
        assert exception.context["reason"] == "Symbol contains invalid characters"

    def test_invalid_stock_symbol_default_reason(self) -> None:
        """Test InvalidStockSymbolError with default reason."""
        exception = InvalidStockSymbolError(symbol="123")
        assert exception.context is not None
        assert exception.context["reason"] == "Invalid stock symbol format"


class TestInvalidStockGradeError:
    """Test cases for InvalidStockGradeError."""

    def test_invalid_stock_grade_inherits_from_business_rule_violation(self) -> None:
        """Test InvalidStockGradeError inherits from BusinessRuleViolationError."""
        exception = InvalidStockGradeError(grade="X")
        assert isinstance(exception, BusinessRuleViolationError)
        assert isinstance(exception, Exception)

    def test_invalid_stock_grade_with_grade(self) -> None:
        """Test InvalidStockGradeError with invalid grade."""
        exception = InvalidStockGradeError(grade="Z")
        assert exception.rule == "valid_stock_grade"
        assert exception.grade == "Z"
        expected_context = {
            "grade": "Z",
            "valid_grades": ["A", "B", "C", "D", "F"],
        }
        assert exception.context == expected_context
        expected_msg = (
            "Business rule 'valid_stock_grade' violated. "
            "Context: {'grade': 'Z', 'valid_grades': ['A', 'B', 'C', 'D', 'F']}"
        )
        assert str(exception) == expected_msg

    def test_invalid_stock_grade_with_custom_valid_grades(self) -> None:
        """Test InvalidStockGradeError with custom valid grades."""
        valid_grades = ["BUY", "HOLD", "SELL"]
        exception = InvalidStockGradeError(
            grade="MAYBE",
            valid_grades=valid_grades,
        )
        assert exception.grade == "MAYBE"
        assert exception.context is not None
        assert exception.context["valid_grades"] == valid_grades

    def test_invalid_stock_grade_none_value(self) -> None:
        """Test InvalidStockGradeError with None grade."""
        exception = InvalidStockGradeError(grade=None)
        assert exception.grade is None
        assert exception.context is not None
        assert exception.context["grade"] is None

    def test_invalid_stock_grade_lowercase(self) -> None:
        """Test InvalidStockGradeError with lowercase grade."""
        exception = InvalidStockGradeError(grade="a")
        assert exception.grade == "a"
        assert exception.context is not None
        assert "a" not in exception.context["valid_grades"]


class TestStockExceptionIntegration:
    """Integration tests for stock exceptions."""

    def test_all_stock_exceptions_have_consistent_behavior(self) -> None:
        """Test that all stock exceptions behave consistently."""
        not_found = StockNotFoundError(identifier="AAPL")
        already_exists = StockAlreadyExistsError(symbol="AAPL")
        invalid_symbol = InvalidStockSymbolError(symbol="")
        invalid_grade = InvalidStockGradeError(grade="X")

        # All should be exceptions
        assert isinstance(not_found, Exception)
        assert isinstance(already_exists, Exception)
        assert isinstance(invalid_symbol, Exception)
        assert isinstance(invalid_grade, Exception)

        # All should have string representations
        assert str(not_found)
        assert str(already_exists)
        assert str(invalid_symbol)
        assert str(invalid_grade)

    def test_stock_exceptions_preserve_context(self) -> None:
        """Test that stock exceptions preserve important context."""
        symbol = "TSLA"
        grade = "G"

        not_found = StockNotFoundError(identifier=symbol)
        already_exists = StockAlreadyExistsError(symbol=symbol)
        invalid_symbol = InvalidStockSymbolError(symbol=symbol, reason="Test reason")
        invalid_grade = InvalidStockGradeError(grade=grade)

        # Context should be accessible
        assert not_found.identifier == symbol
        assert already_exists.symbol == symbol
        assert invalid_symbol.symbol == symbol
        assert invalid_grade.grade == grade
