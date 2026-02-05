"""Executive KPI Benchmark Engine"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class KPICategory(Enum):
    FINANCIAL = "Financial"
    GROWTH = "Growth"
    EFFICIENCY = "Efficiency"
    CUSTOMER = "Customer"
    PEOPLE = "People"
    MARKET = "Market"


class KPIDirection(Enum):
    HIGHER_IS_BETTER = "higher_is_better"
    LOWER_IS_BETTER = "lower_is_better"


@dataclass
class ExecutiveKPI:
    kpi_id: str
    name: str
    benchmark_value: float
    direction: KPIDirection
    category: KPICategory
    unit: str = ""
    weight: float = 1.0


@dataclass
class KPIScore:
    kpi_id: str
    kpi_name: str
    actual_value: float
    benchmark_value: float
    score: float
    gap: float
    rating: str
    insight: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "kpi_id": self.kpi_id,
            "kpi_name": self.kpi_name,
            "actual_value": self.actual_value,
            "benchmark_value": self.benchmark_value,
            "score": round(self.score, 1),
            "gap": round(self.gap, 2),
            "rating": self.rating,
            "insight": self.insight
        }


@dataclass
class ExecutiveBenchmarkReport:
    entity_id: str
    overall_score: float
    overall_rating: str
    grade: str
    category_scores: Dict[str, float]
    kpi_scores: List[KPIScore]
    top_performers: List[str]
    improvement_areas: List[str]
    executive_insights: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "overall_score": round(self.overall_score, 1),
            "overall_rating": self.overall_rating,
            "grade": self.grade,
            "category_scores": {k: round(v, 1) for k, v in self.category_scores.items()},
            "top_performers": self.top_performers,
            "improvement_areas": self.improvement_areas,
            "executive_insights": self.executive_insights
        }


class BenchmarkEngine:
    """Executive KPI benchmarking engine."""

    RATING_THRESHOLDS = {90: "Excellent", 75: "Good", 60: "Fair", 40: "Poor", 0: "Critical"}
    GRADE_THRESHOLDS = {90: "A", 80: "B", 70: "C", 60: "D", 0: "F"}

    def __init__(self, kpis: List[ExecutiveKPI], category_weights: Optional[Dict[str, float]] = None):
        self.kpis = {k.kpi_id: k for k in kpis}
        self.category_weights = category_weights or {}

    def analyze(self, actual_values: Dict[str, float], entity_id: str = "unknown") -> ExecutiveBenchmarkReport:
        """Analyze KPIs against benchmarks."""
        kpi_scores = []
        category_totals: Dict[str, List[float]] = {}

        for kpi_id, kpi in self.kpis.items():
            actual = actual_values.get(kpi_id)
            if actual is None:
                continue

            score_result = self._score_kpi(kpi, actual)
            kpi_scores.append(score_result)

            cat = kpi.category.value
            if cat not in category_totals:
                category_totals[cat] = []
            category_totals[cat].append(score_result.score)

        # Category scores
        category_scores = {cat: sum(scores) / len(scores) for cat, scores in category_totals.items() if scores}

        # Overall score with category weights
        if category_scores:
            weighted_sum = sum(s * self.category_weights.get(c, 1) for c, s in category_scores.items())
            weight_total = sum(self.category_weights.get(c, 1) for c in category_scores)
            overall = weighted_sum / weight_total
        else:
            overall = 0

        # Identify top and bottom performers
        sorted_kpis = sorted(kpi_scores, key=lambda x: x.score, reverse=True)
        top = [f"{k.kpi_name}: {k.actual_value}{self.kpis[k.kpi_id].unit}" for k in sorted_kpis[:3] if k.score >= 75]
        bottom = [f"{k.kpi_name}: {k.actual_value}{self.kpis[k.kpi_id].unit}" for k in sorted_kpis if k.score < 60][-3:]

        # Executive insights
        insights = self._generate_insights(kpi_scores, category_scores, overall)

        return ExecutiveBenchmarkReport(
            entity_id=entity_id,
            overall_score=overall,
            overall_rating=self._rate(overall),
            grade=self._grade(overall),
            category_scores=category_scores,
            kpi_scores=kpi_scores,
            top_performers=top,
            improvement_areas=bottom,
            executive_insights=insights
        )

    def _score_kpi(self, kpi: ExecutiveKPI, actual: float) -> KPIScore:
        benchmark = kpi.benchmark_value
        gap = actual - benchmark

        if kpi.direction == KPIDirection.HIGHER_IS_BETTER:
            score = min(120, (actual / benchmark * 100)) if benchmark > 0 else 100
        else:
            score = min(120, (benchmark / actual * 100)) if actual > 0 else 100

        rating = self._rate(score)

        if score >= 90:
            insight = f"Excellent {kpi.name} performance"
        elif score >= 75:
            insight = f"Solid {kpi.name} performance"
        elif score >= 60:
            insight = f"{kpi.name} meeting expectations"
        else:
            action = "increase" if kpi.direction == KPIDirection.HIGHER_IS_BETTER else "reduce"
            insight = f"Focus on {kpi.name} - {action} needed"

        return KPIScore(
            kpi_id=kpi.kpi_id,
            kpi_name=kpi.name,
            actual_value=actual,
            benchmark_value=benchmark,
            score=score,
            gap=gap,
            rating=rating,
            insight=insight
        )

    def _rate(self, score: float) -> str:
        for t, r in sorted(self.RATING_THRESHOLDS.items(), reverse=True):
            if score >= t:
                return r
        return "Critical"

    def _grade(self, score: float) -> str:
        for t, g in sorted(self.GRADE_THRESHOLDS.items(), reverse=True):
            if score >= t:
                return g
        return "F"

    def _generate_insights(self, kpi_scores: List[KPIScore],
                           category_scores: Dict[str, float], overall: float) -> List[str]:
        insights = []

        # Overall performance
        if overall >= 80:
            insights.append("Business performing above industry benchmarks")
        elif overall < 60:
            insights.append("Performance below industry benchmarks - focus required")

        # Category insights
        for cat, score in category_scores.items():
            if score >= 85:
                insights.append(f"{cat} is a competitive advantage")
            elif score < 50:
                insights.append(f"{cat} requires strategic attention")

        return insights[:5]


def create_executive_benchmarks() -> BenchmarkEngine:
    """Create executive KPI benchmark engine."""
    kpis = [
        # Financial
        ExecutiveKPI("revenue_growth", "Revenue Growth Rate", 15, KPIDirection.HIGHER_IS_BETTER, KPICategory.FINANCIAL, "%"),
        ExecutiveKPI("gross_margin", "Gross Margin", 50, KPIDirection.HIGHER_IS_BETTER, KPICategory.FINANCIAL, "%"),
        ExecutiveKPI("ebitda_margin", "EBITDA Margin", 15, KPIDirection.HIGHER_IS_BETTER, KPICategory.FINANCIAL, "%"),
        ExecutiveKPI("rule_of_40", "Rule of 40", 40, KPIDirection.HIGHER_IS_BETTER, KPICategory.FINANCIAL, "%"),

        # Growth
        ExecutiveKPI("customer_growth", "Customer Growth", 20, KPIDirection.HIGHER_IS_BETTER, KPICategory.GROWTH, "%"),
        ExecutiveKPI("arr_growth", "ARR Growth", 30, KPIDirection.HIGHER_IS_BETTER, KPICategory.GROWTH, "%"),
        ExecutiveKPI("market_expansion", "Market Expansion", 10, KPIDirection.HIGHER_IS_BETTER, KPICategory.GROWTH, "%"),

        # Efficiency
        ExecutiveKPI("cac_payback", "CAC Payback Period", 12, KPIDirection.LOWER_IS_BETTER, KPICategory.EFFICIENCY, "months"),
        ExecutiveKPI("ltv_cac_ratio", "LTV:CAC Ratio", 3, KPIDirection.HIGHER_IS_BETTER, KPICategory.EFFICIENCY, "x"),
        ExecutiveKPI("burn_multiple", "Burn Multiple", 1.5, KPIDirection.LOWER_IS_BETTER, KPICategory.EFFICIENCY, "x"),

        # Customer
        ExecutiveKPI("nps", "Net Promoter Score", 50, KPIDirection.HIGHER_IS_BETTER, KPICategory.CUSTOMER, ""),
        ExecutiveKPI("gross_retention", "Gross Retention", 90, KPIDirection.HIGHER_IS_BETTER, KPICategory.CUSTOMER, "%"),
        ExecutiveKPI("net_retention", "Net Revenue Retention", 110, KPIDirection.HIGHER_IS_BETTER, KPICategory.CUSTOMER, "%"),

        # People
        ExecutiveKPI("employee_engagement", "Employee Engagement", 75, KPIDirection.HIGHER_IS_BETTER, KPICategory.PEOPLE, "%"),
        ExecutiveKPI("voluntary_turnover", "Voluntary Turnover", 15, KPIDirection.LOWER_IS_BETTER, KPICategory.PEOPLE, "%"),
        ExecutiveKPI("revenue_per_employee", "Revenue per Employee", 200000, KPIDirection.HIGHER_IS_BETTER, KPICategory.PEOPLE, "$"),
    ]

    return BenchmarkEngine(kpis, {
        "Financial": 1.3, "Growth": 1.2, "Efficiency": 1.1,
        "Customer": 1.1, "People": 1.0, "Market": 1.0
    })
