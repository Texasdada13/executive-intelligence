"""Board Reporting Engine"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from enum import Enum


class ReportPeriod(Enum):
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    ANNUAL = "Annual"


@dataclass
class FinancialHighlights:
    revenue: float
    revenue_growth: float
    gross_margin: float
    operating_margin: float
    cash_position: float
    burn_rate: float
    runway_months: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "revenue": self.revenue,
            "revenue_growth_pct": round(self.revenue_growth, 1),
            "gross_margin_pct": round(self.gross_margin, 1),
            "operating_margin_pct": round(self.operating_margin, 1),
            "cash_position": self.cash_position,
            "burn_rate": self.burn_rate,
            "runway_months": round(self.runway_months, 1)
        }


@dataclass
class OperationalHighlights:
    customer_count: int
    customer_growth: float
    nps: float
    churn_rate: float
    employee_count: int
    employee_engagement: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "customer_count": self.customer_count,
            "customer_growth_pct": round(self.customer_growth, 1),
            "nps": round(self.nps, 0),
            "churn_rate_pct": round(self.churn_rate, 1),
            "employee_count": self.employee_count,
            "employee_engagement_pct": round(self.employee_engagement, 1)
        }


@dataclass
class BoardReport:
    organization_id: str
    period: ReportPeriod
    period_date: date
    executive_summary: str
    financial_highlights: FinancialHighlights
    operational_highlights: OperationalHighlights
    strategic_progress: Dict[str, Any]
    key_achievements: List[str]
    challenges: List[str]
    next_period_priorities: List[str]
    asks_of_board: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "organization_id": self.organization_id,
            "period": self.period.value,
            "period_date": self.period_date.isoformat(),
            "executive_summary": self.executive_summary,
            "financial_highlights": self.financial_highlights.to_dict(),
            "operational_highlights": self.operational_highlights.to_dict(),
            "strategic_progress": self.strategic_progress,
            "key_achievements": self.key_achievements,
            "challenges": self.challenges,
            "next_period_priorities": self.next_period_priorities,
            "asks_of_board": self.asks_of_board
        }


class BoardReporter:
    """Generates board-ready reports from business data."""

    def generate_report(self, business_data: Dict[str, Any],
                        period: ReportPeriod = ReportPeriod.QUARTERLY,
                        period_date: date = None,
                        organization_id: str = "unknown") -> BoardReport:
        """Generate comprehensive board report."""
        period_date = period_date or date.today()

        # Extract financial data
        financial = FinancialHighlights(
            revenue=business_data.get("revenue", 0),
            revenue_growth=business_data.get("revenue_growth", 0),
            gross_margin=business_data.get("gross_margin", 0),
            operating_margin=business_data.get("operating_margin", 0),
            cash_position=business_data.get("cash", 0),
            burn_rate=business_data.get("burn_rate", 0),
            runway_months=business_data.get("runway", 0)
        )

        # Extract operational data
        operational = OperationalHighlights(
            customer_count=business_data.get("customers", 0),
            customer_growth=business_data.get("customer_growth", 0),
            nps=business_data.get("nps", 0),
            churn_rate=business_data.get("churn", 0),
            employee_count=business_data.get("employees", 0),
            employee_engagement=business_data.get("engagement", 0)
        )

        # Strategic progress
        strategic = {
            "goals_on_track": business_data.get("goals_on_track", 0),
            "goals_at_risk": business_data.get("goals_at_risk", 0),
            "overall_progress": business_data.get("strategic_progress", 0)
        }

        # Generate executive summary
        summary = self._generate_summary(financial, operational, strategic)

        # Key achievements
        achievements = business_data.get("achievements", [])

        # Challenges
        challenges = business_data.get("challenges", [])

        # Priorities
        priorities = business_data.get("priorities", [])

        # Asks
        asks = business_data.get("board_asks", [])

        return BoardReport(
            organization_id=organization_id,
            period=period,
            period_date=period_date,
            executive_summary=summary,
            financial_highlights=financial,
            operational_highlights=operational,
            strategic_progress=strategic,
            key_achievements=achievements[:5],
            challenges=challenges[:5],
            next_period_priorities=priorities[:5],
            asks_of_board=asks[:3]
        )

    def _generate_summary(self, financial: FinancialHighlights,
                          operational: OperationalHighlights,
                          strategic: Dict[str, Any]) -> str:
        """Generate executive summary for board."""
        parts = []

        # Financial summary
        if financial.revenue_growth > 20:
            parts.append(f"Strong revenue growth of {financial.revenue_growth:.0f}%.")
        elif financial.revenue_growth > 0:
            parts.append(f"Steady revenue growth of {financial.revenue_growth:.0f}%.")
        else:
            parts.append(f"Revenue declined {abs(financial.revenue_growth):.0f}%.")

        # Cash position
        if financial.runway_months < 6:
            parts.append(f"Runway of {financial.runway_months:.0f} months requires attention.")
        elif financial.runway_months > 18:
            parts.append(f"Strong cash position with {financial.runway_months:.0f} months runway.")

        # Customer health
        if operational.nps > 50:
            parts.append(f"Customer satisfaction strong (NPS: {operational.nps:.0f}).")
        elif operational.nps < 20:
            parts.append(f"Customer satisfaction needs focus (NPS: {operational.nps:.0f}).")

        # Strategic progress
        progress = strategic.get("overall_progress", 0)
        if progress > 75:
            parts.append(f"Strategic goals on track ({progress:.0f}% complete).")
        elif progress < 50:
            parts.append(f"Strategic execution needs acceleration ({progress:.0f}% complete).")

        return " ".join(parts)
