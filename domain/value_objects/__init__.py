"""
Value objects for the StockBook domain.

Value objects are immutable objects that represent concepts
through their attributes rather than identity.

Note: Money and Quantity have been moved to shared_kernel.value_objects
to avoid duplication and provide consistent behavior across all domains.
"""

from .company_name import CompanyName
from .grade import Grade
from .index_change import IndexChange
from .industry_group import IndustryGroup
from .journal_content import JournalContent
from .notes import Notes
from .portfolio_name import PortfolioName
from .stock_symbol import StockSymbol
from .target_status import TargetStatus
from .transaction_type import TransactionType

__all__ = [
    "StockSymbol",
    "CompanyName",
    "IndustryGroup",
    "Notes",
    "Grade",
    "TransactionType",
    "PortfolioName",
    "TargetStatus",
    "IndexChange",
    "JournalContent",
]
