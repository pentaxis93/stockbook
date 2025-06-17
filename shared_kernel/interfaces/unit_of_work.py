"""
Unit of Work interface for the shared kernel.

Provides foundational transaction management pattern that all bounded contexts
can implement for consistent data persistence and rollback behavior.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, TypeVar

Self = TypeVar("Self", bound="IUnitOfWork")


class IUnitOfWork(ABC):
    """
    Abstract interface for Unit of Work pattern.

    Defines the contract for transaction management that ensures
    data consistency across repository operations.
    """

    @abstractmethod
    def __enter__(self) -> Self:
        """
        Enter the unit of work context.

        Returns:
            Self for use in context manager
        """
        pass

    @abstractmethod
    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> Optional[bool]:
        """
        Exit the unit of work context.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred

        Returns:
            Optional[bool]: True to suppress exceptions, False or None to propagate them
        """
        pass

    @abstractmethod
    def commit(self) -> None:
        """
        Commit all changes made during this unit of work.

        Raises:
            Exception: If commit fails for any reason
        """
        pass

    @abstractmethod
    def rollback(self) -> None:
        """
        Rollback all changes made during this unit of work.

        This should restore the system to the state it was in
        before this unit of work began.
        """
        pass
