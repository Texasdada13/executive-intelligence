"""Executive Business Health Scoring Engine"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class BusinessDomain(Enum):
    FINANCIAL = "Financial Health"
    OPERATIONAL = "Operational Excellence"
    CUSTOMER = "Customer Success"
    PEOPLE = "People & Culture"
    TECHNOLOGY = "Technology & Innovation"
    MARKET = "Market Position"
    RISK = "Risk & Compliance"


@dataclass
class ScoringDimension:
    id: str
    name: str
    domain: BusinessDomain
    weight: float
    description: str = ""


@dataclass
class DimensionScore:
    dimension_id: str
    dimension_name: str
    domain: str
    score: float
    weighted_score: float
    trend: str
    status: str
    insights: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimension_id": self.dimension_id,
            "dimension_name": self.dimension_name,
            "domain": self.domain,
            "score": round(self.score, 1),
            "weighted_score": round(self.weighted_score, 2),
            "trend": self.trend,
            "status": self.status,
            "insights": self.insights
        }


@dataclass
class BusinessHealthReport:
    entity_id: str
    overall_score: float
    overall_grade: str
    overall_status: str
    domain_scores: Dict[str, float]
    dimension_scores: List[DimensionScore]
    strengths: List[str]
    concerns: List[str]
    executive_summary: str
    priority_actions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "overall_score": round(self.overall_score, 1),
            "overall_grade": self.overall_grade,
            "overall_status": self.overall_status,
            "domain_scores": {k: round(v, 1) for k, v in self.domain_scores.items()},
            "dimension_scores": [ds.to_dict() for ds in self.dimension_scores],
            "strengths": self.strengths,
            "concerns": self.concerns,
            "executive_summary": self.executive_summary,
            "priority_actions": self.priority_actions
        }


class ExecutiveScoringEngine:
    """Multi-dimensional business health scoring for executive oversight."""

    GRADE_THRESHOLDS = {90: "A", 80: "B", 70: "C", 60: "D", 0: "F"}
    STATUS_THRESHOLDS = {85: "Thriving", 70: "Healthy", 55: "Stable", 40: "At Risk", 0: "Critical"}

    def __init__(self, dimensions: List[ScoringDimension]):
        self.dimensions = {d.id: d for d in dimensions}
        self.total_weight = sum(d.weight for d in dimensions)

    def calculate_health(self, scores: Dict[str, Dict[str, Any]],
                         entity_id: str = "unknown") -> BusinessHealthReport:
        """Calculate comprehensive business health score."""
        dimension_scores = []
        domain_totals: Dict[str, List[float]] = {}

        for dim_id, dim in self.dimensions.items():
            data = scores.get(dim_id, {})
            score = data.get("score", 0)
            prev_score = data.get("previous_score")

            weighted = score * (dim.weight / self.total_weight)
            trend = self._determine_trend(score, prev_score)
            status = self._get_status(score)
            insights = self._generate_insights(dim, score, trend)

            dimension_scores.append(DimensionScore(
                dimension_id=dim_id,
                dimension_name=dim.name,
                domain=dim.domain.value,
                score=score,
                weighted_score=weighted,
                trend=trend,
                status=status,
                insights=insights
            ))

            domain = dim.domain.value
            if domain not in domain_totals:
                domain_totals[domain] = []
            domain_totals[domain].append(score)

        # Calculate domain averages
        domain_scores = {
            domain: sum(scores) / len(scores)
            for domain, scores in domain_totals.items() if scores
        }

        # Overall score
        overall = sum(ds.weighted_score for ds in dimension_scores)

        # Identify strengths and concerns
        sorted_dims = sorted(dimension_scores, key=lambda x: x.score, reverse=True)
        strengths = [f"{d.dimension_name}: {d.score:.0f}" for d in sorted_dims[:3] if d.score >= 75]
        concerns = [f"{d.dimension_name}: {d.score:.0f}" for d in sorted_dims if d.score < 60][-3:]

        # Executive summary
        summary = self._generate_summary(overall, domain_scores, strengths, concerns)

        # Priority actions
        actions = self._generate_priority_actions(dimension_scores)

        return BusinessHealthReport(
            entity_id=entity_id,
            overall_score=overall,
            overall_grade=self._get_grade(overall),
            overall_status=self._get_status(overall),
            domain_scores=domain_scores,
            dimension_scores=dimension_scores,
            strengths=strengths,
            concerns=concerns,
            executive_summary=summary,
            priority_actions=actions
        )

    def _get_grade(self, score: float) -> str:
        for threshold, grade in sorted(self.GRADE_THRESHOLDS.items(), reverse=True):
            if score >= threshold:
                return grade
        return "F"

    def _get_status(self, score: float) -> str:
        for threshold, status in sorted(self.STATUS_THRESHOLDS.items(), reverse=True):
            if score >= threshold:
                return status
        return "Critical"

    def _determine_trend(self, current: float, previous: float = None) -> str:
        if previous is None:
            return "Baseline"
        diff = current - previous
        if diff > 5:
            return "Improving"
        elif diff < -5:
            return "Declining"
        return "Stable"

    def _generate_insights(self, dim: ScoringDimension, score: float, trend: str) -> List[str]:
        insights = []
        if score >= 85:
            insights.append(f"{dim.name} is a key strength")
        elif score < 50:
            insights.append(f"{dim.name} requires immediate attention")
        elif score < 70:
            insights.append(f"{dim.name} has room for improvement")

        if trend == "Declining":
            insights.append(f"Negative trend in {dim.name}")

        return insights

    def _generate_summary(self, overall: float, domain_scores: Dict[str, float],
                          strengths: List[str], concerns: List[str]) -> str:
        status = self._get_status(overall)
        grade = self._get_grade(overall)

        if status == "Thriving":
            intro = f"Business is performing exceptionally well with an overall score of {overall:.0f} (Grade {grade})."
        elif status == "Healthy":
            intro = f"Business is in good health with a score of {overall:.0f} (Grade {grade})."
        elif status == "Stable":
            intro = f"Business is stable but has opportunities for improvement. Score: {overall:.0f} (Grade {grade})."
        else:
            intro = f"Business requires attention with a score of {overall:.0f} (Grade {grade})."

        return intro

    def _generate_priority_actions(self, dimension_scores: List[DimensionScore]) -> List[str]:
        actions = []
        critical = [ds for ds in dimension_scores if ds.score < 50]
        declining = [ds for ds in dimension_scores if ds.trend == "Declining"]

        for ds in critical[:3]:
            actions.append(f"Address critical {ds.dimension_name} performance")

        for ds in declining[:2]:
            if ds not in critical:
                actions.append(f"Reverse decline in {ds.dimension_name}")

        return actions[:5]


def create_business_health_engine() -> ExecutiveScoringEngine:
    """Create a comprehensive business health scoring engine."""
    dimensions = [
        # Financial
        ScoringDimension("revenue_growth", "Revenue Growth", BusinessDomain.FINANCIAL, 12),
        ScoringDimension("profitability", "Profitability", BusinessDomain.FINANCIAL, 12),
        ScoringDimension("cash_flow", "Cash Flow Health", BusinessDomain.FINANCIAL, 10),
        ScoringDimension("financial_efficiency", "Financial Efficiency", BusinessDomain.FINANCIAL, 8),

        # Operational
        ScoringDimension("operational_efficiency", "Operational Efficiency", BusinessDomain.OPERATIONAL, 8),
        ScoringDimension("quality_metrics", "Quality & Delivery", BusinessDomain.OPERATIONAL, 6),

        # Customer
        ScoringDimension("customer_satisfaction", "Customer Satisfaction", BusinessDomain.CUSTOMER, 10),
        ScoringDimension("customer_retention", "Customer Retention", BusinessDomain.CUSTOMER, 8),
        ScoringDimension("market_share", "Market Share", BusinessDomain.CUSTOMER, 6),

        # People
        ScoringDimension("employee_engagement", "Employee Engagement", BusinessDomain.PEOPLE, 6),
        ScoringDimension("talent_retention", "Talent Retention", BusinessDomain.PEOPLE, 5),

        # Technology
        ScoringDimension("tech_health", "Technology Health", BusinessDomain.TECHNOLOGY, 5),
        ScoringDimension("innovation", "Innovation Pipeline", BusinessDomain.TECHNOLOGY, 4),

        # Risk
        ScoringDimension("security_posture", "Security Posture", BusinessDomain.RISK, 5),
        ScoringDimension("compliance_status", "Compliance Status", BusinessDomain.RISK, 5),
    ]

    return ExecutiveScoringEngine(dimensions)
