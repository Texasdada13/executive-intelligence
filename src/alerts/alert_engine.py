"""Alert engine for Executive Intelligence - monitors business metrics and generates alerts."""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertCategory(Enum):
    GOALS = "goals"
    FINANCIAL = "financial"
    CUSTOMER = "customer"
    PEOPLE = "people"
    CSUITE = "csuite"


@dataclass
class Alert:
    """Represents an executive alert."""
    id: str
    severity: AlertSeverity
    category: AlertCategory
    title: str
    message: str
    metric_name: str
    current_value: Any
    threshold_value: Any
    recommendation: str
    created_at: datetime

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'severity': self.severity.value,
            'category': self.category.value,
            'title': self.title,
            'message': self.message,
            'metric_name': self.metric_name,
            'current_value': self.current_value,
            'threshold_value': self.threshold_value,
            'recommendation': self.recommendation,
            'created_at': self.created_at.isoformat()
        }


class AlertEngine:
    """Engine for generating executive alerts based on thresholds."""

    # Default thresholds
    THRESHOLDS = {
        'goals_behind_max': 2,         # More than 2 goals behind
        'goals_at_risk_max': 3,        # More than 3 goals at risk
        'health_score_critical': 60,   # Health score below 60
        'health_score_warning': 75,    # Health score below 75
        'nps_critical': 0,             # NPS below 0 is critical
        'nps_warning': 30,             # NPS below 30 needs attention
        'churn_critical': 10,          # Churn above 10%
        'churn_warning': 5,            # Churn above 5%
        'engagement_critical': 50,     # Engagement below 50
        'engagement_warning': 70,      # Engagement below 70
        'attrition_critical': 15,      # Attrition above 15%
        'attrition_warning': 10,       # Attrition above 10%
        'csuite_score_critical': 60,   # C-Suite score below 60
        'csuite_score_warning': 70,    # C-Suite score below 70
        'runway_critical_months': 6,   # Less than 6 months runway
        'runway_warning_months': 12,   # Less than 12 months runway
    }

    def __init__(self, custom_thresholds: Optional[Dict] = None):
        self.thresholds = {**self.THRESHOLDS}
        if custom_thresholds:
            self.thresholds.update(custom_thresholds)
        self._alert_counter = 0

    def _generate_id(self) -> str:
        self._alert_counter += 1
        return f"exec-alert-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self._alert_counter}"

    def check_metrics(self, data: Dict[str, Any]) -> List[Alert]:
        """Check all metrics and generate alerts."""
        alerts = []

        health = data.get('health', {})
        goals = data.get('goals', {})
        financial = data.get('financial', {})
        customer = data.get('customer', {})
        people = data.get('people', {})
        csuite = health.get('csuite_scores', {})

        # Check goals at risk and behind
        behind = goals.get('behind', 0)
        at_risk = goals.get('at_risk', 0)

        if behind > self.thresholds['goals_behind_max']:
            alerts.append(Alert(
                id=self._generate_id(),
                severity=AlertSeverity.CRITICAL,
                category=AlertCategory.GOALS,
                title=f"Critical: {behind} Strategic Goals Behind Schedule",
                message=f"You have {behind} strategic goals that are behind schedule, requiring immediate executive attention.",
                metric_name="Goals Behind",
                current_value=behind,
                threshold_value=self.thresholds['goals_behind_max'],
                recommendation="Schedule emergency goal review. Reallocate resources or adjust timelines for at-risk objectives.",
                created_at=datetime.now()
            ))

        if at_risk > self.thresholds['goals_at_risk_max']:
            alerts.append(Alert(
                id=self._generate_id(),
                severity=AlertSeverity.WARNING,
                category=AlertCategory.GOALS,
                title=f"Warning: {at_risk} Strategic Goals At Risk",
                message=f"You have {at_risk} strategic goals at risk of missing targets.",
                metric_name="Goals At Risk",
                current_value=at_risk,
                threshold_value=self.thresholds['goals_at_risk_max'],
                recommendation="Review at-risk goals with owners. Identify blockers and create mitigation plans.",
                created_at=datetime.now()
            ))

        # Check overall health score
        health_score = health.get('score', 100)
        if health_score < self.thresholds['health_score_critical']:
            alerts.append(Alert(
                id=self._generate_id(),
                severity=AlertSeverity.CRITICAL,
                category=AlertCategory.CSUITE,
                title="Critical: Business Health Score Critically Low",
                message=f"Overall business health score is {health_score}, indicating serious organizational challenges.",
                metric_name="Health Score",
                current_value=health_score,
                threshold_value=self.thresholds['health_score_critical'],
                recommendation="Conduct comprehensive business review. Engage with each C-Suite function to address deficiencies.",
                created_at=datetime.now()
            ))
        elif health_score < self.thresholds['health_score_warning']:
            alerts.append(Alert(
                id=self._generate_id(),
                severity=AlertSeverity.WARNING,
                category=AlertCategory.CSUITE,
                title="Warning: Business Health Needs Attention",
                message=f"Overall business health score is {health_score}, below the target of {self.thresholds['health_score_warning']}.",
                metric_name="Health Score",
                current_value=health_score,
                threshold_value=self.thresholds['health_score_warning'],
                recommendation="Review underperforming functions and create improvement plans with respective leaders.",
                created_at=datetime.now()
            ))

        # Check individual C-Suite scores
        csuite_names = {
            'ceo': 'CEO (Strategy)', 'cfo': 'CFO (Finance)', 'cmo': 'CMO (Marketing)',
            'cto': 'CTO (Technology)', 'coo': 'COO (Operations)', 'chro': 'CHRO (People)',
            'ciso': 'CISO (Security)', 'clo': 'CLO (Legal)'
        }

        for role, score in csuite.items():
            role_name = csuite_names.get(role, role.upper())
            if score < self.thresholds['csuite_score_critical']:
                alerts.append(Alert(
                    id=self._generate_id(),
                    severity=AlertSeverity.CRITICAL,
                    category=AlertCategory.CSUITE,
                    title=f"Critical: {role_name} Function Underperforming",
                    message=f"{role_name} health score is {score}, requiring immediate intervention.",
                    metric_name=f"{role.upper()} Score",
                    current_value=score,
                    threshold_value=self.thresholds['csuite_score_critical'],
                    recommendation=f"Schedule deep-dive with {role_name}. Identify root causes and create 30-day improvement plan.",
                    created_at=datetime.now()
                ))
            elif score < self.thresholds['csuite_score_warning']:
                alerts.append(Alert(
                    id=self._generate_id(),
                    severity=AlertSeverity.WARNING,
                    category=AlertCategory.CSUITE,
                    title=f"Warning: {role_name} Function Needs Improvement",
                    message=f"{role_name} health score is {score}, below the target of {self.thresholds['csuite_score_warning']}.",
                    metric_name=f"{role.upper()} Score",
                    current_value=score,
                    threshold_value=self.thresholds['csuite_score_warning'],
                    recommendation=f"Review {role_name} KPIs and identify areas for improvement.",
                    created_at=datetime.now()
                ))

        # Check NPS
        nps = customer.get('nps_score', 50)
        if nps < self.thresholds['nps_critical']:
            alerts.append(Alert(
                id=self._generate_id(),
                severity=AlertSeverity.CRITICAL,
                category=AlertCategory.CUSTOMER,
                title="Critical: NPS Score Negative",
                message=f"NPS is {nps}, indicating more detractors than promoters among your customers.",
                metric_name="NPS",
                current_value=nps,
                threshold_value=self.thresholds['nps_critical'],
                recommendation="Launch immediate customer feedback campaign. Address top complaints and improve customer experience.",
                created_at=datetime.now()
            ))
        elif nps < self.thresholds['nps_warning']:
            alerts.append(Alert(
                id=self._generate_id(),
                severity=AlertSeverity.WARNING,
                category=AlertCategory.CUSTOMER,
                title="Warning: NPS Below Target",
                message=f"NPS is {nps}, below the healthy threshold of {self.thresholds['nps_warning']}.",
                metric_name="NPS",
                current_value=nps,
                threshold_value=self.thresholds['nps_warning'],
                recommendation="Analyze detractor feedback and implement improvements to customer journey.",
                created_at=datetime.now()
            ))

        # Check churn rate
        churn = customer.get('churn_rate', 0)
        if churn > self.thresholds['churn_critical']:
            alerts.append(Alert(
                id=self._generate_id(),
                severity=AlertSeverity.CRITICAL,
                category=AlertCategory.CUSTOMER,
                title="Critical: Customer Churn Rate Alarming",
                message=f"Customer churn rate is {churn:.1f}%, significantly impacting revenue retention.",
                metric_name="Churn Rate",
                current_value=churn,
                threshold_value=self.thresholds['churn_critical'],
                recommendation="Implement emergency retention program. Reach out to at-risk customers with personalized offers.",
                created_at=datetime.now()
            ))
        elif churn > self.thresholds['churn_warning']:
            alerts.append(Alert(
                id=self._generate_id(),
                severity=AlertSeverity.WARNING,
                category=AlertCategory.CUSTOMER,
                title="Warning: Churn Rate Elevated",
                message=f"Customer churn rate is {churn:.1f}%, above the target of {self.thresholds['churn_warning']}%.",
                metric_name="Churn Rate",
                current_value=churn,
                threshold_value=self.thresholds['churn_warning'],
                recommendation="Review churn reasons and implement proactive customer success initiatives.",
                created_at=datetime.now()
            ))

        # Check engagement score
        engagement = people.get('engagement_score', 100)
        if engagement < self.thresholds['engagement_critical']:
            alerts.append(Alert(
                id=self._generate_id(),
                severity=AlertSeverity.CRITICAL,
                category=AlertCategory.PEOPLE,
                title="Critical: Employee Engagement Critically Low",
                message=f"Employee engagement score is {engagement}, indicating serious morale and culture issues.",
                metric_name="Engagement Score",
                current_value=engagement,
                threshold_value=self.thresholds['engagement_critical'],
                recommendation="Conduct employee listening sessions. Address top concerns and improve leadership communication.",
                created_at=datetime.now()
            ))
        elif engagement < self.thresholds['engagement_warning']:
            alerts.append(Alert(
                id=self._generate_id(),
                severity=AlertSeverity.WARNING,
                category=AlertCategory.PEOPLE,
                title="Warning: Employee Engagement Needs Attention",
                message=f"Employee engagement score is {engagement}, below the healthy threshold of {self.thresholds['engagement_warning']}.",
                metric_name="Engagement Score",
                current_value=engagement,
                threshold_value=self.thresholds['engagement_warning'],
                recommendation="Review engagement survey results and implement targeted improvement initiatives.",
                created_at=datetime.now()
            ))

        # Check attrition rate
        attrition = people.get('attrition_rate', 0)
        if attrition > self.thresholds['attrition_critical']:
            alerts.append(Alert(
                id=self._generate_id(),
                severity=AlertSeverity.CRITICAL,
                category=AlertCategory.PEOPLE,
                title="Critical: Employee Attrition Rate Alarming",
                message=f"Employee attrition is {attrition:.1f}%, causing significant talent and knowledge loss.",
                metric_name="Attrition Rate",
                current_value=attrition,
                threshold_value=self.thresholds['attrition_critical'],
                recommendation="Implement retention bonuses for key talent. Review compensation competitiveness and career paths.",
                created_at=datetime.now()
            ))
        elif attrition > self.thresholds['attrition_warning']:
            alerts.append(Alert(
                id=self._generate_id(),
                severity=AlertSeverity.WARNING,
                category=AlertCategory.PEOPLE,
                title="Warning: Attrition Rate Above Target",
                message=f"Employee attrition is {attrition:.1f}%, above the target of {self.thresholds['attrition_warning']}%.",
                metric_name="Attrition Rate",
                current_value=attrition,
                threshold_value=self.thresholds['attrition_warning'],
                recommendation="Conduct stay interviews with high performers. Improve development opportunities.",
                created_at=datetime.now()
            ))

        # Check cash runway
        runway = financial.get('cash_runway', 24)
        if runway < self.thresholds['runway_critical_months']:
            alerts.append(Alert(
                id=self._generate_id(),
                severity=AlertSeverity.CRITICAL,
                category=AlertCategory.FINANCIAL,
                title="Critical: Cash Runway Dangerously Low",
                message=f"Cash runway is only {runway} months, requiring immediate financial action.",
                metric_name="Cash Runway",
                current_value=runway,
                threshold_value=self.thresholds['runway_critical_months'],
                recommendation="Initiate emergency cost reduction. Accelerate fundraising or revenue generation efforts.",
                created_at=datetime.now()
            ))
        elif runway < self.thresholds['runway_warning_months']:
            alerts.append(Alert(
                id=self._generate_id(),
                severity=AlertSeverity.WARNING,
                category=AlertCategory.FINANCIAL,
                title="Warning: Cash Runway Below Target",
                message=f"Cash runway is {runway} months, below the comfortable threshold of {self.thresholds['runway_warning_months']} months.",
                metric_name="Cash Runway",
                current_value=runway,
                threshold_value=self.thresholds['runway_warning_months'],
                recommendation="Review burn rate and identify cost optimization opportunities. Plan for next funding round.",
                created_at=datetime.now()
            ))

        # Sort by severity (critical first)
        severity_order = {AlertSeverity.CRITICAL: 0, AlertSeverity.WARNING: 1, AlertSeverity.INFO: 2}
        alerts.sort(key=lambda a: severity_order[a.severity])

        return alerts

    def get_alert_summary(self, alerts: List[Alert]) -> Dict:
        """Get a summary of alerts by severity."""
        summary = {
            'total': len(alerts),
            'critical': sum(1 for a in alerts if a.severity == AlertSeverity.CRITICAL),
            'warning': sum(1 for a in alerts if a.severity == AlertSeverity.WARNING),
            'info': sum(1 for a in alerts if a.severity == AlertSeverity.INFO),
            'categories': {}
        }

        for alert in alerts:
            cat = alert.category.value
            if cat not in summary['categories']:
                summary['categories'][cat] = 0
            summary['categories'][cat] += 1

        return summary


def create_alert_engine(custom_thresholds: Optional[Dict] = None) -> AlertEngine:
    """Factory function to create an alert engine."""
    return AlertEngine(custom_thresholds)
