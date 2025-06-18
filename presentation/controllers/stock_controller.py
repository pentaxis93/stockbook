"""
Stock controller for presentation layer.

Handles stock-related user interactions, coordinating between the UI
and application services while managing validation and error handling.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from application.services.stock_application_service import \
    StockApplicationService
from presentation.view_models.stock_view_models import (
    CreateStockRequest, CreateStockResponse, StockDetailResponse,
    StockListResponse, StockSearchRequest, StockViewModel, UpdateStockRequest,
    UpdateStockResponse, ValidationErrorResponse)

logger = logging.getLogger(__name__)


class StockController:
    """
    Controller for stock-related presentation logic.

    Coordinates between UI interactions and application services,
    handling validation, transformation, and error management.
    """

    def __init__(self, stock_service: StockApplicationService):
        """
        Initialize controller with application service.

        Args:
            stock_service: Application service for stock operations
        """
        self.stock_service = stock_service

    def create_stock(
        self, request: CreateStockRequest
    ) -> Union[CreateStockResponse, ValidationErrorResponse]:
        """
        Create a new stock.

        Args:
            request: Stock creation request with validation

        Returns:
            Success or error response
        """
        try:
            # Validate request
            validation_errors = request.validate()
            if validation_errors:
                return ValidationErrorResponse(validation_errors)

            # Sanitize input
            sanitized_request = request.sanitize()

            # Convert to command and call application service
            command = sanitized_request.to_command()
            stock_dto = self.stock_service.create_stock(command)

            return CreateStockResponse.success(
                stock_id=stock_dto.id,
                symbol=stock_dto.symbol,
                message="Stock created successfully",
            )

        except ValueError as e:
            logger.warning(f"Stock creation failed: {e}")
            return CreateStockResponse.error(str(e))
        except Exception as e:
            logger.error(f"Unexpected error creating stock: {e}")
            return CreateStockResponse.error(f"Unexpected error: {str(e)}")

    def get_stock_list(self) -> StockListResponse:
        """
        Retrieve list of all stocks.

        Returns:
            Stock list response with data or error
        """
        try:
            stock_dtos = self.stock_service.get_all_stocks()

            if not stock_dtos:
                return StockListResponse.success([], "No stocks found")

            stock_view_models = [StockViewModel.from_dto(dto) for dto in stock_dtos]

            return StockListResponse.success(
                stock_view_models, f"Retrieved {len(stock_view_models)} stocks"
            )

        except Exception as e:
            logger.error(f"Error retrieving stock list: {e}")
            return StockListResponse.error(str(e))

    def get_stock_by_symbol(
        self, symbol: str
    ) -> Union[StockDetailResponse, ValidationErrorResponse]:
        """
        Retrieve stock by symbol.

        Args:
            symbol: Stock symbol to search for

        Returns:
            Stock detail response or validation error
        """
        try:
            # Validate symbol format
            if not symbol or not symbol.strip():
                return ValidationErrorResponse({"symbol": "Symbol cannot be empty"})

            # Normalize symbol
            normalized_symbol = symbol.strip().upper()

            # Validate format
            if not self._is_valid_symbol_format(normalized_symbol):
                return ValidationErrorResponse(
                    {
                        "symbol": "Invalid stock symbol format. Use 1-5 uppercase letters."
                    }
                )

            # Call application service
            stock_dto = self.stock_service.get_stock_by_symbol(normalized_symbol)

            if not stock_dto:
                return StockDetailResponse.error(
                    f"Stock with symbol {normalized_symbol} not found"
                )

            stock_view_model = StockViewModel.from_dto(stock_dto)

            return StockDetailResponse.success(
                stock_view_model, "Stock retrieved successfully"
            )

        except Exception as e:
            logger.error(f"Error retrieving stock by symbol: {e}")
            return StockDetailResponse.error(str(e))

    def update_stock(
        self, request: UpdateStockRequest
    ) -> Union[UpdateStockResponse, ValidationErrorResponse]:
        """
        Update an existing stock.

        Args:
            request: Stock update request

        Returns:
            Update response or validation error
        """
        try:
            # Validate request
            validation_errors = request.validate()
            if validation_errors:
                return ValidationErrorResponse(validation_errors)

            # Check if there are any fields to update
            if not request.has_updates():
                return ValidationErrorResponse({"general": "No fields to update"})

            # Sanitize input
            sanitized_request = request.sanitize()

            # Convert to command and call application service
            command = sanitized_request.to_command()
            stock_dto = self.stock_service.update_stock(command)

            return UpdateStockResponse.success(
                stock_id=stock_dto.id,
                message="Stock updated successfully",
            )

        except ValueError as e:
            logger.warning(f"Stock update failed: {e}")
            return UpdateStockResponse.error(str(e))
        except Exception as e:
            logger.error(f"Unexpected error updating stock: {e}")
            return UpdateStockResponse.error(f"Unexpected error: {str(e)}")

    def search_stocks(
        self, search_request: StockSearchRequest
    ) -> Union[StockListResponse, ValidationErrorResponse]:
        """
        Search stocks with filters.

        Args:
            search_request: Search criteria

        Returns:
            Filtered stock list or validation error
        """
        try:
            # Validate search request
            validation_errors = search_request.validate()
            if validation_errors:
                return ValidationErrorResponse(validation_errors)

            # If no filters, return all stocks
            if not search_request.has_filters:
                return self.get_stock_list()

            # Use the comprehensive search functionality
            stock_dtos = self.stock_service.search_stocks(
                symbol_filter=search_request.symbol_filter,
                name_filter=search_request.name_filter,
                industry_filter=search_request.industry_filter,
                grade_filter=search_request.grade_filter,
            )

            stock_view_models = [StockViewModel.from_dto(dto) for dto in stock_dtos]

            # Create filter summary for response
            active_filters = search_request.active_filters
            filter_count = len(active_filters)

            if filter_count == 0:
                message = f"Retrieved {len(stock_view_models)} stocks"
            elif filter_count == 1:
                filter_name, filter_value = next(iter(active_filters.items()))
                message = f"Retrieved {len(stock_view_models)} stocks with {filter_name} containing '{filter_value}'"
            else:
                message = f"Retrieved {len(stock_view_models)} stocks matching {filter_count} filters"

            return StockListResponse.success(
                stock_view_models,
                message,
                filters_applied=active_filters,
            )

        except Exception as e:
            logger.error(f"Error searching stocks: {e}")
            return StockListResponse.error(str(e))

    def _is_valid_symbol_format(self, symbol: str) -> bool:
        """
        Validate stock symbol format.

        Args:
            symbol: Symbol to validate

        Returns:
            True if valid format
        """
        import re

        pattern = r"^[A-Z]{1,5}$"
        return bool(re.match(pattern, symbol))
