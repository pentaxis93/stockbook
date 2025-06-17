"""
Journal Entry entity.

Placeholder implementation for journal entry domain entity to replace 
legacy Pydantic model dependency in repository interfaces.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class JournalEntryEntity:
    """
    Journal Entry entity representing notes and observations about investments.
    
    TODO: Implement full domain entity with business logic, validation,
    and rich behavior. This is currently a placeholder to remove 
    legacy model dependencies from repository interfaces.
    """
    
    # Identity
    id: Optional[int] = None
    
    # Core attributes
    portfolio_id: Optional[int] = None
    stock_id: Optional[int] = None
    transaction_id: Optional[int] = None
    entry_date: Optional[date] = None
    entry_type: str = "note"  # 'note', 'analysis', 'trade_reason', etc.
    title: str = ""
    content: str = ""
    tags: Optional[str] = None  # Comma-separated tags
    
    def __post_init__(self):
        """Validate journal entry data after initialization."""
        if not self.title:
            raise ValueError("Journal entry title cannot be empty")
        
        if not self.content:
            raise ValueError("Journal entry content cannot be empty")
        
        if len(self.title) > 200:
            raise ValueError("Journal entry title cannot exceed 200 characters")
        
        if len(self.content) > 10000:
            raise ValueError("Journal entry content cannot exceed 10,000 characters")
    
    def __str__(self) -> str:
        """String representation."""
        return f"JournalEntry({self.title})"
    
    def __repr__(self) -> str:
        """Developer representation."""
        return f"JournalEntryEntity(id={self.id}, title='{self.title}', type='{self.entry_type}')"