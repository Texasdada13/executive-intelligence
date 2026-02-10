"""Comprehensive tests for Executive Intelligence"""
import sys
import os
from datetime import date, timedelta
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_all():
    results = []

    # Test 1: Imports
    print("=" * 60)
    print("EXECUTIVE INTELLIGENCE TEST SUITE")
    print("=" * 60)

    try:
        from src.patterns.executive_scoring import ExecutiveScoringEngine, create_business_health_engine, BusinessDomain
        from src.patterns.strategic_planner import StrategicPlanner, StrategicGoal, KeyResult, GoalCategory, GoalStatus, TimeHorizon
        from src.executive.dashboard_aggregator import DashboardAggregator, CSuiteRole
        from src.executive.board_reporter import BoardReporter, ReportPeriod
        print("[PASS] All imports successful")
        results.append(("Imports", True))
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        results.append(("Imports", False))
        return results

    # Test 2: Business Health Scoring
    print("\n" + "-" * 40)
    print("Test: Business Health Scoring")
    try:
        engine = create_business_health_engine()
        report = engine.calculate_health({
            "revenue_growth": {"score": 85, "previous_score": 80},
            "profitability": {"score": 78, "previous_score": 75},
            "cash_flow": {"score": 82},
            "financial_efficiency": {"score": 70},
            "operational_efficiency": {"score": 75},
            "quality_metrics": {"score": 80},
            "customer_satisfaction": {"score": 88},
            "customer_retention": {"score": 85},
            "market_share": {"score": 60},
            "employee_engagement": {"score": 72},
            "talent_retention": {"score": 68},
            "tech_health": {"score": 75},
            "innovation": {"score": 65},
            "security_posture": {"score": 80},
            "compliance_status": {"score": 85}
        }, "org-001")
        print(f"  Overall Score: {report.overall_score:.1f}")
        print(f"  Grade: {report.overall_grade}")
        print(f"  Status: {report.overall_status}")
        print(f"  Domains: {len(report.domain_scores)}")
        print(f"  Strengths: {len(report.strengths)}")
        print("[PASS] Business Health Scoring")
        results.append(("Business Health", True))
    except Exception as e:
        print(f"[FAIL] Business Health: {e}")
        results.append(("Business Health", False))

    # Test 3: Strategic Planning
    print("\n" + "-" * 40)
    print("Test: Strategic Planning")
    try:
        planner = StrategicPlanner()
        today = date.today()
        goals = [
            StrategicGoal(
                goal_id="goal-001",
                title="Increase ARR by 50%",
                description="Annual recurring revenue growth",
                category=GoalCategory.GROWTH,
                owner="CEO",
                start_date=today - timedelta(days=60),
                target_date=today + timedelta(days=120),
                key_results=[
                    KeyResult("kr1", "Acquire 100 new customers", 100, 65),
                    KeyResult("kr2", "Increase ACV to $50K", 50000, 42000),
                    KeyResult("kr3", "Reduce churn to 5%", 5, 7)
                ],
                priority=1
            ),
            StrategicGoal(
                goal_id="goal-002",
                title="Improve Customer NPS",
                description="Customer satisfaction improvement",
                category=GoalCategory.CUSTOMER,
                owner="COO",
                start_date=today - timedelta(days=30),
                target_date=today + timedelta(days=60),
                key_results=[
                    KeyResult("kr1", "NPS score of 50+", 50, 45),
                    KeyResult("kr2", "Response time < 2hrs", 2, 2.5)
                ],
                priority=2
            ),
            StrategicGoal(
                goal_id="goal-003",
                title="Launch New Product",
                description="New product launch",
                category=GoalCategory.GROWTH,
                owner="CTO",
                start_date=today - timedelta(days=90),
                target_date=today + timedelta(days=30),
                key_results=[
                    KeyResult("kr1", "Complete development", 100, 85),
                    KeyResult("kr2", "Beta customers", 10, 8)
                ],
                priority=1
            )
        ]
        report = planner.generate_report(goals, "org-001", TimeHorizon.QUARTERLY)
        print(f"  Total Goals: {report.total_goals}")
        print(f"  On Track: {report.on_track_count}")
        print(f"  At Risk: {report.at_risk_count}")
        print(f"  Overall Progress: {report.overall_progress:.1f}%")
        print(f"  Categories: {len(report.goals_by_category)}")
        print("[PASS] Strategic Planning")
        results.append(("Strategic Planning", True))
    except Exception as e:
        print(f"[FAIL] Strategic Planning: {e}")
        results.append(("Strategic Planning", False))

    # Test 4: C-Suite Dashboard Aggregation
    print("\n" + "-" * 40)
    print("Test: C-Suite Dashboard Aggregation")
    try:
        aggregator = DashboardAggregator()
        role_data = {
            CSuiteRole.CFO: {
                "health_score": 82,
                "key_metrics": {"revenue_growth": 25, "margin": 35},
                "alerts": ["Cash runway below 12 months"],
                "priorities": ["Secure Series B funding"]
            },
            CSuiteRole.CTO: {
                "health_score": 78,
                "key_metrics": {"uptime": 99.9, "tech_debt": "medium"},
                "alerts": [],
                "priorities": ["Complete platform migration"]
            },
            CSuiteRole.COO: {
                "health_score": 85,
                "key_metrics": {"efficiency": 92, "quality": 95},
                "alerts": [],
                "priorities": ["Scale operations for growth"]
            },
            CSuiteRole.CHRO: {
                "health_score": 72,
                "key_metrics": {"engagement": 75, "retention": 88},
                "alerts": ["Engineering turnover elevated"],
                "priorities": ["Improve retention programs"]
            },
            CSuiteRole.CMO: {
                "health_score": 80,
                "key_metrics": {"pipeline": 5000000, "cac": 1200},
                "alerts": [],
                "priorities": ["Launch brand campaign"]
            },
            CSuiteRole.CISO: {
                "health_score": 75,
                "key_metrics": {"security_score": 78, "compliance": 85},
                "alerts": ["SOC2 audit in 60 days"],
                "priorities": ["Complete SOC2 preparation"]
            }
        }
        metrics = aggregator.aggregate_metrics(role_data, "org-001", previous_health=78)
        print(f"  Overall Health: {metrics.overall_health:.1f}")
        print(f"  Grade: {metrics.overall_grade}")
        print(f"  Roles Tracked: {len(metrics.role_metrics)}")
        print(f"  Trend: {metrics.trend}")
        print(f"  Critical Alerts: {len(metrics.critical_alerts)}")
        print(f"  Cross-Functional Insights: {len(metrics.cross_functional_insights)}")
        print("[PASS] C-Suite Dashboard")
        results.append(("C-Suite Dashboard", True))
    except Exception as e:
        print(f"[FAIL] C-Suite Dashboard: {e}")
        results.append(("C-Suite Dashboard", False))

    # Test 5: Board Reporting
    print("\n" + "-" * 40)
    print("Test: Board Reporting")
    try:
        reporter = BoardReporter()
        business_data = {
            "revenue": 5000000,
            "revenue_growth": 28,
            "gross_margin": 72,
            "operating_margin": 15,
            "cash": 8000000,
            "burn_rate": 400000,
            "runway": 20,
            "customers": 250,
            "customer_growth": 35,
            "nps": 55,
            "churn": 4.5,
            "employees": 85,
            "engagement": 78,
            "goals_on_track": 8,
            "goals_at_risk": 2,
            "strategic_progress": 72,
            "achievements": [
                "Closed Series A funding",
                "Launched enterprise product",
                "Achieved SOC2 Type II"
            ],
            "challenges": [
                "Sales cycle lengthening",
                "Engineering hiring competitive"
            ],
            "priorities": [
                "Scale sales team",
                "International expansion",
                "Platform reliability"
            ],
            "board_asks": [
                "Approve Series B exploration",
                "Board member introductions for enterprise sales"
            ]
        }
        report = reporter.generate_report(
            business_data,
            period=ReportPeriod.QUARTERLY,
            organization_id="org-001"
        )
        print(f"  Period: {report.period.value}")
        print(f"  Revenue: ${report.financial_highlights.revenue:,.0f}")
        print(f"  Growth: {report.financial_highlights.revenue_growth:.0f}%")
        print(f"  Runway: {report.financial_highlights.runway_months:.0f} months")
        print(f"  Customers: {report.operational_highlights.customer_count}")
        print(f"  NPS: {report.operational_highlights.nps:.0f}")
        print(f"  Achievements: {len(report.key_achievements)}")
        print("[PASS] Board Reporting")
        results.append(("Board Reporting", True))
    except Exception as e:
        print(f"[FAIL] Board Reporting: {e}")
        results.append(("Board Reporting", False))

    # Test 6: Goal Status Calculation
    print("\n" + "-" * 40)
    print("Test: Goal Status Calculation")
    try:
        planner = StrategicPlanner()
        today = date.today()

        # On-track goal (80% progress, 60% time elapsed)
        on_track_goal = StrategicGoal(
            goal_id="test-1", title="On Track Goal", description="Test",
            category=GoalCategory.GROWTH, owner="CEO",
            start_date=today - timedelta(days=60),
            target_date=today + timedelta(days=40),
            key_results=[KeyResult("kr1", "Target 100", 100, 80)],
            priority=1
        )

        # Behind goal (20% progress, 80% time elapsed)
        behind_goal = StrategicGoal(
            goal_id="test-2", title="Behind Goal", description="Test",
            category=GoalCategory.PROFITABILITY, owner="CFO",
            start_date=today - timedelta(days=80),
            target_date=today + timedelta(days=20),
            key_results=[KeyResult("kr1", "Target 100", 100, 20)],
            priority=1
        )

        on_track_status = planner.update_goal_status(on_track_goal)
        behind_status = planner.update_goal_status(behind_goal)

        print(f"  On-Track Goal Progress: {on_track_goal.progress:.1f}%")
        print(f"  On-Track Goal Status: {on_track_status.value}")
        print(f"  Behind Goal Progress: {behind_goal.progress:.1f}%")
        print(f"  Behind Goal Status: {behind_status.value}")

        assert on_track_status == GoalStatus.ON_TRACK, f"Expected ON_TRACK, got {on_track_status}"
        assert behind_status == GoalStatus.BEHIND, f"Expected BEHIND, got {behind_status}"
        print("[PASS] Goal Status Calculation")
        results.append(("Goal Status", True))
    except Exception as e:
        print(f"[FAIL] Goal Status: {e}")
        results.append(("Goal Status", False))

    # Test 7: Domain Score Aggregation
    print("\n" + "-" * 40)
    print("Test: Domain Score Aggregation")
    try:
        engine = create_business_health_engine()
        report = engine.calculate_health({
            "revenue_growth": {"score": 90},
            "profitability": {"score": 85},
            "cash_flow": {"score": 88},
            "financial_efficiency": {"score": 82},
            "customer_satisfaction": {"score": 75},
            "customer_retention": {"score": 70},
            "employee_engagement": {"score": 60},
            "tech_health": {"score": 70}
        }, "test-org")

        print(f"  Financial Domain: {report.domain_scores.get('Financial Health', 0):.1f}")
        print(f"  Customer Domain: {report.domain_scores.get('Customer Success', 0):.1f}")
        print(f"  People Domain: {report.domain_scores.get('People & Culture', 0):.1f}")
        print(f"  Technology Domain: {report.domain_scores.get('Technology & Innovation', 0):.1f}")

        # Verify financial domain is highest
        financial_score = report.domain_scores.get("Financial Health", 0)
        assert financial_score > 80, "Financial domain should be high with given scores"
        print("[PASS] Domain Score Aggregation")
        results.append(("Domain Aggregation", True))
    except Exception as e:
        print(f"[FAIL] Domain Aggregation: {e}")
        results.append(("Domain Aggregation", False))

    # Test 8: Executive Summary Generation
    print("\n" + "-" * 40)
    print("Test: Executive Summary Generation")
    try:
        reporter = BoardReporter()

        # Strong performance scenario
        strong_data = {
            "revenue": 10000000,
            "revenue_growth": 45,
            "cash": 20000000,
            "runway": 24,
            "customers": 500,
            "nps": 65,
            "strategic_progress": 85
        }
        strong_report = reporter.generate_report(strong_data, organization_id="strong-org")

        # Challenged scenario
        challenged_data = {
            "revenue": 2000000,
            "revenue_growth": -5,
            "cash": 1000000,
            "runway": 4,
            "customers": 100,
            "nps": 15,
            "strategic_progress": 35
        }
        challenged_report = reporter.generate_report(challenged_data, organization_id="challenged-org")

        print(f"  Strong Summary: {strong_report.executive_summary[:60]}...")
        print(f"  Challenged Summary: {challenged_report.executive_summary[:60]}...")

        assert "Strong" in strong_report.executive_summary or "growth" in strong_report.executive_summary.lower()
        assert "runway" in challenged_report.executive_summary.lower() or "decline" in challenged_report.executive_summary.lower()
        print("[PASS] Executive Summary Generation")
        results.append(("Executive Summary", True))
    except Exception as e:
        print(f"[FAIL] Executive Summary: {e}")
        results.append(("Executive Summary", False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, p in results if p)
    total = len(results)
    for name, passed_test in results:
        status = "[PASS]" if passed_test else "[FAIL]"
        print(f"  {status} {name}")
    print("-" * 40)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)

    return results

if __name__ == "__main__":
    test_all()
