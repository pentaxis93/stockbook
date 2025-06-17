"""
Risk assessment service.

Provides comprehensive risk assessment for individual stocks and portfolios,
including various risk metrics and risk management analysis.
"""

from decimal import Decimal
from typing import List, Tuple, Dict, Optional
from domain.entities.stock_entity import StockEntity
from domain.value_objects.quantity import Quantity
from domain.value_objects.money import Money
from .exceptions import RiskAnalysisError, InsufficientDataError
from .value_objects.risk_metrics import (
    RiskProfile, RiskLevel, RiskMetrics, PortfolioRisk, ConcentrationRisk, 
    ConcentrationLevel, RiskFactor
)


class RiskAssessmentConfig:
    """Configuration for risk assessment parameters."""
    
    def __init__(
        self,
        var_confidence_level: Decimal = Decimal("0.95"),
        concentration_threshold: Decimal = Decimal("0.15"),  # 15% max per position
        high_volatility_threshold: Decimal = Decimal("0.30"),  # 30% annual volatility
        high_beta_threshold: Decimal = Decimal("1.5")
    ):
        self.var_confidence_level = var_confidence_level
        self.concentration_threshold = concentration_threshold
        self.high_volatility_threshold = high_volatility_threshold
        self.high_beta_threshold = high_beta_threshold


class RiskAssessmentService:
    """
    Service for comprehensive risk assessment of stocks and portfolios.
    
    Handles risk analysis that operates across multiple dimensions including
    volatility, concentration, correlation, and scenario analysis.
    """
    
    def __init__(self, config: Optional[RiskAssessmentConfig] = None):
        self.config = config or RiskAssessmentConfig()
    
    def assess_stock_risk(self, stock: StockEntity) -> RiskProfile:
        """Calculate overall risk level for individual stocks."""
        volatility_risk = self._assess_volatility_risk(stock)
        beta_risk = self._assess_beta_risk(stock)
        fundamental_risk = self._assess_fundamental_risk(stock)
        sector_risk = self._assess_sector_risk(stock)
        
        # Calculate overall risk score (0-100 scale)
        risk_score = self._calculate_overall_risk_score(
            volatility_risk, beta_risk, fundamental_risk, sector_risk
        )
        
        # Determine overall risk level
        overall_risk_level = self._score_to_risk_level(risk_score)
        
        # Collect risk factors
        risk_factors = self._collect_risk_factors(stock, volatility_risk, beta_risk)
        
        return RiskProfile(
            symbol=stock.symbol,
            overall_risk_level=overall_risk_level,
            volatility_risk=volatility_risk,
            beta_risk=beta_risk,
            fundamental_risk=fundamental_risk,
            sector_risk=sector_risk,
            risk_factors=risk_factors,
            risk_score=risk_score
        )
    
    def assess_portfolio_risk(self, portfolio: List[Tuple[StockEntity, Quantity]]) -> PortfolioRisk:
        """Calculate overall portfolio risk level."""
        if not portfolio:
            raise InsufficientDataError(
                "Cannot assess risk of empty portfolio",
                required_data=["portfolio_positions"],
                available_data=[]
            )
        
        # Assess individual stock risks
        individual_risks = []
        for stock, quantity in portfolio:
            risk_profile = self.assess_stock_risk(stock)
            individual_risks.append(risk_profile)
        
        # Calculate portfolio-level metrics
        portfolio_metrics = self._calculate_portfolio_risk_metrics(portfolio)
        
        # Identify concentration risks
        concentration_risks = self._identify_concentration_risks(portfolio)
        
        # Assess sector and geographic risks
        sector_risks = self._assess_portfolio_sector_risks(portfolio)
        geographic_risks = {}  # Simplified for now
        
        # Generate risk warnings and mitigation strategies
        risk_warnings = self._generate_risk_warnings(portfolio_metrics, concentration_risks)
        mitigation_strategies = self._suggest_mitigation_strategies(portfolio_metrics, concentration_risks)
        
        return PortfolioRisk(
            portfolio_metrics=portfolio_metrics,
            individual_stock_risks=individual_risks,
            sector_risks=sector_risks,
            geographic_risks=geographic_risks,
            correlation_risks=[],  # Simplified for now
            stress_test_results={},  # Simplified for now
            risk_warnings=risk_warnings,
            mitigation_strategies=mitigation_strategies
        )
    
    def _assess_volatility_risk(self, stock: StockEntity) -> RiskLevel:
        """Assess volatility-based risk."""
        volatility = getattr(stock, 'volatility', Decimal('0.2'))  # Default 20%
        
        if volatility >= Decimal('0.5'):
            return RiskLevel.VERY_HIGH
        elif volatility >= self.config.high_volatility_threshold:
            return RiskLevel.HIGH
        elif volatility >= Decimal('0.2'):
            return RiskLevel.MEDIUM
        elif volatility >= Decimal('0.1'):
            return RiskLevel.LOW
        else:
            return RiskLevel.VERY_LOW
    
    def _assess_beta_risk(self, stock: StockEntity) -> RiskLevel:
        """Assess market beta risk."""
        beta = getattr(stock, 'beta', Decimal('1.0'))  # Default market beta
        
        if beta >= Decimal('2.0'):
            return RiskLevel.VERY_HIGH
        elif beta >= self.config.high_beta_threshold:
            return RiskLevel.HIGH
        elif beta >= Decimal('1.1'):
            return RiskLevel.MEDIUM
        elif beta >= Decimal('0.8'):
            return RiskLevel.LOW
        else:
            return RiskLevel.VERY_LOW
    
    def _assess_fundamental_risk(self, stock: StockEntity) -> RiskLevel:
        """Assess fundamental business risk factors."""
        # Simplified assessment based on grade
        if stock.grade == "A":
            return RiskLevel.LOW
        elif stock.grade == "B":
            return RiskLevel.MEDIUM
        elif stock.grade == "C":
            return RiskLevel.HIGH
        else:
            return RiskLevel.MEDIUM  # Default for ungraded
    
    def _assess_sector_risk(self, stock: StockEntity) -> RiskLevel:
        """Assess sector-specific risks."""
        sector = getattr(stock, 'industry', 'Unknown')
        
        # Simplified sector risk mapping
        high_risk_sectors = ["Technology", "Biotech", "Energy"]
        low_risk_sectors = ["Utilities", "Consumer Goods"]
        
        if sector in high_risk_sectors:
            return RiskLevel.HIGH
        elif sector in low_risk_sectors:
            return RiskLevel.LOW
        else:
            return RiskLevel.MEDIUM
    
    def _calculate_overall_risk_score(
        self, 
        volatility_risk: RiskLevel, 
        beta_risk: RiskLevel, 
        fundamental_risk: RiskLevel, 
        sector_risk: RiskLevel
    ) -> Decimal:
        """Calculate weighted overall risk score."""
        risk_level_scores = {
            RiskLevel.VERY_LOW: 10,
            RiskLevel.LOW: 25,
            RiskLevel.MEDIUM: 50,
            RiskLevel.HIGH: 75,
            RiskLevel.VERY_HIGH: 90
        }
        
        # Weighted average
        weights = {
            'volatility': Decimal('0.3'),
            'beta': Decimal('0.2'),
            'fundamental': Decimal('0.3'),
            'sector': Decimal('0.2')
        }
        
        weighted_score = (
            Decimal(str(risk_level_scores[volatility_risk])) * weights['volatility'] +
            Decimal(str(risk_level_scores[beta_risk])) * weights['beta'] +
            Decimal(str(risk_level_scores[fundamental_risk])) * weights['fundamental'] +
            Decimal(str(risk_level_scores[sector_risk])) * weights['sector']
        )
        
        return weighted_score
    
    def _score_to_risk_level(self, score: Decimal) -> RiskLevel:
        """Convert numeric score to risk level."""
        if score >= 80:
            return RiskLevel.VERY_HIGH
        elif score >= 65:
            return RiskLevel.HIGH
        elif score >= 45:
            return RiskLevel.MEDIUM
        elif score >= 25:
            return RiskLevel.LOW
        else:
            return RiskLevel.VERY_LOW
    
    def _collect_risk_factors(
        self, 
        stock: StockEntity, 
        volatility_risk: RiskLevel, 
        beta_risk: RiskLevel
    ) -> List[RiskFactor]:
        """Collect specific risk factors for a stock."""
        factors = []
        
        if volatility_risk in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            factors.append(RiskFactor(
                name="High Volatility",
                description="Stock exhibits high price volatility",
                risk_level=volatility_risk,
                impact_score=Decimal('7'),
                mitigation_suggestions=["Consider position sizing", "Use stop losses"]
            ))
        
        if beta_risk in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            factors.append(RiskFactor(
                name="High Beta",
                description="Stock is more volatile than the market",
                risk_level=beta_risk,
                impact_score=Decimal('6'),
                mitigation_suggestions=["Diversify with low-beta stocks", "Monitor market conditions"]
            ))
        
        return factors
    
    def _calculate_portfolio_risk_metrics(self, portfolio: List[Tuple[StockEntity, Quantity]]) -> RiskMetrics:
        """Calculate portfolio-level risk metrics."""
        # Simplified implementation
        total_positions = len(portfolio)
        
        # Calculate weighted beta (simplified)
        weighted_beta = Decimal('1.0')  # Default
        
        # Portfolio volatility (simplified)
        portfolio_volatility = Decimal('0.2')  # Default 20%
        
        # Simple VaR calculation (5% of portfolio value)
        from .portfolio_calculation_service import PortfolioCalculationService
        calc_service = PortfolioCalculationService()
        total_value = calc_service.calculate_total_value(portfolio)
        var_95 = Money(total_value.amount * Decimal('0.05'), total_value.currency)
        cvar_95 = Money(total_value.amount * Decimal('0.08'), total_value.currency)
        
        # Determine overall risk level
        if total_positions < 5:
            overall_risk = RiskLevel.HIGH  # Concentration risk
        elif portfolio_volatility >= Decimal('0.3'):
            overall_risk = RiskLevel.HIGH
        elif portfolio_volatility >= Decimal('0.2'):
            overall_risk = RiskLevel.MEDIUM
        else:
            overall_risk = RiskLevel.LOW
        
        # Calculate concentration risks
        concentration_risks = self._identify_concentration_risks(portfolio)
        
        # Overall risk score
        risk_score = Decimal('50')  # Simplified
        
        return RiskMetrics(
            overall_risk_level=overall_risk,
            weighted_beta=weighted_beta,
            portfolio_volatility=portfolio_volatility,
            var_95_percent=var_95,
            cvar_95_percent=cvar_95,
            sharpe_ratio=None,  # Simplified
            maximum_drawdown=None,  # Simplified
            concentration_risks=concentration_risks,
            risk_score=risk_score
        )
    
    def _identify_concentration_risks(self, portfolio: List[Tuple[StockEntity, Quantity]]) -> List[ConcentrationRisk]:
        """Identify concentration risks in portfolio."""
        from .portfolio_calculation_service import PortfolioCalculationService
        calc_service = PortfolioCalculationService()
        
        position_allocations = calc_service.calculate_position_allocations(portfolio)
        concentration_risks = []
        
        for allocation in position_allocations:
            percentage = allocation.percentage / Decimal('100')  # Convert to decimal
            
            if percentage >= Decimal('0.25'):  # 25% or more
                concentration_risks.append(ConcentrationRisk(
                    type="position",
                    category=str(allocation.symbol),
                    concentration_level=ConcentrationLevel.CRITICAL,
                    percentage=allocation.percentage,
                    risk_description=f"Single position represents {allocation.percentage}% of portfolio",
                    recommended_action="Consider reducing position size"
                ))
            elif percentage >= self.config.concentration_threshold:  # 15% or more
                concentration_risks.append(ConcentrationRisk(
                    type="position",
                    category=str(allocation.symbol),
                    concentration_level=ConcentrationLevel.HIGH,
                    percentage=allocation.percentage,
                    risk_description=f"Position represents {allocation.percentage}% of portfolio",
                    recommended_action="Monitor position size"
                ))
        
        return concentration_risks
    
    def _assess_portfolio_sector_risks(self, portfolio: List[Tuple[StockEntity, Quantity]]) -> Dict[str, RiskLevel]:
        """Assess sector concentration risks."""
        from .portfolio_calculation_service import PortfolioCalculationService
        calc_service = PortfolioCalculationService()
        
        industry_allocation = calc_service.calculate_industry_allocations(portfolio)
        sector_risks = {}
        
        for sector, percentage in industry_allocation.allocations.items():
            if percentage >= Decimal('60'):
                sector_risks[sector] = RiskLevel.HIGH
            elif percentage >= Decimal('40'):
                sector_risks[sector] = RiskLevel.MEDIUM
            else:
                sector_risks[sector] = RiskLevel.LOW
        
        return sector_risks
    
    def _generate_risk_warnings(
        self, 
        portfolio_metrics: RiskMetrics, 
        concentration_risks: List[ConcentrationRisk]
    ) -> List[str]:
        """Generate risk warnings for portfolio."""
        warnings = []
        
        if portfolio_metrics.overall_risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            warnings.append("Portfolio risk level is elevated - consider risk management strategies")
        
        critical_concentrations = [r for r in concentration_risks if r.concentration_level == ConcentrationLevel.CRITICAL]
        if critical_concentrations:
            warnings.append(f"Critical concentration risk detected in {len(critical_concentrations)} positions")
        
        return warnings
    
    def _suggest_mitigation_strategies(
        self, 
        portfolio_metrics: RiskMetrics, 
        concentration_risks: List[ConcentrationRisk]
    ) -> List[str]:
        """Suggest risk mitigation strategies."""
        strategies = []
        
        if portfolio_metrics.overall_risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            strategies.append("Consider diversification across sectors and asset classes")
            strategies.append("Implement position sizing rules")
        
        if concentration_risks:
            strategies.append("Reduce position sizes for concentrated holdings")
            strategies.append("Add positions in uncorrelated assets")
        
        return strategies