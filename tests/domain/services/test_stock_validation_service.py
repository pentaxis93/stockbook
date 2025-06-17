"""
Unit tests for StockValidationService.

Tests complex business validation rules that apply to stocks but don't
belong in the StockEntity itself.
"""

from decimal import Decimal

import pytest

from domain.entities.stock_entity import StockEntity
from domain.services.exceptions import (BusinessRuleViolationError,
                                        ValidationError)
# These imports now exist after implementation
from domain.services.stock_validation_service import StockValidationService
from domain.value_objects.money import Money
from domain.value_objects.stock_symbol import StockSymbol


# Test data helper
def create_test_stock(
    symbol="AAPL", name="Apple Inc.", current_price=150.00, grade="A"
):
    """Helper to create test stock entities."""
    stock = StockEntity(
        symbol=StockSymbol(symbol),
        name=name,
        industry_group="Technology",
        grade=grade,
        notes="Test stock",
    )
    # Add current_price as an attribute for testing
    stock.current_price = Money(Decimal(str(current_price)), "USD")
    stock.industry = "Technology"  # For compatibility with validation service
    return stock


class TestStockValidationService:
    """Test core stock validation business rules."""

    def test_validate_stock_symbol_uniqueness_check(self):
        """Should validate that stock symbols are unique within constraints."""
        # This would check business rules around symbol uniqueness
        # beyond just database constraints
        pass

    def test_validate_stock_price_reasonableness(self):
        """Should validate that stock prices are within reasonable ranges."""
        service = StockValidationService()
        stock = create_test_stock()
        current_price = Money(Decimal("0.001"), "USD")  # Too low

        with pytest.raises(ValidationError) as exc_info:
            service.validate_price_reasonableness(stock, current_price)
        assert "unreasonably low" in str(exc_info.value)

    def test_validate_stock_price_maximum_limit(self):
        """Should validate maximum reasonable stock price."""
        service = StockValidationService()
        stock = create_test_stock()
        current_price = Money(Decimal("100000.00"), "USD")  # Too high

        with pytest.raises(ValidationError) as exc_info:
            service.validate_price_reasonableness(stock, current_price)
        assert "exceeds maximum" in str(exc_info.value)

    def test_validate_grade_consistency_with_price(self):
        """Should validate that stock grades are consistent with prices."""
        service = StockValidationService()

        # High grade stock with very low price should be flagged
        stock = create_test_stock(grade="A")
        current_price = Money(Decimal("0.50"), "USD")

        with pytest.raises(BusinessRuleViolationError) as exc_info:
            service.validate_grade_price_consistency(stock, current_price)
        assert "inconsistent with price" in str(exc_info.value)

    def test_validate_industry_classification_rules(self):
        """Should validate industry classification business rules."""
        service = StockValidationService()

        # Create stock with invalid industry classification
        stock = StockEntity(
            symbol=StockSymbol("TEST"),
            name="Test Stock",
            industry_group="Invalid Industry Name With Special Characters!!!",
            grade="A",
        )

        with pytest.raises(ValidationError) as exc_info:
            service.validate_industry_classification(stock)
        assert "invalid characters" in str(exc_info.value)


class TestStockBusinessRules:
    """Test complex business rules that span multiple stock attributes."""

    def test_penny_stock_classification_rules(self):
        """Should apply special rules for penny stocks."""
        service = StockValidationService()
        penny_stock = create_test_stock(grade="A")
        current_price = Money(Decimal("0.25"), "USD")  # Penny stock price

        # Penny stocks should have specific grade restrictions
        with pytest.raises(BusinessRuleViolationError):
            service.validate_penny_stock_rules(penny_stock, current_price)

    def test_blue_chip_stock_validation(self):
        """Should validate blue chip stock criteria."""
        service = StockValidationService()
        blue_chip = create_test_stock(current_price=500.00, grade="A")

        result = service.is_blue_chip_candidate(blue_chip)
        assert result.is_eligible == True
        assert len(result.reasons) > 0

    def test_validate_stock_maturity_requirements(self):
        """Should validate business rules for stock maturity."""
        # service = StockValidationService()
        #
        # # Stocks should meet certain criteria to be considered mature investments
        # young_stock = create_test_stock()
        # young_stock.listing_date = datetime.now() - timedelta(days=30)  # Too new
        #
        # with pytest.raises(BusinessRuleViolationError):
        #     service.validate_investment_maturity(young_stock)
        pass

    def test_validate_speculative_investment_warnings(self):
        """Should identify and flag speculative investments."""
        service = StockValidationService()
        speculative_stock = create_test_stock(grade="C")
        current_price = Money(Decimal("0.05"), "USD")  # Low price

        warnings = service.assess_speculative_risk(speculative_stock, current_price)

        assert len(warnings) > 0
        assert any("risk" in warning.message.lower() for warning in warnings)


class TestStockDataIntegrityService:
    """Test data integrity validation for stocks."""

    def test_validate_stock_data_completeness(self):
        """Should validate that required stock data is complete."""
        service = StockValidationService()

        # Test missing name by directly setting the internal attribute
        incomplete_stock_name = create_test_stock()
        incomplete_stock_name._name = (
            ""  # Access internal attribute to bypass constructor validation
        )

        with pytest.raises(ValidationError) as exc_info:
            service.validate_data_completeness(incomplete_stock_name)
        assert "name" in str(exc_info.value).lower()

        # Test missing grade
        incomplete_stock_grade = create_test_stock()
        incomplete_stock_grade._grade = (
            ""  # Access internal attribute to bypass constructor validation
        )

        with pytest.raises(ValidationError) as exc_info:
            service.validate_data_completeness(incomplete_stock_grade)
        assert "grade" in str(exc_info.value).lower()

    def test_validate_cross_field_consistency(self):
        """Should validate consistency across stock fields."""
        service = StockValidationService()

        # Create stock with TECH in symbol but non-tech industry
        inconsistent_stock = StockEntity(
            symbol=StockSymbol("TECH"),
            name="Tech Corporation",
            grade="A",
            industry_group="Healthcare",  # Inconsistent with TECH symbol
        )
        inconsistent_stock.current_price = Money(100, "USD")

        warnings = service.validate_field_consistency(inconsistent_stock)
        assert len(warnings) > 0
        assert "TECH" in warnings[0].message

    def test_validate_historical_data_consistency(self):
        """Should validate that current data is consistent with historical patterns."""
        # service = StockValidationService()
        #
        # # Mock historical context
        # historical_context = HistoricalStockContext(
        #     symbol="AAPL",
        #     historical_price_range=(100, 200),
        #     typical_grade_range=("A-", "A+")
        # )
        #
        # current_stock = create_test_stock(current_price=50.00)  # Below historical range
        #
        # warnings = service.validate_historical_consistency(current_stock, historical_context)
        # assert any("below historical range" in w.message for w in warnings)
        pass


@pytest.mark.skip(reason="TDD - implementation pending")
class TestStockValidationServiceConfiguration:
    """Test service configuration and customization."""

    def test_configure_validation_rules(self):
        """Should allow configuring validation rule parameters."""
        # config = ValidationConfiguration(
        #     min_reasonable_price=0.01,
        #     max_reasonable_price=50000.00,
        #     enable_grade_price_consistency_check=True,
        #     penny_stock_threshold=5.00
        # )
        #
        # service = StockValidationService(config)
        # assert service.config.min_reasonable_price == Decimal("0.01")
        pass

    def test_validation_service_with_custom_rules(self):
        """Should support custom validation rules."""
        # custom_rule = lambda stock: stock.symbol.value.startswith("CUSTOM_")
        # service = StockValidationService()
        # service.add_custom_rule("custom_symbol_prefix", custom_rule)
        #
        # stock = create_test_stock(symbol="NORMAL")
        # with pytest.raises(ValidationError):
        #     service.validate_with_custom_rules(stock)
        pass

    def test_validation_severity_levels(self):
        """Should support different validation severity levels."""
        # service = StockValidationService()
        # stock = create_test_stock(current_price=0.10)  # Questionable but not invalid
        #
        # # Should pass with warning level
        # warnings = service.validate(stock, severity=ValidationSeverity.WARNING)
        # assert len(warnings) > 0
        #
        # # Should fail with strict level
        # with pytest.raises(ValidationError):
        #     service.validate(stock, severity=ValidationSeverity.STRICT)
        pass


@pytest.mark.skip(reason="TDD - implementation pending")
class TestStockValidationServiceIntegration:
    """Test integration with other domain services."""

    def test_validation_with_market_data_service(self):
        """Should integrate with market data for enhanced validation."""
        # market_service = MockMarketDataService()
        # validation_service = StockValidationService(market_data_service=market_service)
        #
        # stock = create_test_stock(current_price=100.00)
        # market_service.set_current_market_price("AAPL", 150.00)
        #
        # warnings = validation_service.validate_against_market_data(stock)
        # assert any("price deviation from market" in w.message for w in warnings)
        pass

    def test_validation_with_risk_assessment_service(self):
        """Should work with risk assessment for comprehensive validation."""
        # risk_service = MockRiskAssessmentService()
        # validation_service = StockValidationService(risk_service=risk_service)
        #
        # high_risk_stock = create_test_stock(grade="D")
        # risk_service.set_risk_level("AAPL", RiskLevel.HIGH)
        #
        # result = validation_service.validate_with_risk_assessment(high_risk_stock)
        # assert result.requires_additional_warnings == True
        pass
