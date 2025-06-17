"""
Domain exception hierarchy for the shared kernel.

Provides foundational exception types that all bounded contexts can build upon
for consistent error handling across the entire domain.
"""

from typing import Any, Dict, Optional


class DomainServiceError(Exception):
    """
    Base exception for all domain service errors.

    Provides consistent error structure with context and inner exception support
    that all domain services can use for error reporting.
    """

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        inner_exception: Optional[Exception] = None,
        error_code: Optional[str] = None,
    ):
        """
        Initialize domain service error.

        Args:
            message: Error message describing what went wrong
            context: Additional context information
            inner_exception: Wrapped exception that caused this error
            error_code: Error code for categorization
        """
        super().__init__(message)
        self._message = message
        self._context = context or {}
        self._inner_exception = inner_exception
        self._error_code = error_code
        self._aggregated_errors = []

        # Set the cause for proper exception chaining
        if inner_exception:
            self.__cause__ = inner_exception

    @property
    def message(self) -> str:
        """Get the error message."""
        return self._message

    @property
    def context(self) -> Dict[str, Any]:
        """Get the error context."""
        return self._context.copy()  # Return copy to maintain immutability

    @property
    def inner_exception(self) -> Optional[Exception]:
        """Get the wrapped inner exception."""
        return self._inner_exception

    @property
    def error_code(self) -> Optional[str]:
        """Get the error code."""
        return self._error_code

    @property
    def aggregated_errors(self) -> list:
        """Get the list of aggregated errors."""
        return self._aggregated_errors.copy()

    def get_context_value(self, key: str, default: Any = None) -> Any:
        """Get value from error context."""
        return self._context.get(key, default)

    def add_context(self, key: str, value: Any) -> None:
        """Add additional context to the error."""
        self._context[key] = value

    def merge_context(self, additional_context: Dict[str, Any]) -> None:
        """Merge additional context into existing context."""
        self._context.update(additional_context)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize error to dictionary."""
        result = {
            "error_type": self.__class__.__name__,
            "message": self._message,
            "context": self._context,
        }

        if self._error_code:
            result["error_code"] = self._error_code

        if self._aggregated_errors:
            result["aggregated_errors"] = [
                err.to_dict() if hasattr(err, "to_dict") else str(err)
                for err in self._aggregated_errors
            ]

        return result

    def format_for_logging(self) -> str:
        """Format error for structured logging."""
        parts = [f"error_type: {self.__class__.__name__}", f"message: {self._message}"]

        if self._error_code:
            parts.append(f"error_code: {self._error_code}")

        for key, value in self._context.items():
            parts.append(f"{key}: {value}")

        parts.append(f"severity: {self.get_severity_level()}")

        return ", ".join(parts)

    def get_severity_level(self) -> int:
        """Get numeric severity level for comparison."""
        return 3  # Default severity for base domain service errors

    @classmethod
    def aggregate_errors(cls, message: str, errors: list) -> "DomainServiceError":
        """Create error that aggregates multiple errors."""
        aggregated = cls(message)
        aggregated._aggregated_errors = errors.copy()
        return aggregated

    def __str__(self) -> str:
        """String representation of the error."""
        if self._error_code:
            return f"[{self._error_code}] {self._message}"
        return self._message


class ValidationError(DomainServiceError):
    """
    Exception for validation failures in domain services.

    Used when input data fails domain validation rules.
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Any = None,
        violations: Optional[list] = None,
        severity: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        inner_exception: Optional[Exception] = None,
        error_code: Optional[str] = None,
    ):
        """
        Initialize validation error.

        Args:
            message: Validation error message
            field: Name of the field that failed validation
            value: Value that failed validation
            violations: List of multiple validation violations
            severity: Severity level (warning, error, critical)
            context: Additional context information
            inner_exception: Wrapped exception that caused this error
            error_code: Error code for categorization
        """
        super().__init__(message, context, inner_exception, error_code)
        self._field = field
        self._value = value
        self._violations = violations or []
        self._severity = severity or "error"

    @property
    def field(self) -> Optional[str]:
        """Get the name of the field that failed validation."""
        return self._field

    @property
    def value(self) -> Any:
        """Get the value that failed validation."""
        return self._value

    @property
    def violations(self) -> list:
        """Get the list of validation violations."""
        return self._violations.copy()

    @property
    def severity(self) -> str:
        """Get the severity level."""
        return self._severity

    def to_dict(self) -> Dict[str, Any]:
        """Serialize validation error to dictionary."""
        result = super().to_dict()

        if self._field:
            result["field"] = self._field
        if self._value is not None:
            result["value"] = self._value
        if self._violations:
            result["violations"] = self._violations
        if self._severity:
            result["severity"] = self._severity

        return result

    def get_severity_level(self) -> int:
        """Get numeric severity level for comparison."""
        severity_levels = {
            "critical": 1,  # Highest priority (lowest number for sorting)
            "error": 2,
            "warning": 3,  # Lowest priority (highest number for sorting)
        }
        return severity_levels.get(self._severity, 2)


class BusinessRuleViolationError(DomainServiceError):
    """
    Exception for business rule violations in domain services.

    Used when operations violate domain business rules.
    """

    def __init__(
        self,
        message: str,
        rule_name: Optional[str] = None,
        severity: Optional[str] = None,
        suggested_actions: Optional[list] = None,
        context: Optional[Dict[str, Any]] = None,
        inner_exception: Optional[Exception] = None,
        error_code: Optional[str] = None,
    ):
        """
        Initialize business rule violation error.

        Args:
            message: Business rule violation message
            rule_name: Name of the violated business rule
            severity: Severity level (warning, blocking, etc.)
            suggested_actions: List of suggested corrective actions
            context: Additional context information
            inner_exception: Wrapped exception that caused this error
            error_code: Error code for categorization
        """
        super().__init__(message, context, inner_exception, error_code)
        self._rule_name = rule_name
        self._severity = severity or "blocking"
        self._suggested_actions = suggested_actions or []

    @property
    def rule_name(self) -> Optional[str]:
        """Get the name of the violated business rule."""
        return self._rule_name

    @property
    def severity(self) -> str:
        """Get the severity level."""
        return self._severity

    @property
    def suggested_actions(self) -> list:
        """Get the list of suggested corrective actions."""
        return self._suggested_actions.copy()

    def get_severity_level(self) -> int:
        """Get numeric severity level for comparison."""
        severity_levels = {
            "critical": 1,  # Highest priority (lowest number for sorting)
            "blocking": 2,
            "warning": 3,  # Lowest priority (highest number for sorting)
        }
        return severity_levels.get(self._severity, 2)

    def format_for_logging(self) -> str:
        """Format error for structured logging."""
        parts = [f"error_type: {self.__class__.__name__}", f"message: {self._message}"]

        if self._error_code:
            parts.append(f"error_code: {self._error_code}")

        if self._rule_name:
            parts.append(f"rule_name: {self._rule_name}")

        for key, value in self._context.items():
            parts.append(f"{key}: {value}")

        parts.append(f"severity: {self.get_severity_level()}")

        return ", ".join(parts)


class CalculationError(DomainServiceError):
    """
    Exception for calculation failures in domain services.

    Used when mathematical operations or calculations fail.
    """

    def __init__(
        self,
        message: str,
        calculation_type: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        precision_limit: Optional[float] = None,
        actual_precision: Optional[float] = None,
        overflow_threshold: Optional[float] = None,
        attempted_result: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None,
        inner_exception: Optional[Exception] = None,
        error_code: Optional[str] = None,
    ):
        """
        Initialize calculation error.

        Args:
            message: Calculation error message
            calculation_type: Type of calculation that failed
            input_data: Problematic input data
            precision_limit: Precision limit for calculations
            actual_precision: Actual precision achieved
            overflow_threshold: Overflow threshold value
            attempted_result: Result that caused overflow
            context: Additional context information
            inner_exception: Wrapped exception that caused this error
            error_code: Error code for categorization
        """
        super().__init__(message, context, inner_exception, error_code)
        self._calculation_type = calculation_type
        self._input_data = input_data or {}
        self._precision_limit = precision_limit
        self._actual_precision = actual_precision
        self._overflow_threshold = overflow_threshold
        self._attempted_result = attempted_result

    @property
    def calculation_type(self) -> Optional[str]:
        """Get the type of calculation that failed."""
        return self._calculation_type

    @property
    def input_data(self) -> Dict[str, Any]:
        """Get the input data that caused the error."""
        return self._input_data.copy()

    @property
    def precision_limit(self) -> Optional[float]:
        """Get the maximum allowed precision."""
        return self._precision_limit

    @property
    def actual_precision(self) -> Optional[float]:
        """Get the actual precision achieved."""
        return self._actual_precision

    @property
    def overflow_threshold(self) -> Optional[float]:
        """Get the threshold for overflow detection."""
        return self._overflow_threshold

    @property
    def attempted_result(self) -> Optional[float]:
        """Get the result that exceeded threshold."""
        return self._attempted_result


class InsufficientDataError(DomainServiceError):
    """
    Exception for insufficient data scenarios in domain services.

    Used when operations cannot proceed due to missing required data.
    """

    def __init__(
        self,
        message: str,
        required_data: Optional[list] = None,
        minimum_data_points: Optional[int] = None,
        actual_data_points: Optional[int] = None,
        data_quality_issues: Optional[list] = None,
        required_data_sources: Optional[list] = None,
        context: Optional[Dict[str, Any]] = None,
        inner_exception: Optional[Exception] = None,
        error_code: Optional[str] = None,
    ):
        """
        Initialize insufficient data error.

        Args:
            message: Insufficient data error message
            required_data: List of required data elements
            minimum_data_points: Minimum required data points
            actual_data_points: Actual data points available
            data_quality_issues: List of data quality issues
            required_data_sources: Required data sources
            context: Additional context information
            inner_exception: Wrapped exception that caused this error
            error_code: Error code for categorization
        """
        super().__init__(message, context, inner_exception, error_code)
        self._required_data = required_data or []
        self._minimum_data_points = minimum_data_points
        self._actual_data_points = actual_data_points
        self._data_quality_issues = data_quality_issues or []
        self._required_data_sources = required_data_sources or []

    @property
    def required_data(self) -> list:
        """Get the list of required data elements."""
        return self._required_data.copy()

    @property
    def minimum_data_points(self) -> Optional[int]:
        """Get the minimum required data points."""
        return self._minimum_data_points

    @property
    def actual_data_points(self) -> Optional[int]:
        """Get the actual data points available."""
        return self._actual_data_points

    @property
    def data_deficit(self) -> Optional[int]:
        """Get the calculated deficit (minimum - actual)."""
        if (
            self._minimum_data_points is not None
            and self._actual_data_points is not None
        ):
            return max(0, self._minimum_data_points - self._actual_data_points)
        return None

    @property
    def data_quality_issues(self) -> list:
        """Get the list of data quality problems."""
        return self._data_quality_issues.copy()

    @property
    def required_data_sources(self) -> list:
        """Get the list of required data sources."""
        return self._required_data_sources.copy()


class AnalysisError(DomainServiceError):
    """
    Exception for analysis failures in domain services.

    Used when analysis operations fail due to various reasons.
    """

    def __init__(
        self,
        message: str,
        analysis_type: Optional[str] = None,
        analysis_parameters: Optional[Dict[str, Any]] = None,
        model_name: Optional[str] = None,
        convergence_criteria: Optional[float] = None,
        achieved_precision: Optional[float] = None,
        timeout_seconds: Optional[int] = None,
        elapsed_seconds: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
        inner_exception: Optional[Exception] = None,
        error_code: Optional[str] = None,
    ):
        """
        Initialize analysis error.

        Args:
            message: Analysis error message
            analysis_type: Type of analysis that failed
            analysis_parameters: Parameters used in analysis
            model_name: Name of the model used
            convergence_criteria: Required convergence criteria
            achieved_precision: Precision actually achieved
            timeout_seconds: Timeout limit in seconds
            elapsed_seconds: Actual elapsed time
            context: Additional context information
            inner_exception: Wrapped exception that caused this error
            error_code: Error code for categorization
        """
        super().__init__(message, context, inner_exception, error_code)
        self._analysis_type = analysis_type
        self._analysis_parameters = analysis_parameters or {}
        self._model_name = model_name
        self._convergence_criteria = convergence_criteria
        self._achieved_precision = achieved_precision
        self._timeout_seconds = timeout_seconds
        self._elapsed_seconds = elapsed_seconds

    @property
    def analysis_type(self) -> Optional[str]:
        """Get the type of analysis that failed."""
        return self._analysis_type

    @property
    def analysis_parameters(self) -> Dict[str, Any]:
        """Get the analysis parameters dictionary."""
        return self._analysis_parameters.copy()

    @property
    def model_name(self) -> Optional[str]:
        """Get the model name used."""
        return self._model_name

    @property
    def convergence_criteria(self) -> Optional[float]:
        """Get the required convergence criteria."""
        return self._convergence_criteria

    @property
    def achieved_precision(self) -> Optional[float]:
        """Get the achieved precision."""
        return self._achieved_precision

    @property
    def timeout_seconds(self) -> Optional[int]:
        """Get the timeout limit."""
        return self._timeout_seconds

    @property
    def elapsed_seconds(self) -> Optional[int]:
        """Get the actual elapsed time."""
        return self._elapsed_seconds

    @property
    def overtime_seconds(self) -> Optional[int]:
        """Get the calculated overtime (elapsed - timeout)."""
        if self._timeout_seconds is not None and self._elapsed_seconds is not None:
            return max(0, self._elapsed_seconds - self._timeout_seconds)
        return None
