"""CompanyName value object for the StockBook domain.

Represents a company name with validation rules and immutability.
"""

from .notes import BaseTextValueObject


class CompanyName(BaseTextValueObject):
    """Value object representing a company name.

    Encapsulates validation logic for company names and ensures immutability.
    """

    MAX_LENGTH = 200

    def __init__(self, value: str):
        """Initialize CompanyName with validation.

        Args:
            value: The company name string

        Raises:
            ValueError: If name exceeds maximum length
        """
        try:
            super().__init__(value, max_length=self.MAX_LENGTH, allow_empty=True)
        except ValueError as e:
            if "cannot exceed" in str(e):
                raise ValueError(
                    f"Company name cannot exceed {self.MAX_LENGTH} characters"
                ) from e
            raise
