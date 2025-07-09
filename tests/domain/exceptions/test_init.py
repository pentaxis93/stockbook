"""Tests for domain exceptions module exports."""

import inspect


class TestDomainExceptionsExports:
    """Test suite for domain exceptions module exports."""

    def test_base_exceptions_exported(self) -> None:
        """Test that all base exceptions are exported from src.domain.exceptions."""
        # Import the main exceptions module
        from src.domain import exceptions

        # Verify base exceptions are accessible
        assert hasattr(exceptions, "DomainError")
        assert hasattr(exceptions, "NotFoundError")
        assert hasattr(exceptions, "AlreadyExistsError")
        assert hasattr(exceptions, "BusinessRuleViolationError")

        # Verify they are the correct classes
        assert inspect.isclass(exceptions.DomainError)
        assert inspect.isclass(exceptions.NotFoundError)
        assert inspect.isclass(exceptions.AlreadyExistsError)
        assert inspect.isclass(exceptions.BusinessRuleViolationError)

        # Verify inheritance
        assert issubclass(exceptions.NotFoundError, exceptions.DomainError)
        assert issubclass(exceptions.AlreadyExistsError, exceptions.DomainError)
        assert issubclass(exceptions.BusinessRuleViolationError, exceptions.DomainError)

    def test_stock_exceptions_exported(self) -> None:
        """Test that all stock exceptions are exported."""
        from src.domain import exceptions

        # Verify stock exceptions are accessible
        assert hasattr(exceptions, "StockNotFoundError")
        assert hasattr(exceptions, "StockAlreadyExistsError")
        assert hasattr(exceptions, "InvalidStockSymbolError")
        assert hasattr(exceptions, "InvalidStockGradeError")

        # Verify they are the correct classes
        assert inspect.isclass(exceptions.StockNotFoundError)
        assert inspect.isclass(exceptions.StockAlreadyExistsError)
        assert inspect.isclass(exceptions.InvalidStockSymbolError)
        assert inspect.isclass(exceptions.InvalidStockGradeError)

        # Verify inheritance
        assert issubclass(exceptions.StockNotFoundError, exceptions.NotFoundError)
        assert issubclass(
            exceptions.StockAlreadyExistsError,
            exceptions.AlreadyExistsError,
        )
        assert issubclass(
            exceptions.InvalidStockSymbolError,
            exceptions.BusinessRuleViolationError,
        )
        assert issubclass(
            exceptions.InvalidStockGradeError,
            exceptions.BusinessRuleViolationError,
        )

    def test_portfolio_exceptions_exported(self) -> None:
        """Test that all portfolio exceptions are exported."""
        from src.domain import exceptions

        # Verify portfolio exceptions are accessible
        assert hasattr(exceptions, "PortfolioNotFoundError")
        assert hasattr(exceptions, "PortfolioAlreadyExistsError")
        assert hasattr(exceptions, "InactivePortfolioError")
        assert hasattr(exceptions, "PortfolioBalanceError")

        # Verify they are the correct classes
        assert inspect.isclass(exceptions.PortfolioNotFoundError)
        assert inspect.isclass(exceptions.PortfolioAlreadyExistsError)
        assert inspect.isclass(exceptions.InactivePortfolioError)
        assert inspect.isclass(exceptions.PortfolioBalanceError)

        # Verify inheritance
        assert issubclass(exceptions.PortfolioNotFoundError, exceptions.NotFoundError)
        assert issubclass(
            exceptions.PortfolioAlreadyExistsError,
            exceptions.AlreadyExistsError,
        )
        assert issubclass(
            exceptions.InactivePortfolioError,
            exceptions.BusinessRuleViolationError,
        )
        assert issubclass(
            exceptions.PortfolioBalanceError,
            exceptions.BusinessRuleViolationError,
        )

    def test_all_list_complete(self) -> None:
        """Test that __all__ list is complete and accurate."""
        from src.domain import exceptions

        # Expected exports
        expected_exports = {
            # Base exceptions
            "DomainError",
            "NotFoundError",
            "AlreadyExistsError",
            "BusinessRuleViolationError",
            # Stock exceptions
            "StockNotFoundError",
            "StockAlreadyExistsError",
            "InvalidStockSymbolError",
            "InvalidStockGradeError",
            # Portfolio exceptions
            "PortfolioNotFoundError",
            "PortfolioAlreadyExistsError",
            "InactivePortfolioError",
            "PortfolioBalanceError",
        }

        # Verify __all__ exists
        assert hasattr(exceptions, "__all__")

        # Verify __all__ contains all expected exports
        assert set(exceptions.__all__) == expected_exports

        # Verify all items in __all__ are actually exported
        for name in exceptions.__all__:
            assert hasattr(exceptions, name)
            assert inspect.isclass(getattr(exceptions, name))

    def test_import_from_domain_exceptions(self) -> None:
        """Test that importing from src.domain.exceptions provides all types."""
        # Test direct imports work
        from src.domain.exceptions import (
            AlreadyExistsError,
            BusinessRuleViolationError,
            DomainError,
            InactivePortfolioError,
            InvalidStockGradeError,
            InvalidStockSymbolError,
            NotFoundError,
            PortfolioAlreadyExistsError,
            PortfolioBalanceError,
            PortfolioNotFoundError,
            StockAlreadyExistsError,
            StockNotFoundError,
        )

        # Test that we can instantiate each exception
        _ = DomainError("test")
        _ = NotFoundError("Stock", "ABC")
        _ = AlreadyExistsError("Stock", "ABC")
        _ = BusinessRuleViolationError("test_rule")
        _ = StockNotFoundError("ABC")
        _ = StockAlreadyExistsError("ABC")
        _ = InvalidStockSymbolError("123")
        _ = InvalidStockGradeError("Z")
        _ = PortfolioNotFoundError("portfolio-1")
        _ = PortfolioAlreadyExistsError("My Portfolio")
        _ = InactivePortfolioError("portfolio-1")
        _ = PortfolioBalanceError("portfolio-1", 1000.0, 500.0)

    def test_exception_module_structure(self) -> None:
        """Test that the exception module structure is correct."""
        # Verify the submodules exist
        from src.domain.exceptions import base, portfolio, stock

        # Verify base module exports
        assert hasattr(base, "DomainError")
        assert hasattr(base, "NotFoundError")
        assert hasattr(base, "AlreadyExistsError")
        assert hasattr(base, "BusinessRuleViolationError")

        # Verify stock module exports
        assert hasattr(stock, "StockNotFoundError")
        assert hasattr(stock, "StockAlreadyExistsError")
        assert hasattr(stock, "InvalidStockSymbolError")
        assert hasattr(stock, "InvalidStockGradeError")

        # Verify portfolio module exports
        assert hasattr(portfolio, "PortfolioNotFoundError")
        assert hasattr(portfolio, "PortfolioAlreadyExistsError")
        assert hasattr(portfolio, "InactivePortfolioError")
        assert hasattr(portfolio, "PortfolioBalanceError")

    def test_exception_instantiation_and_messages(self) -> None:
        """Test that exceptions can be instantiated with proper messages."""
        from src.domain import exceptions

        # Test base exceptions
        error = exceptions.NotFoundError("Stock", "ABC123")
        assert str(error) == "Stock with identifier 'ABC123' not found"

        error = exceptions.AlreadyExistsError("Portfolio", "Main")
        assert str(error) == "Portfolio with identifier 'Main' already exists"

        error = exceptions.BusinessRuleViolationError(
            "max_stocks_per_portfolio",
            {"limit": 50},
        )
        assert "Business rule 'max_stocks_per_portfolio' violated" in str(error)
        assert "{'limit': 50}" in str(error)

        # Test stock exceptions
        error = exceptions.StockNotFoundError("AAPL")
        assert str(error) == "Stock with identifier 'AAPL' not found"

        error = exceptions.StockAlreadyExistsError("MSFT")
        assert str(error) == "Stock with identifier 'MSFT' already exists"

        error = exceptions.InvalidStockSymbolError("123ABC")
        assert "Business rule 'valid_stock_symbol' violated" in str(error)

        # Test portfolio exceptions
        error = exceptions.PortfolioNotFoundError("portfolio-123")
        assert str(error) == "Portfolio with identifier 'portfolio-123' not found"

        error = exceptions.InactivePortfolioError(
            "portfolio-1",
            "add_position",
            "Retired Portfolio",
        )
        assert "Business rule 'portfolio_must_be_active' violated" in str(error)

        error = exceptions.PortfolioBalanceError(
            "portfolio-1",
            1000.0,
            500.0,
            "buy_stock",
        )
        assert "Business rule 'sufficient_portfolio_balance' violated" in str(error)

    def test_no_unexpected_exports(self) -> None:
        """Test that there are no unexpected exports in the module."""
        from src.domain import exceptions

        # Get all public attributes (not starting with _)
        public_attrs = [attr for attr in dir(exceptions) if not attr.startswith("_")]

        # Expected public attributes (exceptions + submodules)
        expected_attrs = {
            # Base exceptions
            "DomainError",
            "NotFoundError",
            "AlreadyExistsError",
            "BusinessRuleViolationError",
            # Stock exceptions
            "StockNotFoundError",
            "StockAlreadyExistsError",
            "InvalidStockSymbolError",
            "InvalidStockGradeError",
            # Portfolio exceptions
            "PortfolioNotFoundError",
            "PortfolioAlreadyExistsError",
            "InactivePortfolioError",
            "PortfolioBalanceError",
            # Submodules
            "base",
            "stock",
            "portfolio",
        }

        # Verify no unexpected exports
        unexpected = set(public_attrs) - expected_attrs
        assert not unexpected, f"Unexpected exports: {unexpected}"
