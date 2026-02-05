"""Strategic Planning and Goal Tracking"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime, date


class GoalStatus(Enum):
    NOT_STARTED = "Not Started"
    ON_TRACK = "On Track"
    AT_RISK = "At Risk"
    BEHIND = "Behind"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class GoalCategory(Enum):
    GROWTH = "Growth"
    PROFITABILITY = "Profitability"
    CUSTOMER = "Customer"
    OPERATIONAL = "Operational"
    PEOPLE = "People"
    TECHNOLOGY = "Technology"
    RISK = "Risk & Compliance"


class TimeHorizon(Enum):
    QUARTERLY = "Quarterly"
    ANNUAL = "Annual"
    MULTI_YEAR = "Multi-Year"


@dataclass
class KeyResult:
    kr_id: str
    description: str
    target_value: float
    current_value: float
    unit: str = ""
    weight: float = 1.0

    @property
    def progress(self) -> float:
        if self.target_value == 0:
            return 0
        return min(100, (self.current_value / self.target_value) * 100)


@dataclass
class StrategicGoal:
    goal_id: str
    title: str
    description: str
    category: GoalCategory
    owner: str
    start_date: date
    target_date: date
    key_results: List[KeyResult]
    priority: int = 1  # 1 = highest
    status: GoalStatus = GoalStatus.NOT_STARTED

    @property
    def progress(self) -> float:
        if not self.key_results:
            return 0
        total_weight = sum(kr.weight for kr in self.key_results)
        weighted_progress = sum(kr.progress * kr.weight for kr in self.key_results)
        return weighted_progress / total_weight if total_weight > 0 else 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "owner": self.owner,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "key_results": [
                {
                    "kr_id": kr.kr_id,
                    "description": kr.description,
                    "target": kr.target_value,
                    "current": kr.current_value,
                    "unit": kr.unit,
                    "progress": round(kr.progress, 1)
                }
                for kr in self.key_results
            ],
            "priority": self.priority,
            "status": self.status.value,
            "progress": round(self.progress, 1)
        }


@dataclass
class StrategicPlanReport:
    entity_id: str
    time_horizon: str
    total_goals: int
    on_track_count: int
    at_risk_count: int
    behind_count: int
    completed_count: int
    overall_progress: float
    goals_by_category: Dict[str, int]
    goals: List[StrategicGoal]
    priority_focus: List[str]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entity_id": self.entity_id,
            "time_horizon": self.time_horizon,
            "total_goals": self.total_goals,
            "on_track_count": self.on_track_count,
            "at_risk_count": self.at_risk_count,
            "behind_count": self.behind_count,
            "completed_count": self.completed_count,
            "overall_progress": round(self.overall_progress, 1),
            "goals_by_category": self.goals_by_category,
            "priority_focus": self.priority_focus,
            "recommendations": self.recommendations
        }


class StrategicPlanner:
    """Strategic planning and goal tracking engine."""

    def __init__(self):
        self.goals: List[StrategicGoal] = []

    def add_goal(self, goal: StrategicGoal):
        """Add a strategic goal."""
        self.goals.append(goal)

    def update_goal_status(self, goal: StrategicGoal) -> GoalStatus:
        """Determine goal status based on progress and timeline."""
        progress = goal.progress
        today = date.today()

        if goal.status == GoalStatus.COMPLETED:
            return GoalStatus.COMPLETED

        if goal.status == GoalStatus.CANCELLED:
            return GoalStatus.CANCELLED

        # Calculate expected progress based on timeline
        total_days = (goal.target_date - goal.start_date).days
        elapsed_days = (today - goal.start_date).days

        if total_days > 0 and elapsed_days > 0:
            expected_progress = (elapsed_days / total_days) * 100

            if progress >= expected_progress * 0.9:
                return GoalStatus.ON_TRACK
            elif progress >= expected_progress * 0.7:
                return GoalStatus.AT_RISK
            else:
                return GoalStatus.BEHIND

        if progress == 0:
            return GoalStatus.NOT_STARTED

        return GoalStatus.ON_TRACK

    def generate_report(self, goals: List[StrategicGoal] = None,
                        entity_id: str = "unknown",
                        time_horizon: TimeHorizon = TimeHorizon.QUARTERLY) -> StrategicPlanReport:
        """Generate strategic plan report."""
        goals = goals or self.goals

        # Update statuses
        for goal in goals:
            goal.status = self.update_goal_status(goal)

        # Count by status
        on_track = sum(1 for g in goals if g.status == GoalStatus.ON_TRACK)
        at_risk = sum(1 for g in goals if g.status == GoalStatus.AT_RISK)
        behind = sum(1 for g in goals if g.status == GoalStatus.BEHIND)
        completed = sum(1 for g in goals if g.status == GoalStatus.COMPLETED)

        # Overall progress
        overall = sum(g.progress for g in goals) / len(goals) if goals else 0

        # Goals by category
        by_category: Dict[str, int] = {}
        for g in goals:
            cat = g.category.value
            by_category[cat] = by_category.get(cat, 0) + 1

        # Priority focus (top priority goals that need attention)
        at_risk_goals = [g for g in goals if g.status in [GoalStatus.AT_RISK, GoalStatus.BEHIND]]
        at_risk_goals.sort(key=lambda x: x.priority)
        priority_focus = [f"P{g.priority}: {g.title}" for g in at_risk_goals[:5]]

        # Recommendations
        recommendations = self._generate_recommendations(goals, on_track, at_risk, behind)

        return StrategicPlanReport(
            entity_id=entity_id,
            time_horizon=time_horizon.value,
            total_goals=len(goals),
            on_track_count=on_track,
            at_risk_count=at_risk,
            behind_count=behind,
            completed_count=completed,
            overall_progress=overall,
            goals_by_category=by_category,
            goals=goals,
            priority_focus=priority_focus,
            recommendations=recommendations
        )

    def _generate_recommendations(self, goals: List[StrategicGoal],
                                  on_track: int, at_risk: int, behind: int) -> List[str]:
        """Generate strategic recommendations."""
        recs = []

        if behind > 0:
            recs.append(f"{behind} goals are behind schedule - review resource allocation")

        if at_risk > len(goals) * 0.3:
            recs.append("High number of at-risk goals - consider reprioritization")

        # Check for unbalanced category focus
        categories = {}
        for g in goals:
            cat = g.category.value
            categories[cat] = categories.get(cat, 0) + 1

        if "Growth" not in categories and "Profitability" not in categories:
            recs.append("Consider adding growth or profitability goals")

        if "People" not in categories:
            recs.append("Consider adding people and culture goals")

        return recs[:5]
