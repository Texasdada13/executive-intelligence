"""Unified Context Builder for Cross-Product Executive Intelligence"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class HealthLevel(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


class FunctionArea(Enum):
    MARKETING = "marketing"
    SECURITY = "security"
    FINANCE = "finance"
    OPERATIONS = "operations"
    PEOPLE = "people"
    PRODUCT = "product"
    SALES = "sales"
    STRATEGY = "strategy"


@dataclass
class UnifiedHealthScore:
    """Unified health score for a business function."""
    function: FunctionArea
    score: float  # 0-100
    grade: str  # A, B, C, D, F
    level: HealthLevel
    key_metrics: Dict[str, Any] = field(default_factory=dict)
    alerts: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    last_updated: Optional[datetime] = None

    @classmethod
    def from_score(cls, function: FunctionArea, score: float, **kwargs) -> 'UnifiedHealthScore':
        """Create a health score from a numeric score."""
        grade = cls._score_to_grade(score)
        level = cls._score_to_level(score)
        return cls(
            function=function,
            score=score,
            grade=grade,
            level=level,
            **kwargs
        )

    @staticmethod
    def _score_to_grade(score: float) -> str:
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        return 'F'

    @staticmethod
    def _score_to_level(score: float) -> HealthLevel:
        if score >= 85:
            return HealthLevel.EXCELLENT
        elif score >= 70:
            return HealthLevel.GOOD
        elif score >= 55:
            return HealthLevel.FAIR
        elif score >= 40:
            return HealthLevel.POOR
        return HealthLevel.CRITICAL

    def to_dict(self) -> Dict[str, Any]:
        return {
            'function': self.function.value,
            'score': round(self.score, 1),
            'grade': self.grade,
            'level': self.level.value,
            'key_metrics': self.key_metrics,
            'alerts': self.alerts,
            'recommendations': self.recommendations,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }


@dataclass
class UnifiedExecutiveContext:
    """Aggregated context from all business functions for CEO-level insights."""
    organization_id: str
    organization_name: str
    overall_health: float
    overall_grade: str
    function_scores: Dict[FunctionArea, UnifiedHealthScore] = field(default_factory=dict)
    critical_alerts: List[Dict[str, Any]] = field(default_factory=list)
    opportunities: List[Dict[str, Any]] = field(default_factory=list)
    cross_functional_insights: List[str] = field(default_factory=list)
    generated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'organization_id': self.organization_id,
            'organization_name': self.organization_name,
            'overall_health': round(self.overall_health, 1),
            'overall_grade': self.overall_grade,
            'function_scores': {
                k.value: v.to_dict() for k, v in self.function_scores.items()
            },
            'critical_alerts': self.critical_alerts,
            'opportunities': self.opportunities,
            'cross_functional_insights': self.cross_functional_insights,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None
        }

    def to_ai_context(self) -> Dict[str, Any]:
        """Convert to format suitable for AI chat context."""
        return {
            'overall_health': self.overall_health,
            'functions': {
                k.value: {
                    'score': v.score,
                    'grade': v.grade,
                    'level': v.level.value,
                    'alerts': v.alerts[:3],  # Top 3 alerts per function
                    'key_metrics': v.key_metrics
                }
                for k, v in self.function_scores.items()
            },
            'critical_alerts': [a['message'] for a in self.critical_alerts[:5]],
            'opportunities': [o['description'] for o in self.opportunities[:3]],
            'cross_functional_insights': self.cross_functional_insights[:5]
        }


class UnifiedContextBuilder:
    """Builds unified context by aggregating data from multiple products."""

    # Weights for calculating overall health
    FUNCTION_WEIGHTS = {
        FunctionArea.MARKETING: 0.15,
        FunctionArea.SECURITY: 0.20,
        FunctionArea.FINANCE: 0.25,
        FunctionArea.OPERATIONS: 0.15,
        FunctionArea.PEOPLE: 0.10,
        FunctionArea.PRODUCT: 0.10,
        FunctionArea.STRATEGY: 0.05
    }

    def __init__(self, adapters: Dict[str, Any] = None):
        """
        Initialize with product adapters.

        Args:
            adapters: Dict of adapter instances keyed by product name
        """
        self.adapters = adapters or {}

    def build_context(
        self,
        org_id: str,
        org_name: str,
        marketing_data: Dict[str, Any] = None,
        security_data: Dict[str, Any] = None,
        executive_data: Dict[str, Any] = None
    ) -> UnifiedExecutiveContext:
        """
        Build unified executive context from multiple data sources.

        Args:
            org_id: Organization ID
            org_name: Organization name
            marketing_data: Marketing Intelligence data
            security_data: Security Intelligence data
            executive_data: Executive Intelligence internal data

        Returns:
            UnifiedExecutiveContext with aggregated insights
        """
        function_scores = {}
        critical_alerts = []
        opportunities = []
        cross_functional = []

        # Process Marketing data
        if marketing_data:
            marketing_score = self._process_marketing(marketing_data)
            function_scores[FunctionArea.MARKETING] = marketing_score
            critical_alerts.extend(self._extract_alerts(marketing_score, 'Marketing'))
            opportunities.extend(self._extract_opportunities(marketing_data, 'Marketing'))

        # Process Security data
        if security_data:
            security_score = self._process_security(security_data)
            function_scores[FunctionArea.SECURITY] = security_score
            critical_alerts.extend(self._extract_alerts(security_score, 'Security'))
            opportunities.extend(self._extract_opportunities(security_data, 'Security'))

        # Process Executive data (internal metrics)
        if executive_data:
            exec_scores = self._process_executive(executive_data)
            function_scores.update(exec_scores)
            for func, score in exec_scores.items():
                critical_alerts.extend(self._extract_alerts(score, func.value.title()))

        # Calculate overall health
        overall_health = self._calculate_overall_health(function_scores)
        overall_grade = UnifiedHealthScore._score_to_grade(overall_health)

        # Generate cross-functional insights
        cross_functional = self._generate_cross_functional_insights(
            function_scores, marketing_data, security_data, executive_data
        )

        # Sort alerts by severity
        critical_alerts.sort(key=lambda x: x.get('severity_score', 0), reverse=True)

        return UnifiedExecutiveContext(
            organization_id=org_id,
            organization_name=org_name,
            overall_health=overall_health,
            overall_grade=overall_grade,
            function_scores=function_scores,
            critical_alerts=critical_alerts[:10],  # Top 10 alerts
            opportunities=opportunities[:5],  # Top 5 opportunities
            cross_functional_insights=cross_functional,
            generated_at=datetime.utcnow()
        )

    def _process_marketing(self, data: Dict[str, Any]) -> UnifiedHealthScore:
        """Process marketing data into unified health score."""
        metrics = data.get('metrics_summary', data)

        # Calculate marketing health from key metrics
        roas = metrics.get('roas', 1)
        roi = metrics.get('roi_percentage', 0)
        health = metrics.get('health_score', 50)

        # Use provided health score or calculate from metrics
        if health == 50 and roas > 0:
            # Simple calculation if no health score provided
            health = min(100, max(0, 50 + (roas - 1) * 20 + (roi / 10)))

        alerts = []
        if roas < 1:
            alerts.append(f"ROAS is below 1 ({roas:.2f}x) - marketing spend not generating positive returns")
        if roi < 0:
            alerts.append(f"Marketing ROI is negative ({roi:.1f}%) - review channel allocation")

        recommendations = []
        if roas < 1.5:
            recommendations.append("Consider reallocating budget from underperforming channels")
        if metrics.get('avg_cac', 0) > metrics.get('customer_ltv', float('inf')) * 0.3:
            recommendations.append("CAC may be too high relative to LTV - optimize acquisition channels")

        return UnifiedHealthScore.from_score(
            function=FunctionArea.MARKETING,
            score=health,
            key_metrics={
                'roas': roas,
                'roi_percentage': roi,
                'total_spend': metrics.get('total_spend', 0),
                'total_revenue': metrics.get('total_revenue', 0),
                'active_campaigns': metrics.get('active_campaigns', 0)
            },
            alerts=alerts,
            recommendations=recommendations,
            last_updated=datetime.utcnow()
        )

    def _process_security(self, data: Dict[str, Any]) -> UnifiedHealthScore:
        """Process security data into unified health score."""
        metrics = data.get('metrics_summary', data)

        posture_score = metrics.get('posture_score', 50)
        vulns = metrics.get('vulnerabilities', {})
        critical_vulns = vulns.get('critical', 0) if isinstance(vulns, dict) else 0

        alerts = []
        if critical_vulns > 0:
            alerts.append(f"{critical_vulns} critical vulnerabilities require immediate remediation")
        if metrics.get('open_incidents', 0) > 3:
            alerts.append(f"{metrics.get('open_incidents')} open security incidents need attention")
        if metrics.get('avg_compliance_score', 100) < 70:
            alerts.append(f"Compliance score ({metrics.get('avg_compliance_score', 0):.1f}%) is below threshold")

        recommendations = []
        if critical_vulns > 0:
            recommendations.append("Prioritize patching critical vulnerabilities within SLA")
        if metrics.get('mfa_adoption', 100) < 90:
            recommendations.append(f"Increase MFA adoption from {metrics.get('mfa_adoption', 0)}% to 95%+")

        return UnifiedHealthScore.from_score(
            function=FunctionArea.SECURITY,
            score=posture_score,
            key_metrics={
                'posture_score': posture_score,
                'critical_vulnerabilities': critical_vulns,
                'open_incidents': metrics.get('open_incidents', 0),
                'compliance_score': metrics.get('avg_compliance_score', 0),
                'mttr_hours': metrics.get('mttr_hours', 0)
            },
            alerts=alerts,
            recommendations=recommendations,
            last_updated=datetime.utcnow()
        )

    def _process_executive(self, data: Dict[str, Any]) -> Dict[FunctionArea, UnifiedHealthScore]:
        """Process executive data into function health scores."""
        scores = {}
        metrics = data.get('metrics_summary', data)

        # Finance health
        financial = data.get('financial_metrics', {})
        if financial:
            finance_score = min(100, max(0,
                50 +
                financial.get('revenue_growth', 0) +
                financial.get('net_margin', 0)
            ))
            alerts = []
            runway = financial.get('runway_months')
            if runway is not None and runway < 12:
                alerts.append(f"Cash runway is {runway} months - review funding")
            if financial.get('revenue_growth', 0) < 0:
                alerts.append(f"Revenue declining at {financial.get('revenue_growth')}%")

            scores[FunctionArea.FINANCE] = UnifiedHealthScore.from_score(
                function=FunctionArea.FINANCE,
                score=finance_score,
                key_metrics={
                    'revenue_growth': financial.get('revenue_growth', 0),
                    'gross_margin': financial.get('gross_margin', 0),
                    'net_margin': financial.get('net_margin', 0),
                    'runway_months': financial.get('runway_months')
                },
                alerts=alerts,
                last_updated=datetime.utcnow()
            )

        # People health
        people = data.get('people_metrics', {})
        if people:
            people_score = min(100, max(0,
                people.get('engagement', 50) +
                (100 - people.get('turnover', 20) * 2) / 2
            ))
            alerts = []
            if people.get('engagement', 100) < 60:
                alerts.append(f"Employee engagement at {people.get('engagement')}% - retention risk")
            if people.get('turnover', 0) > 20:
                alerts.append(f"High turnover rate: {people.get('turnover')}%")

            scores[FunctionArea.PEOPLE] = UnifiedHealthScore.from_score(
                function=FunctionArea.PEOPLE,
                score=people_score,
                key_metrics={
                    'engagement': people.get('engagement', 0),
                    'turnover': people.get('turnover', 0),
                    'open_positions': people.get('open_positions', 0)
                },
                alerts=alerts,
                last_updated=datetime.utcnow()
            )

        # Operations health (from customer metrics)
        customers = data.get('customer_metrics', {})
        if customers:
            ops_score = min(100, max(0,
                customers.get('nps', 50) +
                (100 - customers.get('churn_rate', 10) * 3)
            ) / 2 + 25)
            alerts = []
            if customers.get('nps', 100) < 30:
                alerts.append(f"NPS at {customers.get('nps')} - customer satisfaction issue")
            if customers.get('churn_rate', 0) > 10:
                alerts.append(f"Customer churn at {customers.get('churn_rate')}% - retention problem")

            scores[FunctionArea.OPERATIONS] = UnifiedHealthScore.from_score(
                function=FunctionArea.OPERATIONS,
                score=ops_score,
                key_metrics={
                    'nps': customers.get('nps', 0),
                    'churn_rate': customers.get('churn_rate', 0),
                    'customer_health_score': customers.get('customer_health_score', 0)
                },
                alerts=alerts,
                last_updated=datetime.utcnow()
            )

        # Strategy health (from goals)
        goals = metrics.get('goals_summary', {})
        if goals:
            total = goals.get('total', 1)
            on_track = goals.get('on_track', 0)
            strategy_score = (on_track / total * 100) if total > 0 else 50

            alerts = []
            if goals.get('at_risk', 0) > 0:
                alerts.append(f"{goals.get('at_risk')} strategic goals are at risk")
            if goals.get('overall_progress', 100) < 50:
                alerts.append(f"Overall goal progress at {goals.get('overall_progress')}%")

            scores[FunctionArea.STRATEGY] = UnifiedHealthScore.from_score(
                function=FunctionArea.STRATEGY,
                score=strategy_score,
                key_metrics={
                    'total_goals': total,
                    'on_track': on_track,
                    'at_risk': goals.get('at_risk', 0),
                    'overall_progress': goals.get('overall_progress', 0)
                },
                alerts=alerts,
                last_updated=datetime.utcnow()
            )

        return scores

    def _calculate_overall_health(self, scores: Dict[FunctionArea, UnifiedHealthScore]) -> float:
        """Calculate weighted overall health score."""
        if not scores:
            return 50.0

        total_weight = 0
        weighted_sum = 0

        for func, score in scores.items():
            weight = self.FUNCTION_WEIGHTS.get(func, 0.1)
            weighted_sum += score.score * weight
            total_weight += weight

        if total_weight == 0:
            return 50.0

        return weighted_sum / total_weight

    def _extract_alerts(self, score: UnifiedHealthScore, source: str) -> List[Dict[str, Any]]:
        """Extract critical alerts from a health score."""
        alerts = []
        severity_base = 100 - score.score  # Higher severity for lower scores

        for alert_text in score.alerts:
            alerts.append({
                'message': alert_text,
                'source': source,
                'function': score.function.value,
                'severity_score': severity_base,
                'grade': score.grade
            })

        return alerts

    def _extract_opportunities(self, data: Dict[str, Any], source: str) -> List[Dict[str, Any]]:
        """Extract opportunities from product data."""
        opportunities = []

        # This would be enhanced with product-specific logic
        if source == 'Marketing':
            best_channel = data.get('context_for_ai', {}).get('best_channel')
            if best_channel:
                opportunities.append({
                    'description': f"Double down on {best_channel} - highest performing channel",
                    'source': source,
                    'type': 'growth'
                })

        return opportunities

    def _generate_cross_functional_insights(
        self,
        scores: Dict[FunctionArea, UnifiedHealthScore],
        marketing: Dict = None,
        security: Dict = None,
        executive: Dict = None
    ) -> List[str]:
        """Generate insights that span multiple functions."""
        insights = []

        # Marketing + Finance insight
        if FunctionArea.MARKETING in scores and FunctionArea.FINANCE in scores:
            mkt = scores[FunctionArea.MARKETING]
            fin = scores[FunctionArea.FINANCE]
            if mkt.score < 60 and fin.key_metrics.get('revenue_growth', 0) < 10:
                insights.append(
                    "Marketing underperformance may be contributing to slow revenue growth - "
                    "consider reviewing marketing ROI and channel mix"
                )

        # Security + Operations insight
        if FunctionArea.SECURITY in scores and FunctionArea.OPERATIONS in scores:
            sec = scores[FunctionArea.SECURITY]
            ops = scores[FunctionArea.OPERATIONS]
            if sec.score < 70 and ops.key_metrics.get('nps', 100) < 40:
                insights.append(
                    "Security posture and customer satisfaction both need attention - "
                    "security incidents may be impacting customer experience"
                )

        # People + Strategy insight
        if FunctionArea.PEOPLE in scores and FunctionArea.STRATEGY in scores:
            ppl = scores[FunctionArea.PEOPLE]
            strat = scores[FunctionArea.STRATEGY]
            if ppl.key_metrics.get('turnover', 0) > 15 and strat.key_metrics.get('at_risk', 0) > 1:
                insights.append(
                    "High turnover may be impacting strategic execution - "
                    "consider retention initiatives for key goal owners"
                )

        # Overall health insight
        avg_score = sum(s.score for s in scores.values()) / len(scores) if scores else 50
        if avg_score < 60:
            insights.append(
                "Multiple business functions need attention - consider a comprehensive review "
                "to identify root causes and prioritize improvements"
            )
        elif avg_score > 80:
            insights.append(
                "Strong performance across functions - consider investing in growth initiatives "
                "or expanding into new markets"
            )

        return insights


def create_unified_context_builder(adapters: Dict[str, Any] = None) -> UnifiedContextBuilder:
    """Factory function to create a UnifiedContextBuilder."""
    return UnifiedContextBuilder(adapters)
