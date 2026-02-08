"""Demo Data Generator for Executive Intelligence"""
import random
from datetime import datetime, date, timedelta
from typing import Dict, Any, List


def generate_demo_data(org_name: str = "Demo Company") -> Dict[str, Any]:
    """Generate comprehensive demo data for Executive Intelligence."""

    org_id = f"demo-{random.randint(1000, 9999)}"

    return {
        'organization': generate_organization(org_id, org_name),
        'goals': generate_strategic_goals(org_id),
        'metrics': generate_executive_metrics(org_id),
        'board_reports': generate_board_reports(org_id),
    }


def generate_organization(org_id: str, name: str) -> Dict[str, Any]:
    """Generate demo organization."""
    industries = ['Technology', 'SaaS', 'E-commerce', 'FinTech', 'HealthTech']
    sizes = ['Startup', 'SMB', 'Mid-Market', 'Enterprise']
    stages = ['Early Stage', 'Growth', 'Scale-up', 'Mature']

    return {
        'id': org_id,
        'name': name,
        'industry': random.choice(industries),
        'size': random.choice(sizes),
        'stage': random.choice(stages),
        'fiscal_year_end': 'December',
    }


def generate_strategic_goals(org_id: str) -> List[Dict[str, Any]]:
    """Generate demo strategic goals with key results."""
    goal_templates = [
        {
            'title': 'Achieve $10M ARR',
            'category': 'Revenue',
            'priority': 1,
            'progress': random.uniform(60, 85),
            'key_results': [
                ('Close 50 enterprise deals', 50, random.randint(28, 42), 'deals'),
                ('Increase ACV to $25K', 25000, random.randint(18000, 24000), 'dollars'),
                ('Reduce sales cycle to 45 days', 45, random.randint(48, 62), 'days'),
            ]
        },
        {
            'title': 'Expand to European Market',
            'category': 'Growth',
            'priority': 2,
            'progress': random.uniform(30, 55),
            'key_results': [
                ('Hire EU sales team (5 people)', 5, random.randint(2, 4), 'hires'),
                ('Achieve GDPR compliance', 100, random.randint(70, 95), 'percent'),
                ('Sign 10 EU customers', 10, random.randint(3, 8), 'customers'),
            ]
        },
        {
            'title': 'Launch V2.0 Product',
            'category': 'Product',
            'priority': 1,
            'progress': random.uniform(50, 75),
            'key_results': [
                ('Complete core features', 100, random.randint(65, 90), 'percent'),
                ('Beta testing with 20 customers', 20, random.randint(12, 18), 'customers'),
                ('Achieve NPS of 50+', 50, random.randint(35, 55), 'score'),
            ]
        },
        {
            'title': 'Improve Customer Retention',
            'category': 'Customer Success',
            'priority': 2,
            'progress': random.uniform(45, 70),
            'key_results': [
                ('Reduce churn to 3%', 3, random.uniform(3.5, 5.5), 'percent'),
                ('Increase NPS to 60', 60, random.randint(45, 58), 'score'),
                ('Implement customer health scoring', 100, random.randint(60, 85), 'percent'),
            ]
        },
        {
            'title': 'Build World-Class Team',
            'category': 'People',
            'priority': 3,
            'progress': random.uniform(55, 80),
            'key_results': [
                ('Hire 25 new team members', 25, random.randint(15, 22), 'hires'),
                ('Achieve 80% employee engagement', 80, random.randint(68, 82), 'percent'),
                ('Reduce voluntary turnover to 10%', 10, random.uniform(11, 16), 'percent'),
            ]
        },
        {
            'title': 'Operational Excellence',
            'category': 'Operations',
            'priority': 3,
            'progress': random.uniform(40, 65),
            'key_results': [
                ('Achieve 99.9% uptime', 99.9, random.uniform(99.2, 99.8), 'percent'),
                ('Reduce support ticket resolution to 4 hours', 4, random.uniform(4.5, 7), 'hours'),
                ('Implement automated reporting', 100, random.randint(50, 80), 'percent'),
            ]
        },
    ]

    goals = []
    for template in goal_templates:
        start_date = date.today() - timedelta(days=random.randint(60, 180))
        target_date = date.today() + timedelta(days=random.randint(30, 180))

        status_map = {
            (0, 30): 'At Risk',
            (30, 50): 'Behind',
            (50, 70): 'On Track',
            (70, 100): 'Ahead',
        }

        progress = template['progress']
        status = 'On Track'
        for (low, high), s in status_map.items():
            if low <= progress < high:
                status = s
                break

        goal = {
            'id': f"goal-{random.randint(10000, 99999)}",
            'organization_id': org_id,
            'title': template['title'],
            'description': f"Strategic initiative to {template['title'].lower()}",
            'category': template['category'],
            'owner': random.choice(['CEO', 'CTO', 'CFO', 'VP Sales', 'VP Product', 'VP Engineering']),
            'priority': template['priority'],
            'status': status,
            'start_date': start_date.isoformat(),
            'target_date': target_date.isoformat(),
            'progress': round(progress, 1),
            'key_results': [],
        }

        for kr_desc, target, current, unit in template['key_results']:
            goal['key_results'].append({
                'id': f"kr-{random.randint(10000, 99999)}",
                'description': kr_desc,
                'target_value': target,
                'current_value': current,
                'unit': unit,
                'progress': round((current / target) * 100, 1) if target else 0,
            })

        goals.append(goal)

    return goals


def generate_executive_metrics(org_id: str) -> List[Dict[str, Any]]:
    """Generate demo executive metrics over multiple periods."""
    metrics_list = []

    base_revenue = random.uniform(500000, 1500000)
    base_customers = random.randint(150, 400)
    base_employees = random.randint(30, 80)

    for i in range(6):  # Last 6 months
        period_date = date.today() - timedelta(days=30 * (5 - i))

        revenue = base_revenue * (1 + 0.08 * i + random.uniform(-0.02, 0.05))
        customers = int(base_customers * (1 + 0.05 * i))
        employees = int(base_employees * (1 + 0.03 * i))

        metrics_list.append({
            'id': f"metr-{random.randint(10000, 99999)}",
            'organization_id': org_id,
            'period': 'monthly',
            'period_date': period_date.isoformat(),

            # Financial
            'revenue': round(revenue, 2),
            'revenue_growth': round(random.uniform(5, 15), 1),
            'gross_margin': round(random.uniform(65, 78), 1),
            'operating_margin': round(random.uniform(-10, 15), 1),
            'cash_position': round(random.uniform(2000000, 8000000), 2),
            'burn_rate': round(random.uniform(200000, 500000), 2),

            # Customer
            'customer_count': customers,
            'customer_growth': round(random.uniform(3, 12), 1),
            'nps': round(random.uniform(35, 65), 0),
            'churn_rate': round(random.uniform(2, 6), 1),

            # People
            'employee_count': employees,
            'employee_engagement': round(random.uniform(65, 85), 1),
            'voluntary_turnover': round(random.uniform(8, 18), 1),

            # Health scores
            'overall_health': round(random.uniform(60, 85), 1),
            'financial_health': round(random.uniform(55, 90), 1),
            'operational_health': round(random.uniform(60, 85), 1),
            'customer_health': round(random.uniform(65, 90), 1),
            'people_health': round(random.uniform(60, 80), 1),
        })

    return metrics_list


def generate_board_reports(org_id: str) -> List[Dict[str, Any]]:
    """Generate demo board reports."""
    reports = []

    for i in range(3):  # Last 3 quarters
        period_date = date.today() - timedelta(days=90 * (2 - i))

        reports.append({
            'id': f"board-{random.randint(10000, 99999)}",
            'organization_id': org_id,
            'period': 'quarterly',
            'period_date': period_date.isoformat(),
            'executive_summary': f"""
Q{((period_date.month - 1) // 3) + 1} was a strong quarter with continued momentum across key initiatives.
Revenue grew {random.randint(8, 15)}% QoQ, driven by enterprise sales.
Product V2.0 development is on track for Q{((period_date.month - 1) // 3) + 2} launch.
Team scaled from {random.randint(40, 50)} to {random.randint(50, 65)} employees.
Key challenges include competitive pressure and talent acquisition in engineering.
            """.strip(),
            'key_achievements': [
                f"Closed {random.randint(10, 20)} new enterprise customers",
                f"Revenue reached ${random.randint(800, 1200)}K (up {random.randint(8, 15)}% QoQ)",
                "Successfully launched new analytics feature",
                f"NPS improved to {random.randint(45, 60)} (up {random.randint(5, 12)} points)",
                f"Hired {random.randint(8, 15)} key team members",
            ],
            'challenges': [
                "Enterprise sales cycle longer than expected",
                "Engineering hiring velocity below target",
                "Churn slightly elevated in SMB segment",
            ],
            'priorities': [
                "Close Series B funding round",
                "Launch V2.0 product",
                "Expand enterprise sales team",
                "Improve customer onboarding",
            ],
            'board_asks': [
                "Approve Series B term sheet",
                "Introduce potential enterprise customers",
                "Guidance on EU expansion timing",
            ],
        })

    return reports


def load_demo_data_to_db(db, models, org_name: str = "TechVenture Corp"):
    """Load demo data into the database."""
    data = generate_demo_data(org_name)

    # Create organization
    org = models.Organization(
        id=data['organization']['id'],
        name=data['organization']['name'],
        industry=data['organization']['industry'],
        size=data['organization']['size'],
        stage=data['organization']['stage'],
        fiscal_year_end=data['organization']['fiscal_year_end'],
    )
    db.session.add(org)

    # Create goals with key results
    for g in data['goals']:
        from datetime import date
        goal = models.StrategicGoal(
            id=g['id'],
            organization_id=g['organization_id'],
            title=g['title'],
            description=g['description'],
            category=g['category'],
            owner=g['owner'],
            priority=g['priority'],
            status=g['status'],
            start_date=date.fromisoformat(g['start_date']),
            target_date=date.fromisoformat(g['target_date']),
            progress=g['progress'],
        )
        db.session.add(goal)

        # Add key results
        for kr in g['key_results']:
            key_result = models.KeyResult(
                id=kr['id'],
                goal_id=g['id'],
                description=kr['description'],
                target_value=kr['target_value'],
                current_value=kr['current_value'],
                unit=kr['unit'],
            )
            db.session.add(key_result)

    # Create metrics
    for m in data['metrics']:
        from datetime import date
        metrics = models.ExecutiveMetrics(
            id=m['id'],
            organization_id=m['organization_id'],
            period=m['period'],
            period_date=date.fromisoformat(m['period_date']),
            revenue=m['revenue'],
            revenue_growth=m['revenue_growth'],
            gross_margin=m['gross_margin'],
            operating_margin=m['operating_margin'],
            cash_position=m['cash_position'],
            burn_rate=m['burn_rate'],
            customer_count=m['customer_count'],
            customer_growth=m['customer_growth'],
            nps=m['nps'],
            churn_rate=m['churn_rate'],
            employee_count=m['employee_count'],
            employee_engagement=m['employee_engagement'],
            voluntary_turnover=m['voluntary_turnover'],
            overall_health=m['overall_health'],
            financial_health=m['financial_health'],
            operational_health=m['operational_health'],
            customer_health=m['customer_health'],
            people_health=m['people_health'],
        )
        db.session.add(metrics)

    # Create board reports
    for b in data['board_reports']:
        from datetime import date
        report = models.BoardReport(
            id=b['id'],
            organization_id=b['organization_id'],
            period=b['period'],
            period_date=date.fromisoformat(b['period_date']),
            executive_summary=b['executive_summary'],
            key_achievements=b['key_achievements'],
            challenges=b['challenges'],
            priorities=b['priorities'],
            board_asks=b['board_asks'],
        )
        db.session.add(report)

    db.session.commit()

    return data['organization']['id']
