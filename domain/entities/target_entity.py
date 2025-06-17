"""
Target aggregate root entity.

Placeholder implementation for target domain entity to replace 
legacy Pydantic model dependency in repository interfaces.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional

from shared_kernel.value_objects import Money


@dataclass
class TargetEntity:
    """
    Target aggregate root representing investment goals or price targets.
    
    TODO: Implement full domain entity with business logic, validation,
    and rich behavior. This is currently a placeholder to remove 
    legacy model dependencies from repository interfaces.
    """
    
    # Identity
    id: Optional[int] = None
    
    # Core attributes
    portfolio_id: int = 0
    stock_id: int = 0
    target_type: str = ""  # 'price', 'percentage', etc.
    target_value: Optional[Money] = None
    status: str = "active"  # 'active', 'hit', 'failed', 'cancelled'
    created_date: Optional[date] = None
    target_date: Optional[date] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        """Validate target data after initialization."""
        if not self.target_type:
            raise ValueError("Target type cannot be empty")
        
        if self.status not in ['active', 'hit', 'failed', 'cancelled']:
            raise ValueError("Invalid target status")
        
        if self.portfolio_id <= 0:
            raise ValueError("Portfolio ID must be positive")
        
        if self.stock_id <= 0:
            raise ValueError("Stock ID must be positive")
    
    def __str__(self) -> str:
        """String representation."""
        return f"Target({self.target_type}: {self.target_value}, status={self.status})"
    
    def __repr__(self) -> str:
        """Developer representation."""
        return f"TargetEntity(id={self.id}, type='{self.target_type}', status='{self.status}')"