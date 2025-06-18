"""
Value objects for the StockBook domain.

Value objects are immutable objects that represent concepts
through their attributes rather than identity.

Note: Money and Quantity have been moved to shared_kernel.value_objects
to avoid duplication and provide consistent behavior across all domains.
"""

from .stock_symbol import StockSymbol
from .company_name import CompanyName
from .industry_group import IndustryGroup
from .notes import Notes

__all__ = ["StockSymbol", "CompanyName", "IndustryGroup", "Notes"]
