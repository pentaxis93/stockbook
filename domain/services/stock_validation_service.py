"""
Stock validation service.

Provides complex business validation rules for stocks that don't naturally
belong in the StockEntity itself.
"""

from decimal import Decimal
from typing import List, Dict, Optional, Callable
from domain.entities.stock_entity import StockEntity
from domain.value_objects.money import Money
from .exceptions import ValidationError, BusinessRuleViolationError


class ValidationConfiguration:
    """Configuration for stock validation rules."""
    
    def __init__(
        self,
        min_reasonable_price: Decimal = Decimal("0.01"),
        max_reasonable_price: Decimal = Decimal("50000.00"),
        enable_grade_price_consistency_check: bool = True,
        penny_stock_threshold: Decimal = Decimal("5.00")
    ):
        self.min_reasonable_price = min_reasonable_price
        self.max_reasonable_price = max_reasonable_price
        self.enable_grade_price_consistency_check = enable_grade_price_consistency_check
        self.penny_stock_threshold = penny_stock_threshold


class ValidationSeverity:
    """Validation severity levels."""
    WARNING = "warning"
    STRICT = "strict"


class ValidationWarning:
    """Represents a validation warning."""
    
    def __init__(self, message: str, severity: str = "medium"):
        self.message = message
        self.severity = severity


class BluechipEligibilityResult:
    """Result of blue chip candidacy assessment."""
    
    def __init__(self, is_eligible: bool, reasons: List[str]):
        self.is_eligible = is_eligible
        self.reasons = reasons


class StockValidationService:
    """
    Service for complex stock validation business rules.
    
    Handles validation logic that spans multiple stock attributes
    or requires complex business rule evaluation.
    """
    
    def __init__(self, config: Optional[ValidationConfiguration] = None):
        self.config = config or ValidationConfiguration()
        self._custom_rules: Dict[str, Callable[[StockEntity], bool]] = {}
    
    def validate_price_reasonableness(self, stock: StockEntity, current_price: Money) -> None:
        """Validate that stock price is within reasonable bounds."""
        price = current_price.amount
        
        if price < self.config.min_reasonable_price:
            raise ValidationError(
                f"Stock price ${price} is unreasonably low. Minimum reasonable price is ${self.config.min_reasonable_price}",
                field="current_price",
                value=str(price)
            )
        
        if price > self.config.max_reasonable_price:
            raise ValidationError(
                f"Stock price ${price} exceeds maximum reasonable price of ${self.config.max_reasonable_price}",
                field="current_price", 
                value=str(price)
            )
    
    def validate_grade_price_consistency(self, stock: StockEntity, current_price: Optional[Money] = None) -> None:
        """Validate that stock grade is consistent with price level."""
        if not self.config.enable_grade_price_consistency_check:
            return
        
        if not current_price:
            return  # Skip validation if no price available
        
        price = current_price.amount
        grade = stock.grade
        
        # High grade stocks with very low prices should be flagged
        if grade in ["A+", "A"] and price < Decimal("1.00"):
            raise BusinessRuleViolationError(
                f"Stock grade {grade} inconsistent with price ${price}. High-grade stocks typically have higher prices.",
                rule_name="grade_price_consistency",
                context={"grade": grade, "price": str(price)}
            )
        
        # Very low grade stocks with high prices should be flagged  
        if grade in ["D", "F"] and price > Decimal("100.00"):
            raise BusinessRuleViolationError(
                f"Stock grade {grade} inconsistent with price ${price}. Low-grade stocks typically have lower prices.",
                rule_name="grade_price_consistency",
                context={"grade": grade, "price": str(price)}
            )
    
    def validate_industry_classification(self, stock: StockEntity) -> None:
        """Validate industry classification follows business rules."""
        if not stock.industry_group:
            raise ValidationError(
                "Industry classification is required",
                field="industry_group"
            )
        
        # Check for invalid characters or format
        if not stock.industry_group.replace(" ", "").replace("&", "").isalnum():
            raise ValidationError(
                f"Industry classification '{stock.industry_group}' contains invalid characters",
                field="industry_group",
                value=stock.industry_group
            )
        
        # Check length constraints
        if len(stock.industry_group) > 50:
            raise ValidationError(
                f"Industry classification too long: {len(stock.industry_group)} characters (max 50)",
                field="industry_group",
                value=stock.industry_group
            )
    
    def validate_penny_stock_rules(self, stock: StockEntity, current_price: Optional[Money] = None) -> None:
        """Apply special validation rules for penny stocks."""
        if not current_price:
            return  # Skip validation if no price available
        
        price = current_price.amount
        
        if price <= self.config.penny_stock_threshold:
            # Penny stocks cannot have highest grades
            if stock.grade in ["A+", "A"]:
                raise BusinessRuleViolationError(
                    f"Penny stock (${price}) cannot have grade {stock.grade}. Maximum grade for penny stocks is A-.",
                    rule_name="penny_stock_grade_restriction",
                    context={"price": str(price), "grade": stock.grade}
                )
    
    def is_blue_chip_candidate(self, stock: StockEntity) -> BluechipEligibilityResult:
        """Assess if stock meets blue chip criteria."""
        reasons = []
        is_eligible = True
        
        # Price criteria (simplified - normally would include market cap)
        if stock.current_price.amount < Decimal("50.00"):
            is_eligible = False
            reasons.append("Price below typical blue chip range")
        else:
            reasons.append("Price indicates large market cap potential")
        
        # Grade criteria
        if stock.grade not in ["A+", "A", "A-"]:
            is_eligible = False
            reasons.append("Grade below blue chip quality standards")
        else:
            reasons.append("High quality grade rating")
        
        # Industry criteria (blue chips typically in established industries)
        established_industries = ["Technology", "Finance", "Healthcare", "Consumer Goods", "Utilities"]
        if stock.industry_group not in established_industries:
            is_eligible = False
            reasons.append("Not in established blue chip industry")
        else:
            reasons.append("In established blue chip industry")
        
        return BluechipEligibilityResult(is_eligible, reasons)
    
    def assess_speculative_risk(self, stock: StockEntity, current_price: Optional[Money] = None) -> List[ValidationWarning]:
        """Assess and warn about speculative investment risks."""
        warnings = []
        
        if not current_price:
            return warnings  # Skip validation if no price available
        
        price = current_price.amount
        
        # Low grade with low price = high speculation
        if stock.grade in ["D", "F"] and price < Decimal("5.00"):
            warnings.append(ValidationWarning(
                "High risk speculative investment: Low grade and low price indicate significant volatility risk",
                severity="high"
            ))
        
        # Very low price regardless of grade
        if price < Decimal("1.00"):
            warnings.append(ValidationWarning(
                "Penny stock warning: Extreme price volatility and liquidity risks",
                severity="high"
            ))
        
        # Low grade with any price
        if stock.grade in ["D", "F"]:
            warnings.append(ValidationWarning(
                "Low quality rating: Fundamental business risks may be elevated",
                severity="medium"
            ))
        
        return warnings
    
    def validate_data_completeness(self, stock: StockEntity) -> None:
        """Validate that required stock data is complete."""
        if not stock.name or stock.name.strip() == "":
            raise ValidationError(
                "Stock name is required and cannot be empty",
                field="name"
            )
        
        if not stock.symbol:
            raise ValidationError(
                "Stock symbol is required",
                field="symbol"
            )
        
        if not stock.grade or stock.grade.strip() == "":
            raise ValidationError(
                "Stock grade is required",
                field="grade"
            )
    
    def validate_field_consistency(self, stock: StockEntity) -> List[ValidationWarning]:
        """Validate consistency across stock fields."""
        warnings = []
        
        # Check symbol-industry consistency (simplified heuristic)
        symbol_str = stock.symbol.value
        industry = stock.industry_group or ""
        
        if "TECH" in symbol_str.upper() and "Technology" not in industry:
            warnings.append(ValidationWarning(
                f"Symbol '{symbol_str}' suggests technology company but industry is '{industry}'"
            ))
        
        return warnings
    
    def add_custom_rule(self, rule_name: str, rule_function: Callable[[StockEntity], bool]) -> None:
        """Add a custom validation rule."""
        self._custom_rules[rule_name] = rule_function
    
    def validate_with_custom_rules(self, stock: StockEntity) -> None:
        """Apply all custom validation rules."""
        for rule_name, rule_function in self._custom_rules.items():
            try:
                if not rule_function(stock):
                    raise ValidationError(
                        f"Custom validation rule '{rule_name}' failed",
                        field="custom_rule"
                    )
            except Exception as e:
                raise ValidationError(
                    f"Custom validation rule '{rule_name}' error: {str(e)}",
                    field="custom_rule"
                )
    
    def validate(self, stock: StockEntity, severity: str = ValidationSeverity.WARNING) -> List[ValidationWarning]:
        """
        Perform comprehensive stock validation.
        
        Returns warnings for WARNING severity, raises exceptions for STRICT severity.
        """
        warnings = []
        
        try:
            # Always run core validations
            self.validate_data_completeness(stock)
            self.validate_price_reasonableness(stock)
            self.validate_industry_classification(stock)
            self.validate_grade_price_consistency(stock)
            self.validate_penny_stock_rules(stock)
            
            # Add consistency warnings
            warnings.extend(self.validate_field_consistency(stock))
            
            # Add speculative risk warnings
            warnings.extend(self.assess_speculative_risk(stock))
            
        except (ValidationError, BusinessRuleViolationError) as e:
            if severity == ValidationSeverity.STRICT:
                raise
            else:
                warnings.append(ValidationWarning(str(e), severity="high"))
        
        return warnings