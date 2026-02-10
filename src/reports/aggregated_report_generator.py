"""
Aggregated Report Generator for Executive Intelligence

Generates unified reports across all Fractional C-Suite products:
- Executive Summary Report
- Board Presentation Report
- Quarterly Business Review
- Department Performance Reports

Supports multiple output formats and customization.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime, timedelta
import json


class ReportType(Enum):
    """Types of aggregated reports."""
    EXECUTIVE_SUMMARY = "executive_summary"
    BOARD_PRESENTATION = "board_presentation"
    QUARTERLY_REVIEW = "quarterly_review"
    DEPARTMENT_DEEP_DIVE = "department_deep_dive"
    RISK_ASSESSMENT = "risk_assessment"
    STRATEGIC_ROADMAP = "strategic_roadmap"


class ReportFormat(Enum):
    """Output formats for reports."""
    HTML = "html"
    JSON = "json"
    MARKDOWN = "markdown"


class Department(Enum):
    """C-Suite departments/roles."""
    CFO = "cfo"
    CTO = "cto"
    CMO = "cmo"
    CISO = "ciso"
    COO = "coo"
    CHRO = "chro"


@dataclass
class DepartmentMetrics:
    """Metrics for a single department."""
    department: Department
    role_title: str
    product_name: str
    health_score: float
    trend: str  # improving, stable, declining
    key_metrics: Dict[str, Any]
    highlights: List[str]
    concerns: List[str]
    recommendations: List[str]

    def to_dict(self) -> Dict:
        return {
            "department": self.department.value,
            "role_title": self.role_title,
            "product_name": self.product_name,
            "health_score": self.health_score,
            "trend": self.trend,
            "key_metrics": self.key_metrics,
            "highlights": self.highlights,
            "concerns": self.concerns,
            "recommendations": self.recommendations
        }


@dataclass
class ReportSection:
    """A section within a report."""
    title: str
    content: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    charts: List[Dict] = field(default_factory=list)
    subsections: List['ReportSection'] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "content": self.content,
            "metrics": self.metrics,
            "charts": self.charts,
            "subsections": [s.to_dict() for s in self.subsections]
        }


@dataclass
class AggregatedReport:
    """Complete aggregated report."""
    report_id: str
    report_type: ReportType
    title: str
    organization: str
    generated_at: datetime
    reporting_period: str

    # Summary
    executive_summary: str
    overall_health_score: float
    overall_grade: str

    # Department data
    department_metrics: List[DepartmentMetrics]

    # Sections
    sections: List[ReportSection]

    # Key findings
    key_findings: List[str]
    strategic_recommendations: List[str]
    risk_items: List[Dict]

    # Metadata
    data_sources: List[str]
    confidence_level: float

    def to_dict(self) -> Dict:
        return {
            "report_id": self.report_id,
            "report_type": self.report_type.value,
            "title": self.title,
            "organization": self.organization,
            "generated_at": self.generated_at.isoformat(),
            "reporting_period": self.reporting_period,
            "executive_summary": self.executive_summary,
            "overall_health_score": self.overall_health_score,
            "overall_grade": self.overall_grade,
            "department_metrics": [d.to_dict() for d in self.department_metrics],
            "sections": [s.to_dict() for s in self.sections],
            "key_findings": self.key_findings,
            "strategic_recommendations": self.strategic_recommendations,
            "risk_items": self.risk_items,
            "data_sources": self.data_sources,
            "confidence_level": self.confidence_level
        }


class AggregatedReportGenerator:
    """
    Generates comprehensive reports from cross-product data.
    """

    # Report templates
    REPORT_TEMPLATES = {
        ReportType.EXECUTIVE_SUMMARY: {
            "sections": ["Overview", "Financial Health", "Technology", "Marketing", "Security", "Operations", "People", "Recommendations"],
            "include_charts": True,
            "detail_level": "high"
        },
        ReportType.BOARD_PRESENTATION: {
            "sections": ["Executive Summary", "Key Metrics", "Financial Position", "Strategic Progress", "Risk Overview", "Outlook"],
            "include_charts": True,
            "detail_level": "summary"
        },
        ReportType.QUARTERLY_REVIEW: {
            "sections": ["Quarter Overview", "Financial Performance", "Operational Metrics", "People & Culture", "Technology & Security", "Strategic Initiatives", "Next Quarter Priorities"],
            "include_charts": True,
            "detail_level": "comprehensive"
        }
    }

    # Role mappings
    ROLE_INFO = {
        Department.CFO: {"title": "Chief Financial Officer", "product": "Cash Flow Intelligence"},
        Department.CTO: {"title": "Chief Technology Officer", "product": "App Rationalization Pro"},
        Department.CMO: {"title": "Chief Marketing Officer", "product": "Marketing Intelligence"},
        Department.CISO: {"title": "Chief Information Security Officer", "product": "Security Intelligence"},
        Department.COO: {"title": "Chief Operating Officer", "product": "Operations Intelligence"},
        Department.CHRO: {"title": "Chief Human Resources Officer", "product": "Talent Intelligence"},
    }

    def __init__(self, organization: str = "Demo Organization"):
        self.organization = organization
        self._report_counter = 0

    def _generate_report_id(self) -> str:
        """Generate unique report ID."""
        self._report_counter += 1
        return f"RPT-{datetime.now().strftime('%Y%m%d')}-{self._report_counter:04d}"

    def _score_to_grade(self, score: float) -> str:
        """Convert score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        return "F"

    def _analyze_trend(self, current: float, previous: float) -> str:
        """Analyze trend direction."""
        if previous == 0:
            return "stable"
        change = ((current - previous) / previous) * 100
        if change > 5:
            return "improving"
        elif change < -5:
            return "declining"
        return "stable"

    def _generate_executive_summary_text(self, data: Dict, health_score: float) -> str:
        """Generate executive summary narrative."""
        grade = self._score_to_grade(health_score)

        summary = f"""
The organization's overall health score is {health_score:.0f}/100 (Grade: {grade}),
reflecting the combined performance across all business functions.

Key highlights from this reporting period:
"""
        # Add department highlights
        products = data.get('products', [])
        for product in products[:3]:  # Top 3
            if product.get('health_score', 0) > 75:
                summary += f"\n- {product.get('role', 'N/A')}: Strong performance with {product.get('health_score', 0):.0f}/100 health score"

        # Add concerns
        low_performers = [p for p in products if p.get('health_score', 100) < 70]
        if low_performers:
            summary += f"\n\nAreas requiring attention: "
            summary += ", ".join([f"{p.get('role')} ({p.get('health_score', 0):.0f}/100)" for p in low_performers])

        return summary.strip()

    def _extract_department_metrics(self, data: Dict) -> List[DepartmentMetrics]:
        """Extract department metrics from cross-product data."""
        metrics = []

        products = data.get('products', [])
        for product in products:
            role = product.get('role', '').upper()
            try:
                dept = Department(role.lower())
            except ValueError:
                continue

            role_info = self.ROLE_INFO.get(dept, {})

            # Determine concerns based on metrics
            concerns = []
            recs = []

            if product.get('health_score', 100) < 70:
                concerns.append(f"Health score below target ({product.get('health_score', 0):.0f}/100)")
                recs.append(f"Review {role} department performance and identify improvement areas")

            for alert in product.get('alerts', []):
                concerns.append(alert.get('message', 'Unknown alert'))

            if product.get('trend') == 'declining':
                concerns.append("Performance trending downward")
                recs.append("Investigate root cause of declining metrics")

            metrics.append(DepartmentMetrics(
                department=dept,
                role_title=role_info.get('title', role),
                product_name=role_info.get('product', product.get('product', '')),
                health_score=product.get('health_score', 0),
                trend=product.get('trend', 'stable'),
                key_metrics=product.get('key_metrics', {}),
                highlights=product.get('highlights', []),
                concerns=concerns,
                recommendations=recs
            ))

        return metrics

    def _generate_sections(self, report_type: ReportType, data: Dict, dept_metrics: List[DepartmentMetrics]) -> List[ReportSection]:
        """Generate report sections based on type."""
        sections = []
        template = self.REPORT_TEMPLATES.get(report_type, {})
        section_names = template.get('sections', [])

        for section_name in section_names:
            if section_name == "Overview" or section_name == "Executive Summary" or section_name == "Quarter Overview":
                sections.append(self._create_overview_section(section_name, data))
            elif section_name in ["Financial Health", "Financial Performance", "Financial Position"]:
                sections.append(self._create_financial_section(section_name, dept_metrics))
            elif section_name == "Technology":
                sections.append(self._create_technology_section(dept_metrics))
            elif section_name == "Marketing":
                sections.append(self._create_marketing_section(dept_metrics))
            elif section_name in ["Security", "Technology & Security"]:
                sections.append(self._create_security_section(dept_metrics))
            elif section_name in ["Operations", "Operational Metrics"]:
                sections.append(self._create_operations_section(dept_metrics))
            elif section_name in ["People", "People & Culture"]:
                sections.append(self._create_people_section(dept_metrics))
            elif section_name in ["Recommendations", "Strategic Initiatives", "Next Quarter Priorities"]:
                sections.append(self._create_recommendations_section(data, dept_metrics))
            elif section_name == "Key Metrics":
                sections.append(self._create_key_metrics_section(data, dept_metrics))
            elif section_name in ["Risk Overview", "Strategic Progress", "Outlook"]:
                sections.append(self._create_generic_section(section_name, data))

        return sections

    def _create_overview_section(self, title: str, data: Dict) -> ReportSection:
        """Create overview section."""
        health = data.get('overall_health_score', 0)
        return ReportSection(
            title=title,
            content=f"Overall organizational health stands at {health:.0f}/100. "
                    f"This report aggregates insights from all C-Suite intelligence products "
                    f"to provide a comprehensive view of business performance.",
            metrics={
                "overall_health": health,
                "grade": self._score_to_grade(health),
                "total_alerts": data.get('total_alerts', 0),
                "critical_alerts": data.get('critical_alerts', 0)
            },
            charts=[{"type": "gauge", "title": "Overall Health", "value": health}]
        )

    def _create_financial_section(self, title: str, dept_metrics: List[DepartmentMetrics]) -> ReportSection:
        """Create financial section."""
        cfo = next((d for d in dept_metrics if d.department == Department.CFO), None)
        if not cfo:
            return ReportSection(title=title, content="Financial data not available.")

        return ReportSection(
            title=title,
            content=f"Financial health score: {cfo.health_score:.0f}/100. "
                    f"Trend: {cfo.trend}. "
                    f"{' '.join(cfo.highlights)}",
            metrics=cfo.key_metrics,
            charts=[
                {"type": "trend", "title": "Revenue Growth", "metric": "revenue_growth"},
                {"type": "bar", "title": "Financial KPIs", "metrics": list(cfo.key_metrics.keys())}
            ]
        )

    def _create_technology_section(self, dept_metrics: List[DepartmentMetrics]) -> ReportSection:
        """Create technology section."""
        cto = next((d for d in dept_metrics if d.department == Department.CTO), None)
        if not cto:
            return ReportSection(title="Technology", content="Technology data not available.")

        return ReportSection(
            title="Technology & Applications",
            content=f"Technology portfolio health: {cto.health_score:.0f}/100. "
                    f"{' '.join(cto.highlights)}",
            metrics=cto.key_metrics,
            charts=[{"type": "pie", "title": "Application Portfolio Distribution"}]
        )

    def _create_marketing_section(self, dept_metrics: List[DepartmentMetrics]) -> ReportSection:
        """Create marketing section."""
        cmo = next((d for d in dept_metrics if d.department == Department.CMO), None)
        if not cmo:
            return ReportSection(title="Marketing", content="Marketing data not available.")

        return ReportSection(
            title="Marketing & Growth",
            content=f"Marketing performance: {cmo.health_score:.0f}/100. "
                    f"{' '.join(cmo.highlights)}",
            metrics=cmo.key_metrics,
            charts=[{"type": "funnel", "title": "Marketing Funnel"}]
        )

    def _create_security_section(self, dept_metrics: List[DepartmentMetrics]) -> ReportSection:
        """Create security section."""
        ciso = next((d for d in dept_metrics if d.department == Department.CISO), None)
        if not ciso:
            return ReportSection(title="Security", content="Security data not available.")

        return ReportSection(
            title="Security & Compliance",
            content=f"Security posture: {ciso.health_score:.0f}/100. "
                    f"{' '.join(ciso.highlights)}",
            metrics=ciso.key_metrics,
            charts=[{"type": "radar", "title": "Security Dimensions"}]
        )

    def _create_operations_section(self, dept_metrics: List[DepartmentMetrics]) -> ReportSection:
        """Create operations section."""
        coo = next((d for d in dept_metrics if d.department == Department.COO), None)
        if not coo:
            return ReportSection(title="Operations", content="Operations data not available.")

        return ReportSection(
            title="Operations",
            content=f"Operational efficiency: {coo.health_score:.0f}/100. "
                    f"{' '.join(coo.highlights)}",
            metrics=coo.key_metrics,
            charts=[{"type": "bar", "title": "Operational KPIs"}]
        )

    def _create_people_section(self, dept_metrics: List[DepartmentMetrics]) -> ReportSection:
        """Create people/HR section."""
        chro = next((d for d in dept_metrics if d.department == Department.CHRO), None)
        if not chro:
            return ReportSection(title="People & Culture", content="HR data not available.")

        return ReportSection(
            title="People & Culture",
            content=f"Employee engagement: {chro.health_score:.0f}/100. "
                    f"{' '.join(chro.highlights)}",
            metrics=chro.key_metrics,
            charts=[{"type": "trend", "title": "Engagement Trend"}]
        )

    def _create_recommendations_section(self, data: Dict, dept_metrics: List[DepartmentMetrics]) -> ReportSection:
        """Create recommendations section."""
        recs = data.get('recommendations', [])
        all_dept_recs = []
        for dept in dept_metrics:
            all_dept_recs.extend(dept.recommendations)

        combined_recs = list(set(recs + all_dept_recs))[:10]

        return ReportSection(
            title="Strategic Recommendations",
            content="Based on analysis across all business functions, the following actions are recommended:",
            metrics={"total_recommendations": len(combined_recs)},
            subsections=[
                ReportSection(title=f"{i+1}. {rec}", content="")
                for i, rec in enumerate(combined_recs)
            ]
        )

    def _create_key_metrics_section(self, data: Dict, dept_metrics: List[DepartmentMetrics]) -> ReportSection:
        """Create key metrics summary section."""
        metrics = {}
        for dept in dept_metrics:
            metrics[dept.role_title] = {
                "score": dept.health_score,
                "trend": dept.trend,
                **dept.key_metrics
            }

        return ReportSection(
            title="Key Metrics Summary",
            content="Performance metrics across all departments:",
            metrics=metrics,
            charts=[{"type": "heatmap", "title": "Department Performance Matrix"}]
        )

    def _create_generic_section(self, title: str, data: Dict) -> ReportSection:
        """Create a generic section."""
        return ReportSection(
            title=title,
            content=f"This section covers {title.lower()} aspects of the organization.",
            metrics={}
        )

    def _extract_key_findings(self, data: Dict, dept_metrics: List[DepartmentMetrics]) -> List[str]:
        """Extract key findings from data."""
        findings = []

        # Overall health
        health = data.get('overall_health_score', 0)
        if health >= 80:
            findings.append(f"Strong overall organizational health at {health:.0f}/100")
        elif health < 60:
            findings.append(f"Organizational health needs attention at {health:.0f}/100")

        # Department-specific
        for dept in dept_metrics:
            if dept.health_score >= 85:
                findings.append(f"{dept.role_title}: Excellent performance ({dept.health_score:.0f}/100)")
            elif dept.health_score < 60:
                findings.append(f"{dept.role_title}: Performance below target ({dept.health_score:.0f}/100)")

        # Alerts
        if data.get('critical_alerts', 0) > 0:
            findings.append(f"{data.get('critical_alerts')} critical alerts require immediate attention")

        return findings[:8]

    def _extract_risk_items(self, data: Dict, dept_metrics: List[DepartmentMetrics]) -> List[Dict]:
        """Extract risk items from data."""
        risks = []

        for dept in dept_metrics:
            if dept.health_score < 60:
                risks.append({
                    "category": dept.department.value.upper(),
                    "severity": "high",
                    "description": f"{dept.role_title} performance below acceptable threshold",
                    "impact": "Potential impact on overall business operations",
                    "mitigation": dept.recommendations[0] if dept.recommendations else "Review and improve"
                })

            for concern in dept.concerns:
                if "critical" in concern.lower():
                    risks.append({
                        "category": dept.department.value.upper(),
                        "severity": "critical",
                        "description": concern,
                        "impact": "Immediate attention required",
                        "mitigation": "Address within 24-48 hours"
                    })

        return risks

    def generate_report(
        self,
        report_type: ReportType,
        cross_product_data: Dict,
        reporting_period: Optional[str] = None
    ) -> AggregatedReport:
        """
        Generate an aggregated report from cross-product data.

        Args:
            report_type: Type of report to generate
            cross_product_data: Data from CrossProductAggregator
            reporting_period: Optional period string (e.g., "Q1 2026")

        Returns:
            Complete AggregatedReport
        """
        if not reporting_period:
            reporting_period = datetime.now().strftime("%B %Y")

        # Extract health score
        health_score = cross_product_data.get('overall_health_score', 0)

        # Extract department metrics
        dept_metrics = self._extract_department_metrics(cross_product_data)

        # Generate executive summary
        exec_summary = self._generate_executive_summary_text(cross_product_data, health_score)

        # Generate sections
        sections = self._generate_sections(report_type, cross_product_data, dept_metrics)

        # Extract findings and risks
        key_findings = self._extract_key_findings(cross_product_data, dept_metrics)
        risk_items = self._extract_risk_items(cross_product_data, dept_metrics)
        strategic_recs = cross_product_data.get('recommendations', [])

        # Data sources
        data_sources = [d.product_name for d in dept_metrics]

        return AggregatedReport(
            report_id=self._generate_report_id(),
            report_type=report_type,
            title=f"{report_type.value.replace('_', ' ').title()} - {reporting_period}",
            organization=self.organization,
            generated_at=datetime.now(),
            reporting_period=reporting_period,
            executive_summary=exec_summary,
            overall_health_score=health_score,
            overall_grade=self._score_to_grade(health_score),
            department_metrics=dept_metrics,
            sections=sections,
            key_findings=key_findings,
            strategic_recommendations=strategic_recs,
            risk_items=risk_items,
            data_sources=data_sources,
            confidence_level=len(dept_metrics) / 6 * 100  # Based on available data sources
        )

    def render_html(self, report: AggregatedReport) -> str:
        """Render report as HTML."""
        sections_html = ""
        for section in report.sections:
            metrics_html = ""
            if section.metrics:
                metrics_html = "<div class='metrics'>"
                for k, v in section.metrics.items():
                    if isinstance(v, dict):
                        continue
                    metrics_html += f"<div class='metric'><span class='label'>{k}:</span> <span class='value'>{v}</span></div>"
                metrics_html += "</div>"

            sections_html += f"""
            <section class="report-section">
                <h2>{section.title}</h2>
                <p>{section.content}</p>
                {metrics_html}
            </section>
            """

        dept_html = ""
        for dept in report.department_metrics:
            trend_class = "improving" if dept.trend == "improving" else "declining" if dept.trend == "declining" else "stable"
            dept_html += f"""
            <div class="department-card">
                <h3>{dept.role_title}</h3>
                <div class="score">{dept.health_score:.0f}/100</div>
                <div class="trend {trend_class}">{dept.trend}</div>
                <div class="product">{dept.product_name}</div>
            </div>
            """

        findings_html = "<ul>" + "".join(f"<li>{f}</li>" for f in report.key_findings) + "</ul>"
        recs_html = "<ul>" + "".join(f"<li>{r}</li>" for r in report.strategic_recommendations) + "</ul>"

        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>{report.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
        .header {{ background: linear-gradient(135deg, #1e40af, #3b82f6); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }}
        .header h1 {{ margin: 0 0 10px 0; }}
        .header .meta {{ opacity: 0.9; }}
        .score-card {{ display: flex; gap: 20px; margin-bottom: 30px; }}
        .score-card .item {{ background: #f3f4f6; padding: 20px; border-radius: 8px; text-align: center; flex: 1; }}
        .score-card .item .value {{ font-size: 32px; font-weight: bold; color: #1e40af; }}
        .score-card .item .label {{ color: #666; font-size: 14px; }}
        .department-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }}
        .department-card {{ background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; }}
        .department-card h3 {{ margin: 0 0 10px 0; color: #1e40af; }}
        .department-card .score {{ font-size: 24px; font-weight: bold; }}
        .department-card .trend {{ font-size: 12px; padding: 4px 8px; border-radius: 4px; display: inline-block; }}
        .department-card .trend.improving {{ background: #d1fae5; color: #059669; }}
        .department-card .trend.declining {{ background: #fee2e2; color: #dc2626; }}
        .department-card .trend.stable {{ background: #e5e7eb; color: #6b7280; }}
        .report-section {{ background: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 25px; margin-bottom: 20px; }}
        .report-section h2 {{ margin-top: 0; color: #1e40af; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }}
        .metrics {{ display: flex; flex-wrap: wrap; gap: 15px; margin-top: 15px; }}
        .metric {{ background: #f9fafb; padding: 10px 15px; border-radius: 6px; }}
        .metric .label {{ color: #6b7280; }}
        .metric .value {{ font-weight: bold; color: #1e40af; margin-left: 5px; }}
        ul {{ padding-left: 20px; }}
        li {{ margin-bottom: 8px; }}
        .footer {{ text-align: center; color: #9ca3af; margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{report.title}</h1>
        <div class="meta">
            {report.organization} | Generated: {report.generated_at.strftime('%B %d, %Y')} | Report ID: {report.report_id}
        </div>
    </div>

    <div class="score-card">
        <div class="item">
            <div class="value">{report.overall_health_score:.0f}</div>
            <div class="label">Health Score</div>
        </div>
        <div class="item">
            <div class="value">{report.overall_grade}</div>
            <div class="label">Grade</div>
        </div>
        <div class="item">
            <div class="value">{len(report.department_metrics)}</div>
            <div class="label">Departments</div>
        </div>
        <div class="item">
            <div class="value">{report.confidence_level:.0f}%</div>
            <div class="label">Data Coverage</div>
        </div>
    </div>

    <section class="report-section">
        <h2>Executive Summary</h2>
        <p>{report.executive_summary}</p>
    </section>

    <h2>Department Performance</h2>
    <div class="department-grid">
        {dept_html}
    </div>

    {sections_html}

    <section class="report-section">
        <h2>Key Findings</h2>
        {findings_html}
    </section>

    <section class="report-section">
        <h2>Strategic Recommendations</h2>
        {recs_html}
    </section>

    <div class="footer">
        <p>Generated by Executive Intelligence | Patriot Tech Systems</p>
        <p>Data Sources: {', '.join(report.data_sources)}</p>
    </div>
</body>
</html>
"""

    def render_markdown(self, report: AggregatedReport) -> str:
        """Render report as Markdown."""
        md = f"""# {report.title}

**Organization:** {report.organization}
**Generated:** {report.generated_at.strftime('%B %d, %Y')}
**Report ID:** {report.report_id}

---

## Executive Summary

**Overall Health Score:** {report.overall_health_score:.0f}/100 (Grade: {report.overall_grade})

{report.executive_summary}

---

## Department Performance

| Department | Score | Trend |
|------------|-------|-------|
"""
        for dept in report.department_metrics:
            md += f"| {dept.role_title} | {dept.health_score:.0f}/100 | {dept.trend} |\n"

        md += "\n---\n\n"

        for section in report.sections:
            md += f"## {section.title}\n\n{section.content}\n\n"
            if section.metrics:
                md += "**Metrics:**\n"
                for k, v in section.metrics.items():
                    if not isinstance(v, dict):
                        md += f"- {k}: {v}\n"
            md += "\n"

        md += "## Key Findings\n\n"
        for finding in report.key_findings:
            md += f"- {finding}\n"

        md += "\n## Strategic Recommendations\n\n"
        for rec in report.strategic_recommendations:
            md += f"- {rec}\n"

        md += f"\n---\n\n*Data Sources: {', '.join(report.data_sources)}*\n"

        return md


def create_aggregated_report_generator(organization: str = "Demo Organization") -> AggregatedReportGenerator:
    """Factory function to create report generator."""
    return AggregatedReportGenerator(organization=organization)


def generate_demo_report() -> AggregatedReport:
    """Generate a demo report with sample data."""
    from ..integrations.cross_product_aggregator import create_demo_cross_product_data

    generator = create_aggregated_report_generator("Acme Corporation")
    demo_data = create_demo_cross_product_data()

    return generator.generate_report(
        report_type=ReportType.EXECUTIVE_SUMMARY,
        cross_product_data=demo_data,
        reporting_period="February 2026"
    )
