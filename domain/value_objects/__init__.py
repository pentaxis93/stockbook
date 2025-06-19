"""
Value objects for the StockBook domain.

Value objects are immutable objects that represent concepts
through their attributes rather than identity.

Note: Money and Quantity have been moved to shared_kernel.value_objects
to avoid duplication and provide consistent behavior across all domains.
"""

from .company_name import CompanyName
from .grade import Grade
from .industry_group import IndustryGroup
from .notes import Notes
from .stock_symbol import StockSymbol

__all__ = ["StockSymbol", "CompanyName", "IndustryGroup", "Notes", "Grade"]
