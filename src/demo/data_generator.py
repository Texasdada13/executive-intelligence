"""Demo Data Generator for Executive Intelligence"""
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid


class ExecutiveDemoGenerator:
    """Generates realistic demo data for Executive Intelligence product."""

    GOAL_CATEGORIES = [
        'Revenue Growth', 'Customer Acquisition', 'Product Development',
        'Market Expansion', 'Operational Excellence', 'Talent Development',
        'Digital Transformation', 'Cost Optimization', 'Brand Building',
        'Partnership Development', 'Innovation', 'Sustainability'
    ]

    CSUITE_FUNCTIONS = [
        ('CEO', 'Chief Executive Officer'),
        ('CFO', 'Chief Financial Officer'),
        ('CTO', 'Chief Technology Officer'),
        ('CMO', 'Chief Marketing Officer'),
        ('COO', 'Chief Operating Officer'),
        ('CHRO', 'Chief Human Resources Officer'),
        ('CSO', 'Chief Strategy Officer'),
        ('CPO', 'Chief Product Officer')
    ]

    INDUSTRIES = [
        'Technology', 'Healthcare', 'Financial Services', 'Retail',
        'Manufacturing', 'Professional Services', 'Media', 'Energy'
    ]

    RISK_CATEGORIES = [
        'Market Competition', 'Economic Downturn', 'Talent Shortage',
        'Technology Disruption', 'Regulatory Changes', 'Supply Chain',
        'Cybersecurity', 'Reputation', 'Customer Concentration'
    ]

    def __init__(self, seed: Optional[int] = None):
        if seed:
            random.seed(seed)

    def generate_organization(self, name: str = None) -> Dict[str, Any]:
        """Generate a demo organization."""
        name = name or f"Enterprise Corp {random.randint(1000, 9999)}"
        annual_revenue = random.randint(5000000, 500000000)

        return {
            'id': str(uuid.uuid4()),
            'name': name,
            'industry': random.choice(self.INDUSTRIES),
            'annual_revenue': annual_revenue,
            'employee_count': random.randint(50, 5000),
            'founding_year': random.randint(1990, 2020),
            'growth_stage': random.choice(['startup', 'growth', 'scale-up', 'enterprise']),
            'fiscal_year_end': random.choice(['December', 'March', 'June', 'September']),
            'created_at': datetime.utcnow().isoformat()
        }

    def generate_strategic_goals(self, org_id: str, count: int = 6) -> List[Dict[str, Any]]:
        """Generate strategic goals/OKRs."""
        goals = []
        selected_categories = random.sample(self.GOAL_CATEGORIES, min(count, len(self.GOAL_CATEGORIES)))

        for i, category in enumerate(selected_categories):
            target = random.randint(10, 100)
            progress = random.randint(0, 120)  # Can exceed target
            start_date = datetime.utcnow() - timedelta(days=random.randint(30, 180))

            # Determine status based on progress and time elapsed
            days_elapsed = (datetime.utcnow() - start_date).days
            expected_progress = min(100, (days_elapsed / 365) * 100 * 1.2)  # Expected linear progress

            if progress >= target:
                status = 'completed'
            elif progress >= expected_progress * 0.9:
                status = 'on_track'
            elif progress >= expected_progress * 0.6:
                status = 'behind'
            else:
                status = 'at_risk'

            goals.append({
                'id': str(uuid.uuid4()),
                'organization_id': org_id,
                'title': f"{category} Initiative",
                'category': category,
                'description': f"Strategic initiative focused on {category.lower()}",
                'target': target,
                'current': min(progress, 150),  # Cap display at 150%
                'progress_percentage': round(min(progress / target * 100, 150), 1),
                'status': status,
                'priority': random.choice(['critical', 'high', 'medium']),
                'owner': random.choice([f[0] for f in self.CSUITE_FUNCTIONS]),
                'start_date': start_date.isoformat(),
                'target_date': (start_date + timedelta(days=random.randint(180, 365))).isoformat(),
                'key_results': random.randint(2, 5),
                'key_results_complete': random.randint(0, 4)
            })

        return goals

    def generate_financial_metrics(self, org: Dict) -> Dict[str, Any]:
        """Generate financial performance metrics."""
        annual_revenue = org['annual_revenue']
        monthly_revenue = annual_revenue / 12

        # Generate realistic financial metrics
        gross_margin = random.uniform(0.35, 0.75)
        operating_margin = gross_margin - random.uniform(0.15, 0.35)
        net_margin = operating_margin - random.uniform(0.05, 0.15)

        revenue_growth = random.uniform(-0.1, 0.5)
        burn_rate = monthly_revenue * random.uniform(0.3, 0.9) if net_margin < 0.1 else 0
        runway_months = (annual_revenue * 0.2) / burn_rate if burn_rate > 0 else 999

        return {
            'annual_revenue': annual_revenue,
            'monthly_revenue': round(monthly_revenue),
            'revenue_growth': round(revenue_growth * 100, 1),
            'gross_margin': round(gross_margin * 100, 1),
            'operating_margin': round(operating_margin * 100, 1),
            'net_margin': round(net_margin * 100, 1),
            'burn_rate': round(burn_rate) if burn_rate > 0 else 0,
            'runway_months': min(round(runway_months), 36) if burn_rate > 0 else None,
            'cash_position': round(annual_revenue * random.uniform(0.1, 0.5)),
            'arr': round(annual_revenue * random.uniform(0.6, 1.2)) if random.choice([True, False]) else None,
            'mrr': round(monthly_revenue * random.uniform(0.7, 1.3)),
            'customer_ltv': round(random.randint(5000, 100000)),
            'cac': round(random.randint(1000, 20000)),
            'ltv_cac_ratio': round(random.uniform(2.0, 8.0), 1),
            'period': 'current_quarter',
            'generated_at': datetime.utcnow().isoformat()
        }

    def generate_customer_metrics(self) -> Dict[str, Any]:
        """Generate customer performance metrics."""
        total_customers = random.randint(100, 10000)
        enterprise_pct = random.uniform(0.1, 0.4)

        return {
            'total_customers': total_customers,
            'enterprise_customers': int(total_customers * enterprise_pct),
            'smb_customers': int(total_customers * (1 - enterprise_pct)),
            'nps': random.randint(15, 80),
            'csat': round(random.uniform(3.5, 4.8), 1),
            'churn_rate': round(random.uniform(2, 15), 1),
            'retention_rate': round(100 - random.uniform(2, 15), 1),
            'growth': round(random.uniform(-5, 30), 1),
            'avg_contract_value': random.randint(10000, 200000),
            'expansion_revenue_pct': round(random.uniform(10, 40), 1),
            'customer_health_score': random.randint(60, 95),
            'at_risk_accounts': random.randint(0, int(total_customers * 0.1)),
            'period': 'current_quarter'
        }

    def generate_people_metrics(self, org: Dict) -> Dict[str, Any]:
        """Generate workforce metrics."""
        employee_count = org['employee_count']

        return {
            'total_employees': employee_count,
            'new_hires_ytd': random.randint(int(employee_count * 0.05), int(employee_count * 0.25)),
            'departures_ytd': random.randint(int(employee_count * 0.03), int(employee_count * 0.15)),
            'turnover': round(random.uniform(8, 25), 1),
            'engagement': random.randint(55, 90),
            'enps': random.randint(-10, 60),
            'open_positions': random.randint(int(employee_count * 0.02), int(employee_count * 0.1)),
            'time_to_hire_days': random.randint(30, 90),
            'offer_acceptance_rate': round(random.uniform(0.7, 0.95) * 100, 1),
            'diversity_score': random.randint(40, 80),
            'training_hours_per_employee': random.randint(10, 50),
            'performance_rating_avg': round(random.uniform(3.2, 4.5), 1),
            'period': 'current_year'
        }

    def generate_csuite_health(self) -> Dict[str, Dict[str, Any]]:
        """Generate C-Suite function health scores."""
        csuite = {}

        for abbrev, title in self.CSUITE_FUNCTIONS:
            health_score = random.randint(45, 95)
            csuite[abbrev.lower()] = {
                'title': title,
                'abbreviation': abbrev,
                'health_score': health_score,
                'status': 'excellent' if health_score >= 85 else 'good' if health_score >= 70 else 'needs_attention' if health_score >= 50 else 'critical',
                'key_initiatives': random.randint(2, 6),
                'initiatives_on_track': random.randint(1, 5),
                'team_size': random.randint(5, 50),
                'budget_utilization': round(random.uniform(0.6, 1.1) * 100, 1),
                'key_metrics_meeting_target': random.randint(3, 8),
                'key_metrics_total': random.randint(5, 10)
            }

        return csuite

    def generate_risks(self, org_id: str, count: int = 6) -> List[Dict[str, Any]]:
        """Generate enterprise risk register."""
        risks = []
        selected_categories = random.sample(self.RISK_CATEGORIES, min(count, len(self.RISK_CATEGORIES)))

        for category in selected_categories:
            likelihood = random.randint(1, 5)
            impact = random.randint(1, 5)
            score = likelihood * impact

            risks.append({
                'id': str(uuid.uuid4()),
                'organization_id': org_id,
                'category': category,
                'title': f"{category} Risk",
                'description': f"Enterprise risk related to {category.lower()}",
                'likelihood': likelihood,
                'impact': impact,
                'score': score,
                'severity': 'critical' if score >= 20 else 'high' if score >= 12 else 'medium' if score >= 6 else 'low',
                'status': random.choice(['identified', 'mitigating', 'monitoring', 'accepted']),
                'owner': random.choice([f[0] for f in self.CSUITE_FUNCTIONS]),
                'mitigation_plan': random.choice([True, True, False]),
                'last_reviewed': (datetime.utcnow() - timedelta(days=random.randint(1, 60))).isoformat()
            })

        return risks

    def generate_board_info(self) -> Dict[str, Any]:
        """Generate board meeting and governance info."""
        next_meeting = datetime.utcnow() + timedelta(days=random.randint(7, 60))

        return {
            'next_meeting_date': next_meeting.isoformat(),
            'days_until_meeting': (next_meeting - datetime.utcnow()).days,
            'board_members': random.randint(5, 9),
            'committees': random.randint(2, 4),
            'pending_approvals': random.randint(0, 3),
            'last_meeting_date': (datetime.utcnow() - timedelta(days=random.randint(30, 90))).isoformat(),
            'quarterly_report_status': random.choice(['draft', 'in_review', 'ready', 'pending'])
        }

    def generate_metrics_summary(
        self,
        goals: List[Dict],
        financial: Dict,
        customers: Dict,
        people: Dict,
        csuite: Dict
    ) -> Dict[str, Any]:
        """Generate overall executive dashboard summary."""
        goals_at_risk = len([g for g in goals if g['status'] == 'at_risk'])
        goals_behind = len([g for g in goals if g['status'] == 'behind'])
        goals_on_track = len([g for g in goals if g['status'] in ['on_track', 'completed']])

        avg_goal_progress = sum(g['progress_percentage'] for g in goals) / len(goals) if goals else 0

        # Calculate overall health score
        financial_score = min(100, max(0, 50 + financial['revenue_growth'] + financial['net_margin']))
        customer_score = min(100, customers['nps'] + (100 - customers['churn_rate'] * 3))
        people_score = people['engagement']
        goal_score = (goals_on_track / len(goals) * 100) if goals else 50
        csuite_score = sum(f['health_score'] for f in csuite.values()) / len(csuite)

        overall_health = int((
            financial_score * 0.25 +
            customer_score * 0.20 +
            people_score * 0.15 +
            goal_score * 0.25 +
            csuite_score * 0.15
        ))

        return {
            'overall_health': min(100, max(0, overall_health)),
            'health_grade': 'A' if overall_health >= 85 else 'B' if overall_health >= 70 else 'C' if overall_health >= 55 else 'D' if overall_health >= 40 else 'F',
            'goals_summary': {
                'total': len(goals),
                'at_risk': goals_at_risk,
                'behind': goals_behind,
                'on_track': goals_on_track,
                'overall_progress': round(avg_goal_progress, 1)
            },
            'financial_health': round(financial_score),
            'customer_health': round(customer_score),
            'people_health': people_score,
            'csuite_avg_health': round(csuite_score),
            'top_priority': goals[0]['category'] if goals else None,
            'key_focus_areas': [g['category'] for g in sorted(goals, key=lambda x: x['progress_percentage'])[:3]],
            'generated_at': datetime.utcnow().isoformat()
        }

    def generate_full_demo(self, org_name: str = None) -> Dict[str, Any]:
        """Generate complete demo dataset."""
        org = self.generate_organization(org_name)
        goals = self.generate_strategic_goals(org['id'])
        financial = self.generate_financial_metrics(org)
        customers = self.generate_customer_metrics()
        people = self.generate_people_metrics(org)
        csuite = self.generate_csuite_health()
        risks = self.generate_risks(org['id'])
        board = self.generate_board_info()
        metrics = self.generate_metrics_summary(goals, financial, customers, people, csuite)

        return {
            'organization': org,
            'strategic_goals': goals,
            'financial_metrics': financial,
            'customer_metrics': customers,
            'people_metrics': people,
            'csuite_health': csuite,
            'risks': risks,
            'board_info': board,
            'metrics_summary': metrics,
            'context_for_ai': self._build_ai_context(metrics, goals, financial, customers, people, csuite, board, risks)
        }

    def _build_ai_context(
        self,
        metrics: Dict,
        goals: List[Dict],
        financial: Dict,
        customers: Dict,
        people: Dict,
        csuite: Dict,
        board: Dict,
        risks: List[Dict]
    ) -> Dict[str, Any]:
        """Build context dictionary for AI suggestion engine."""
        return {
            'overall_health': metrics['overall_health'],
            'goals': {
                'at_risk': metrics['goals_summary']['at_risk'],
                'behind': metrics['goals_summary']['behind'],
                'overall_progress': metrics['goals_summary']['overall_progress']
            },
            'financial': {
                'runway_months': financial.get('runway_months', 999),
                'revenue_growth': financial['revenue_growth'],
                'gross_margin': financial['gross_margin'],
                'burn_rate': financial['burn_rate'],
                'revenue': financial['annual_revenue']
            },
            'customers': {
                'nps': customers['nps'],
                'churn_rate': customers['churn_rate'],
                'growth': customers['growth']
            },
            'people': {
                'engagement': people['engagement'],
                'turnover': people['turnover']
            },
            'csuite': csuite,
            'board': {
                'days_until_meeting': board['days_until_meeting']
            },
            'risks': [{'severity': r['severity']} for r in risks if r['severity'] == 'critical']
        }


def create_executive_demo_generator(seed: int = None) -> ExecutiveDemoGenerator:
    """Factory function to create demo generator."""
    return ExecutiveDemoGenerator(seed)
