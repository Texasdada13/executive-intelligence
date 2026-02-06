"""Report generator for Executive Intelligence dashboards."""
import csv
import io
from datetime import datetime
from typing import Dict, List, Any, Optional


class ReportGenerator:
    """Generate exportable reports from executive data."""

    def __init__(self):
        self.product_name = "Executive Intelligence"
        self.product_color = "#fd7e14"  # Orange/Gold

    def generate_csv(self, data: Dict[str, Any], report_type: str = 'full') -> str:
        """Generate CSV report from dashboard data."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([f'{self.product_name} Report'])
        writer.writerow([f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
        writer.writerow([])

        if report_type in ['full', 'health']:
            # Business Health
            health = data.get('health', {})
            writer.writerow(['BUSINESS HEALTH'])
            writer.writerow(['Overall Grade', health.get('grade', 'N/A')])
            writer.writerow(['Health Score', f"{health.get('score', 0)}/100"])
            writer.writerow([])

            # C-Suite Health Scores
            writer.writerow(['C-SUITE HEALTH SCORES'])
            writer.writerow(['Executive', 'Score'])
            csuite = health.get('csuite_scores', {})
            for role, score in csuite.items():
                writer.writerow([role.upper(), f"{score}/100"])
            writer.writerow([])

        if report_type in ['full', 'goals']:
            # Strategic Goals
            goals_data = data.get('goals', {})
            writer.writerow(['STRATEGIC GOALS SUMMARY'])
            writer.writerow(['Total Goals', goals_data.get('total', 0)])
            writer.writerow(['On Track', goals_data.get('on_track', 0)])
            writer.writerow(['At Risk', goals_data.get('at_risk', 0)])
            writer.writerow(['Behind', goals_data.get('behind', 0)])
            writer.writerow([])

            writer.writerow(['GOAL DETAILS'])
            writer.writerow(['Goal', 'Category', 'Progress', 'Status', 'Priority'])
            for goal in goals_data.get('items', []):
                writer.writerow([
                    goal.get('title', ''),
                    goal.get('category', ''),
                    f"{goal.get('progress', 0):.1f}%",
                    goal.get('status', ''),
                    goal.get('priority', '')
                ])
            writer.writerow([])

        if report_type in ['full', 'financial']:
            # Financial Metrics
            financial = data.get('financial', {})
            writer.writerow(['FINANCIAL METRICS'])
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Revenue Growth', f"{financial.get('revenue_growth', 0):.1f}%"])
            writer.writerow(['Profit Margin', f"{financial.get('profit_margin', 0):.1f}%"])
            writer.writerow(['Cash Runway', f"{financial.get('cash_runway', 0)} months"])
            writer.writerow(['Burn Rate', f"${financial.get('burn_rate', 0):,.0f}/month"])
            writer.writerow([])

        if report_type in ['full', 'customer']:
            # Customer Metrics
            customer = data.get('customer', {})
            writer.writerow(['CUSTOMER METRICS'])
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['NPS Score', customer.get('nps_score', 0)])
            writer.writerow(['Churn Rate', f"{customer.get('churn_rate', 0):.1f}%"])
            writer.writerow(['CSAT Score', f"{customer.get('csat_score', 0):.1f}/5"])
            writer.writerow(['LTV:CAC Ratio', f"{customer.get('ltv_cac_ratio', 0):.1f}x"])
            writer.writerow([])

        if report_type in ['full', 'people']:
            # People Metrics
            people = data.get('people', {})
            writer.writerow(['PEOPLE METRICS'])
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Engagement Score', f"{people.get('engagement_score', 0)}/100"])
            writer.writerow(['Attrition Rate', f"{people.get('attrition_rate', 0):.1f}%"])
            writer.writerow(['Hiring Velocity', f"{people.get('hiring_velocity', 0)} hires/month"])
            writer.writerow(['Diversity Index', f"{people.get('diversity_index', 0):.2f}"])

        return output.getvalue()

    def generate_html_report(self, data: Dict[str, Any], org_name: str = '') -> str:
        """Generate HTML report for PDF conversion."""
        health = data.get('health', {})
        goals_data = data.get('goals', {})
        financial = data.get('financial', {})
        customer = data.get('customer', {})
        people = data.get('people', {})
        csuite = health.get('csuite_scores', {})

        # Grade color
        grade = health.get('grade', 'C')
        if grade == 'A':
            grade_color = '#28a745'
        elif grade == 'B':
            grade_color = '#17a2b8'
        elif grade == 'C':
            grade_color = '#ffc107'
        elif grade == 'D':
            grade_color = '#fd7e14'
        else:
            grade_color = '#dc3545'

        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Executive Intelligence Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; color: #333; }}
        .header {{ background: linear-gradient(135deg, {self.product_color}, #e83e8c); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .header p {{ margin: 5px 0 0; opacity: 0.9; }}
        .health-card {{ background: linear-gradient(135deg, {grade_color}, {grade_color}dd); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px; }}
        .health-grade {{ font-size: 64px; font-weight: bold; }}
        .health-score {{ font-size: 18px; opacity: 0.9; }}
        .csuite-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 30px; }}
        .csuite-card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }}
        .csuite-role {{ font-size: 12px; color: #666; text-transform: uppercase; }}
        .csuite-score {{ font-size: 20px; font-weight: bold; color: {self.product_color}; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }}
        .metric-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid {self.product_color}; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: {self.product_color}; }}
        .metric-label {{ font-size: 12px; color: #666; text-transform: uppercase; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
        th {{ background: {self.product_color}; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #eee; }}
        tr:hover {{ background: #f8f9fa; }}
        .section-title {{ font-size: 18px; color: #333; margin: 30px 0 15px; border-bottom: 2px solid {self.product_color}; padding-bottom: 5px; }}
        .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; }}
        .status-on_track {{ color: #28a745; font-weight: bold; }}
        .status-at_risk {{ color: #ffc107; font-weight: bold; }}
        .status-behind {{ color: #dc3545; font-weight: bold; }}
        .progress-bar {{ background: #e9ecef; border-radius: 4px; height: 8px; }}
        .progress-fill {{ background: {self.product_color}; height: 100%; border-radius: 4px; }}
        .three-col {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Executive Intelligence Report</h1>
        <p>{org_name or 'Organization'} - Generated {datetime.now().strftime("%B %d, %Y")}</p>
    </div>

    <div class="health-card">
        <div class="health-grade">{grade}</div>
        <div class="health-score">Business Health Score: {health.get('score', 0)}/100</div>
    </div>

    <h2 class="section-title">C-Suite Health Scores</h2>
    <div class="csuite-grid">'''

        for role, score in csuite.items():
            html += f'''
        <div class="csuite-card">
            <div class="csuite-role">{role.upper()}</div>
            <div class="csuite-score">{score}</div>
        </div>'''

        html += f'''
    </div>

    <h2 class="section-title">Strategic Goals</h2>
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value">{goals_data.get('total', 0)}</div>
            <div class="metric-label">Total Goals</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color: #28a745;">{goals_data.get('on_track', 0)}</div>
            <div class="metric-label">On Track</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color: #ffc107;">{goals_data.get('at_risk', 0)}</div>
            <div class="metric-label">At Risk</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color: #dc3545;">{goals_data.get('behind', 0)}</div>
            <div class="metric-label">Behind</div>
        </div>
    </div>

    <table>
        <thead>
            <tr><th>Goal</th><th>Category</th><th>Progress</th><th>Status</th></tr>
        </thead>
        <tbody>'''

        for goal in goals_data.get('items', []):
            status = goal.get('status', 'unknown')
            status_class = f'status-{status}'
            progress = goal.get('progress', 0)
            html += f'''
            <tr>
                <td><strong>{goal.get('title', '')}</strong></td>
                <td>{goal.get('category', '')}</td>
                <td>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {progress}%"></div>
                    </div>
                    {progress:.0f}%
                </td>
                <td class="{status_class}">{status.replace('_', ' ').title()}</td>
            </tr>'''

        html += f'''
        </tbody>
    </table>

    <div class="three-col">
        <div>
            <h2 class="section-title">Financial</h2>
            <table>
                <tr><td>Revenue Growth</td><td><strong>{financial.get('revenue_growth', 0):.1f}%</strong></td></tr>
                <tr><td>Profit Margin</td><td><strong>{financial.get('profit_margin', 0):.1f}%</strong></td></tr>
                <tr><td>Cash Runway</td><td><strong>{financial.get('cash_runway', 0)} mo</strong></td></tr>
                <tr><td>Burn Rate</td><td><strong>${financial.get('burn_rate', 0):,.0f}</strong></td></tr>
            </table>
        </div>
        <div>
            <h2 class="section-title">Customer</h2>
            <table>
                <tr><td>NPS Score</td><td><strong>{customer.get('nps_score', 0)}</strong></td></tr>
                <tr><td>Churn Rate</td><td><strong>{customer.get('churn_rate', 0):.1f}%</strong></td></tr>
                <tr><td>CSAT Score</td><td><strong>{customer.get('csat_score', 0):.1f}/5</strong></td></tr>
                <tr><td>LTV:CAC</td><td><strong>{customer.get('ltv_cac_ratio', 0):.1f}x</strong></td></tr>
            </table>
        </div>
        <div>
            <h2 class="section-title">People</h2>
            <table>
                <tr><td>Engagement</td><td><strong>{people.get('engagement_score', 0)}</strong></td></tr>
                <tr><td>Attrition</td><td><strong>{people.get('attrition_rate', 0):.1f}%</strong></td></tr>
                <tr><td>Hiring Velocity</td><td><strong>{people.get('hiring_velocity', 0)}/mo</strong></td></tr>
                <tr><td>Diversity Index</td><td><strong>{people.get('diversity_index', 0):.2f}</strong></td></tr>
            </table>
        </div>
    </div>

    <div class="footer">
        <p>Generated by Executive Intelligence - Your Fractional CEO</p>
        <p>Part of the Fractional C-Suite by Patriot Tech Systems</p>
    </div>
</body>
</html>'''

        return html


def create_report_generator() -> ReportGenerator:
    """Factory function to create a report generator."""
    return ReportGenerator()
