"""Executive Dashboard Aggregator - Unified C-Suite View"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime


class CSuiteRole(Enum):
    CFO = "CFO"
    CTO = "CTO"
    COO = "COO"
    CHRO = "CHRO"
    CMO = "CMO"
    CISO = "CISO"


@dataclass
class RoleMetrics:
    role: CSuiteRole
    health_score: float
    grade: str
    key_metrics: Dict[str, Any]
    alerts: List[str]
    top_priorities: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role.value,
            "health_score": round(self.health_score, 1),
            "grade": self.grade,
            "key_metrics": self.key_metrics,
            "alerts": self.alerts,
            "top_priorities": self.top_priorities
        }


@dataclass
class CSuiteMetrics:
    organization_id: str
    overall_health: float
    overall_grade: str
    role_metrics: Dict[str, RoleMetrics]
    critical_alerts: List[str]
    cross_functional_insights: List[str]
    priority_actions: List[str]
    trend: str
    snapshot_date: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "organization_id": self.organization_id,
            "overall_health": round(self.overall_health, 1),
            "overall_grade": self.overall_grade,
            "role_metrics": {k: v.to_dict() for k, v in self.role_metrics.items()},
            "critical_alerts": self.critical_alerts,
            "cross_functional_insights": self.cross_functional_insights,
            "priority_actions": self.priority_actions,
            "trend": self.trend,
            "snapshot_date": self.snapshot_date.isoformat()
        }


class DashboardAggregator:
    """Aggregates metrics across all C-Suite roles for executive dashboard."""

    GRADE_THRESHOLDS = {90: "A", 80: "B", 70: "C", 60: "D", 0: "F"}
    ROLE_WEIGHTS = {
        CSuiteRole.CFO: 1.2,
        CSuiteRole.CTO: 1.0,
        CSuiteRole.COO: 1.0,
        CSuiteRole.CHRO: 0.9,
        CSuiteRole.CMO: 1.0,
        CSuiteRole.CISO: 1.1,
    }

    def aggregate_metrics(self, role_data: Dict[CSuiteRole, Dict[str, Any]],
                          organization_id: str = "unknown",
                          previous_health: float = None) -> CSuiteMetrics:
        """Aggregate metrics from all C-Suite roles."""
        role_metrics = {}
        all_alerts = []
        all_priorities = []

        for role, data in role_data.items():
            health = data.get("health_score", 0)
            metrics = RoleMetrics(
                role=role,
                health_score=health,
                grade=self._get_grade(health),
                key_metrics=data.get("key_metrics", {}),
                alerts=data.get("alerts", []),
                top_priorities=data.get("priorities", [])
            )
            role_metrics[role.value] = metrics

            # Collect critical alerts
            if health < 50:
                all_alerts.append(f"{role.value}: Health score critical ({health:.0f})")
            all_alerts.extend([f"{role.value}: {a}" for a in metrics.alerts[:2]])

            # Collect priorities
            all_priorities.extend([f"{role.value}: {p}" for p in metrics.top_priorities[:2]])

        # Calculate overall health with role weights
        if role_metrics:
            weighted_sum = sum(
                m.health_score * self.ROLE_WEIGHTS.get(CSuiteRole(m.role), 1)
                for m in role_metrics.values()
            )
            weight_total = sum(
                self.ROLE_WEIGHTS.get(CSuiteRole(m.role), 1)
                for m in role_metrics.values()
            )
            overall = weighted_sum / weight_total
        else:
            overall = 0

        # Determine trend
        if previous_health is not None:
            if overall > previous_health + 5:
                trend = "Improving"
            elif overall < previous_health - 5:
                trend = "Declining"
            else:
                trend = "Stable"
        else:
            trend = "Baseline"

        # Cross-functional insights
        insights = self._generate_cross_functional_insights(role_metrics)

        return CSuiteMetrics(
            organization_id=organization_id,
            overall_health=overall,
            overall_grade=self._get_grade(overall),
            role_metrics=role_metrics,
            critical_alerts=all_alerts[:10],
            cross_functional_insights=insights,
            priority_actions=all_priorities[:10],
            trend=trend
        )

    def _get_grade(self, score: float) -> str:
        for threshold, grade in sorted(self.GRADE_THRESHOLDS.items(), reverse=True):
            if score >= threshold:
                return grade
        return "F"

    def _generate_cross_functional_insights(self, role_metrics: Dict[str, RoleMetrics]) -> List[str]:
        """Generate insights that span multiple roles."""
        insights = []

        # Check for related patterns
        cfo = role_metrics.get("CFO")
        cmo = role_metrics.get("CMO")
        chro = role_metrics.get("CHRO")
        cto = role_metrics.get("CTO")
        ciso = role_metrics.get("CISO")

        if cfo and cmo:
            if cfo.health_score < 60 and cmo.health_score > 75:
                insights.append("Strong marketing but financial stress - review CAC and marketing ROI")
            elif cmo.health_score < 60 and cfo.health_score > 75:
                insights.append("Financial health good but marketing underperforming - consider investment")

        if chro and all([cfo, cto, cmo]):
            avg_ops = sum([cfo.health_score, cto.health_score, cmo.health_score]) / 3
            if chro.health_score < 60 and avg_ops > 75:
                insights.append("Strong operations but people challenges - risk of burnout/turnover")

        if ciso and cto:
            if ciso.health_score < 50 and cto.health_score > 75:
                insights.append("Technology advancing but security lagging - close the gap")

        return insights[:5]
