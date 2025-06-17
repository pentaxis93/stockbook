"""
Comprehensive test suite for domain exceptions in shared kernel.

Tests the foundational exception hierarchy as a reusable component 
across all bounded contexts. This follows TDD approach by defining 
all expected behavior before implementation.
"""

import pytest
from shared_kernel.exceptions.domain_exceptions import (
    DomainServiceError,
    ValidationError,
    BusinessRuleViolationError,
    CalculationError,
    InsufficientDataError,
    AnalysisError
)


class TestDomainServiceError:
    """Test base DomainServiceError exception."""
    
    def test_create_basic_domain_service_error(self):
        """Should create basic domain service error with message."""
        error = DomainServiceError("Something went wrong")
        
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert isinstance(error, Exception)
    
    def test_domain_service_error_with_context(self):
        """Should create domain service error with additional context."""
        context = {"user_id": "user-123", "operation": "calculate_total"}
        error = DomainServiceError("Operation failed", context=context)
        
        assert error.message == "Operation failed"
        assert error.context == context
        assert error.get_context_value("user_id") == "user-123"
        assert error.get_context_value("non_existent") is None
        assert error.get_context_value("non_existent", "default") == "default"
    
    def test_domain_service_error_with_inner_exception(self):
        """Should create domain service error wrapping inner exception."""
        inner_exception = ValueError("Invalid input")
        error = DomainServiceError("Domain operation failed", inner_exception=inner_exception)
        
        assert error.message == "Domain operation failed"
        assert error.inner_exception == inner_exception
        assert error.__cause__ == inner_exception
    
    def test_error_serialization(self):
        """Should serialize error to dictionary."""
        context = {"field": "amount", "value": "invalid"}
        error = DomainServiceError("Test error", context=context)
        
        error_dict = error.to_dict()
        
        assert error_dict["error_type"] == "DomainServiceError"
        assert error_dict["message"] == "Test error"
        assert error_dict["context"] == context
    
    def test_error_with_error_code(self):
        """Should support error codes for categorization."""
        error = DomainServiceError("Error occurred", error_code="DOM001")
        
        assert error.error_code == "DOM001"
        assert "DOM001" in str(error)


class TestValidationError:
    """Test ValidationError for data validation failures."""
    
    def test_create_validation_error_with_field(self):
        """Should create validation error for specific field."""
        error = ValidationError("Email is required", field="email")
        
        assert error.message == "Email is required"
        assert error.field == "email"
        assert isinstance(error, DomainServiceError)
    
    def test_validation_error_with_value(self):
        """Should create validation error with invalid value."""
        error = ValidationError("Price must be positive", field="price", value=-10)
        
        assert error.message == "Price must be positive"
        assert error.field == "price"
        assert error.value == -10
    
    def test_validation_error_with_multiple_violations(self):
        """Should support multiple validation violations."""
        violations = [
            {"field": "email", "message": "Email is required"},
            {"field": "age", "message": "Age must be positive"}
        ]
        error = ValidationError("Multiple validation errors", violations=violations)
        
        assert error.violations == violations
        assert len(error.violations) == 2
    
    def test_validation_error_severity_levels(self):
        """Should support different severity levels."""
        warning = ValidationError("Data might be incomplete", severity="warning")
        error = ValidationError("Data is invalid", severity="error")
        critical = ValidationError("System constraint violated", severity="critical")
        
        assert warning.severity == "warning"
        assert error.severity == "error"
        assert critical.severity == "critical"
    
    def test_validation_error_serialization(self):
        """Should serialize validation error with all details."""
        error = ValidationError(
            "Invalid price",
            field="price",
            value=-100,
            severity="error"
        )
        
        error_dict = error.to_dict()
        
        assert error_dict["error_type"] == "ValidationError"
        assert error_dict["field"] == "price"
        assert error_dict["value"] == -100
        assert error_dict["severity"] == "error"


class TestBusinessRuleViolationError:
    """Test BusinessRuleViolationError for business logic violations."""
    
    def test_create_business_rule_violation(self):
        """Should create business rule violation with rule details."""
        error = BusinessRuleViolationError(
            "Penny stocks cannot have A+ grade",
            rule_name="penny_stock_grade_restriction"
        )
        
        assert error.message == "Penny stocks cannot have A+ grade"
        assert error.rule_name == "penny_stock_grade_restriction"
        assert isinstance(error, DomainServiceError)
    
    def test_business_rule_violation_with_context(self):
        """Should create business rule violation with business context."""
        context = {"stock_price": 0.50, "grade": "A+", "threshold": 5.00}
        error = BusinessRuleViolationError(
            "Grade too high for penny stock",
            rule_name="penny_stock_grade_restriction",
            context=context
        )
        
        assert error.rule_name == "penny_stock_grade_restriction"
        assert error.context == context
        assert error.get_context_value("stock_price") == 0.50
    
    def test_business_rule_severity(self):
        """Should support business rule violation severity."""
        warning = BusinessRuleViolationError(
            "Recommended diversification not met",
            rule_name="diversification_guideline",
            severity="warning"
        )
        
        blocking = BusinessRuleViolationError(
            "Insufficient funds",
            rule_name="account_balance_check",
            severity="blocking"
        )
        
        assert warning.severity == "warning"
        assert blocking.severity == "blocking"
    
    def test_suggested_actions(self):
        """Should provide suggested corrective actions."""
        suggestions = [
            "Reduce grade to A- or lower",
            "Increase stock price above $5.00"
        ]
        
        error = BusinessRuleViolationError(
            "Penny stock grade violation",
            rule_name="penny_stock_grade_restriction",
            suggested_actions=suggestions
        )
        
        assert error.suggested_actions == suggestions
        assert len(error.suggested_actions) == 2


class TestCalculationError:
    """Test CalculationError for mathematical operation failures."""
    
    def test_create_calculation_error(self):
        """Should create calculation error with operation details."""
        error = CalculationError(
            "Division by zero in portfolio calculation",
            calculation_type="portfolio_diversification"
        )
        
        assert error.message == "Division by zero in portfolio calculation"
        assert error.calculation_type == "portfolio_diversification"
        assert isinstance(error, DomainServiceError)
    
    def test_calculation_error_with_input_data(self):
        """Should create calculation error with problematic input data."""
        input_data = {"dividend": 100, "divisor": 0, "operation": "divide"}
        error = CalculationError(
            "Cannot divide by zero",
            calculation_type="ratio_calculation",
            input_data=input_data
        )
        
        assert error.calculation_type == "ratio_calculation"
        assert error.input_data == input_data
        assert error.input_data["divisor"] == 0
    
    def test_calculation_precision_error(self):
        """Should handle precision-related calculation errors."""
        error = CalculationError(
            "Calculation result exceeds precision limits",
            calculation_type="compound_interest",
            precision_limit=10,
            actual_precision=15
        )
        
        assert error.precision_limit == 10
        assert error.actual_precision == 15
    
    def test_calculation_overflow_error(self):
        """Should handle calculation overflow scenarios."""
        error = CalculationError(
            "Calculation result overflow",
            calculation_type="exponential_growth",
            overflow_threshold=1e10,
            attempted_result=1e15
        )
        
        assert error.overflow_threshold == 1e10
        assert error.attempted_result == 1e15


class TestInsufficientDataError:
    """Test InsufficientDataError for missing data scenarios."""
    
    def test_create_insufficient_data_error(self):
        """Should create insufficient data error with missing data details."""
        error = InsufficientDataError(
            "Cannot calculate without price data",
            required_data=["current_price", "historical_prices"]
        )
        
        assert error.message == "Cannot calculate without price data"
        assert error.required_data == ["current_price", "historical_prices"]
        assert isinstance(error, DomainServiceError)
    
    def test_insufficient_data_with_minimum_requirements(self):
        """Should specify minimum data requirements."""
        error = InsufficientDataError(
            "Insufficient historical data for analysis",
            required_data=["price_history"],
            minimum_data_points=30,
            actual_data_points=10
        )
        
        assert error.minimum_data_points == 30
        assert error.actual_data_points == 10
        assert error.data_deficit == 20
    
    def test_insufficient_data_with_data_quality(self):
        """Should handle data quality issues."""
        error = InsufficientDataError(
            "Data quality insufficient for analysis",
            required_data=["stock_prices"],
            data_quality_issues=["missing_values", "outliers", "stale_data"]
        )
        
        assert error.data_quality_issues == ["missing_values", "outliers", "stale_data"]
        assert len(error.data_quality_issues) == 3
    
    def test_data_source_specification(self):
        """Should specify which data sources are needed."""
        error = InsufficientDataError(
            "Missing market data",
            required_data=["market_prices"],
            required_data_sources=["market_feed", "historical_db"]
        )
        
        assert error.required_data_sources == ["market_feed", "historical_db"]


class TestAnalysisError:
    """Test AnalysisError for analytical operation failures."""
    
    def test_create_analysis_error(self):
        """Should create analysis error with analysis details."""
        error = AnalysisError(
            "Risk analysis failed due to insufficient correlation data",
            analysis_type="portfolio_risk_assessment"
        )
        
        assert error.message == "Risk analysis failed due to insufficient correlation data"
        assert error.analysis_type == "portfolio_risk_assessment"
        assert isinstance(error, DomainServiceError)
    
    def test_analysis_error_with_parameters(self):
        """Should create analysis error with analysis parameters."""
        parameters = {
            "time_horizon": "1_year",
            "confidence_level": 0.95,
            "method": "monte_carlo"
        }
        
        error = AnalysisError(
            "Monte Carlo simulation failed",
            analysis_type="value_at_risk",
            analysis_parameters=parameters
        )
        
        assert error.analysis_type == "value_at_risk"
        assert error.analysis_parameters == parameters
        assert error.analysis_parameters["confidence_level"] == 0.95
    
    def test_analysis_model_error(self):
        """Should handle model-specific analysis errors."""
        error = AnalysisError(
            "Model convergence failed",
            analysis_type="optimization",
            model_name="mean_reversion",
            convergence_criteria=1e-6,
            achieved_precision=1e-3
        )
        
        assert error.model_name == "mean_reversion"
        assert error.convergence_criteria == 1e-6
        assert error.achieved_precision == 1e-3
    
    def test_analysis_timeout_error(self):
        """Should handle analysis timeout scenarios."""
        error = AnalysisError(
            "Analysis timed out",
            analysis_type="complex_simulation",
            timeout_seconds=300,
            elapsed_seconds=450
        )
        
        assert error.timeout_seconds == 300
        assert error.elapsed_seconds == 450
        assert error.overtime_seconds == 150


class TestExceptionHierarchy:
    """Test exception hierarchy and inheritance."""
    
    def test_all_exceptions_inherit_from_domain_service_error(self):
        """Should all inherit from DomainServiceError."""
        validation_error = ValidationError("Test")
        business_error = BusinessRuleViolationError("Test", rule_name="test")
        calculation_error = CalculationError("Test", calculation_type="test")
        data_error = InsufficientDataError("Test", required_data=["test"])
        analysis_error = AnalysisError("Test", analysis_type="test")
        
        assert isinstance(validation_error, DomainServiceError)
        assert isinstance(business_error, DomainServiceError)
        assert isinstance(calculation_error, DomainServiceError)
        assert isinstance(data_error, DomainServiceError)
        assert isinstance(analysis_error, DomainServiceError)
    
    def test_polymorphic_exception_handling(self):
        """Should support polymorphic exception handling."""
        exceptions = [
            ValidationError("Validation failed"),
            BusinessRuleViolationError("Rule violated", rule_name="test"),
            CalculationError("Calculation failed", calculation_type="test"),
            InsufficientDataError("Data missing", required_data=["test"]),
            AnalysisError("Analysis failed", analysis_type="test")
        ]
        
        # Should all be catchable as DomainServiceError
        for exception in exceptions:
            try:
                raise exception
            except DomainServiceError as e:
                assert isinstance(e, DomainServiceError)
                assert hasattr(e, 'message')
                assert hasattr(e, 'to_dict')
    
    def test_exception_chaining_support(self):
        """Should support exception chaining."""
        try:
            # Simulate nested operation
            try:
                raise ValueError("Low-level error")
            except ValueError as e:
                raise CalculationError(
                    "High-level calculation failed",
                    calculation_type="nested_operation",
                    inner_exception=e
                ) from e
        except CalculationError as calc_error:
            assert calc_error.inner_exception is not None
            assert isinstance(calc_error.inner_exception, ValueError)
            assert calc_error.__cause__ is not None


class TestExceptionUtilities:
    """Test exception utility methods and features."""
    
    def test_error_aggregation(self):
        """Should support aggregating multiple errors."""
        errors = [
            ValidationError("Field A is invalid", field="field_a"),
            ValidationError("Field B is invalid", field="field_b"),
            BusinessRuleViolationError("Rule X violated", rule_name="rule_x")
        ]
        
        aggregated = DomainServiceError.aggregate_errors(
            "Multiple domain errors occurred",
            errors
        )
        
        assert aggregated.message == "Multiple domain errors occurred"
        assert aggregated.aggregated_errors == errors
        assert len(aggregated.aggregated_errors) == 3
    
    def test_error_severity_comparison(self):
        """Should support error severity comparison."""
        warning = ValidationError("Warning", severity="warning")
        error = ValidationError("Error", severity="error")
        critical = BusinessRuleViolationError("Critical", rule_name="test", severity="critical")
        
        # Should be orderable by severity
        errors = [critical, warning, error]
        sorted_errors = sorted(errors, key=lambda e: e.get_severity_level())
        
        assert sorted_errors[0].severity == "critical"
        assert sorted_errors[1].severity == "error"
        assert sorted_errors[2].severity == "warning"
    
    def test_error_context_merging(self):
        """Should support merging error contexts."""
        base_context = {"user_id": "user-123", "session_id": "session-456"}
        additional_context = {"operation": "calculate", "attempt": 2}
        
        error = ValidationError("Test error", context=base_context)
        error.merge_context(additional_context)
        
        assert error.get_context_value("user_id") == "user-123"
        assert error.get_context_value("operation") == "calculate"
        assert error.get_context_value("attempt") == 2
    
    def test_error_formatting_for_logging(self):
        """Should provide structured formatting for logging."""
        error = BusinessRuleViolationError(
            "Test rule violation",
            rule_name="test_rule",
            context={"value": 100, "threshold": 50}
        )
        
        log_format = error.format_for_logging()
        
        assert "BusinessRuleViolationError" in log_format
        assert "test_rule" in log_format
        assert "value: 100" in log_format
        assert "threshold: 50" in log_format