"""
Stock page coordinator for presentation layer.

Provides data-focused operations for stock management, designed to work
with any UI framework through clean data interfaces.
"""

import logging
from typing import Any, Dict, List, Optional

from src.presentation.adapters.stock_presentation_adapter import (
    StockPresentationAdapter,
)
from src.presentation.controllers.stock_controller import StockController
from src.presentation.view_models.stock_view_models import (
    StockViewModel,
    ValidationErrorResponse,
)

logger = logging.getLogger(__name__)


class StockPageCoordinator:
    """
    Provides data-focused operations for stock management.

    Returns structured data instead of performing UI operations,
    enabling integration with any UI framework.
    """

    def __init__(
        self,
        controller: StockController,
        presentation_adapter: Optional[StockPresentationAdapter] = None,
    ):
        """
        Initialize coordinator with controller and adapter.

        Args:
            controller: Stock controller for business logic
            presentation_adapter: Framework-agnostic presentation adapter
        """
        self.controller = controller
        self.presentation_adapter = presentation_adapter

    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get dashboard data without performing UI operations.

        Returns:
            Dictionary containing dashboard data structure
        """
        try:
            # Get stock data from controller
            stock_response = self.controller.get_stock_list()

            stocks = []
            if stock_response.success and stock_response.stocks:
                stocks = stock_response.stocks

            # Calculate metrics
            metrics = self.calculate_stock_metrics(stocks)

            # Define tabs configuration
            tabs_config = ["All Stocks", "By Grade", "Add Stock"]

            return {
                "stocks": stocks,
                "metrics": metrics,
                "tabs_config": tabs_config,
                "success": stock_response.success,
                "message": (
                    stock_response.message
                    if hasattr(stock_response, "message")
                    else None
                ),
            }

        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {
                "stocks": [],
                "metrics": self.calculate_stock_metrics([]),
                "tabs_config": ["All Stocks", "By Grade", "Add Stock"],
                "success": False,
                "message": "An unexpected error occurred while loading dashboard data",
            }

    def get_stock_management_data(self, action: str) -> Dict[str, Any]:
        """
        Get stock management data without performing UI operations.

        Args:
            action: The action to perform (list, create, search)

        Returns:
            Dictionary containing management data structure
        """
        try:
            navigation_options = ["list", "create", "search"]

            # Route to appropriate data based on action
            data: Any
            if action == "list":
                stock_response = self.controller.get_stock_list()
                data = stock_response.stocks if stock_response.success else []

            elif action == "create":
                # For create action, return empty form data structure
                data = {
                    "form_fields": [
                        "symbol",
                        "name",
                        "sector",
                        "industry_group",
                        "grade",
                        "notes",
                    ],
                    "validation_rules": {
                        "symbol": "required|max:5|alpha",
                        "name": "required|max:200",
                        "grade": "in:A,B,C",
                    },
                }

            elif action == "search":
                # For search action, return search form structure
                data = {
                    "search_fields": ["symbol", "name", "sector", "grade"],
                    "filter_options": {
                        "grade": ["A", "B", "C"],
                        "sector": [],  # Would be populated from existing stocks
                    },
                }

            else:
                # Default to list action
                stock_response = self.controller.get_stock_list()
                data = stock_response.stocks if stock_response.success else []

            return {
                "action": action,
                "data": data,
                "navigation_options": navigation_options,
                "success": True,
            }

        except Exception as e:
            logger.error(f"Error getting stock management data: {e}")
            return {
                "action": action,
                "data": [],
                "navigation_options": ["list", "create", "search"],
                "success": False,
                "message": "An unexpected error occurred while loading management data",
            }

    def get_stock_detail_data(self, symbol: str) -> Dict[str, Any]:
        """
        Get stock detail data without performing UI operations.

        Args:
            symbol: Stock symbol to get details for

        Returns:
            Dictionary containing stock detail data structure
        """
        try:
            # Get stock detail from controller
            detail_response = self.controller.get_stock_by_symbol(symbol)

            # Handle validation errors
            if isinstance(detail_response, ValidationErrorResponse):
                return {
                    "stock": None,
                    "sections": [],
                    "success": False,
                    "message": detail_response.message,
                }

            # Handle unsuccessful responses
            if not detail_response.success:
                return {
                    "stock": None,
                    "sections": [],
                    "success": False,
                    "message": detail_response.message,
                }

            stock = detail_response.stock

            # Handle case where stock is None (shouldn't happen with successful response)
            if stock is None:
                return {
                    "stock": None,
                    "sections": [],
                    "success": False,
                    "message": "Stock data is missing",
                }

            # Define detail sections
            sections = {
                "basic_info": {
                    "title": "Basic Information",
                    "fields": ["symbol", "name", "sector", "industry_group", "grade"],
                },
                "additional_info": {
                    "title": "Additional Information",
                    "fields": ["id", "display_name", "is_high_grade", "has_notes"],
                },
                "notes": {
                    "title": "Notes",
                    "content": stock.notes if stock.notes else "",
                    "expanded": stock.has_notes,
                },
            }

            return {
                "stock": stock,
                "sections": sections,
                "success": True,
                "message": detail_response.message,
            }

        except Exception as e:
            logger.error(f"Error getting stock detail data: {e}")
            return {
                "stock": None,
                "sections": {},
                "success": False,
                "message": "An unexpected error occurred while loading stock details",
            }

    def calculate_stock_metrics(self, stocks: List[StockViewModel]) -> Dict[str, Any]:
        """Calculate summary metrics for stock list."""
        total_stocks = len(stocks)
        grade_counts = {"A": 0, "B": 0, "C": 0}
        for stock in stocks:
            grade_value = stock.grade if stock.grade else "Ungraded"
            if grade_value in grade_counts:
                grade_counts[grade_value] += 1

        high_grade_percentage = (
            (grade_counts["A"] / total_stocks * 100) if total_stocks > 0 else 0
        )
        return {
            "total_stocks": total_stocks,
            "grade_a_count": grade_counts["A"],
            "grade_b_count": grade_counts["B"],
            "grade_c_count": grade_counts["C"],
            "high_grade_percentage": high_grade_percentage,
        }
