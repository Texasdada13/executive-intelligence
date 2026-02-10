"""
Cross-Product Aggregator Engine

Fetches and aggregates data from all Fractional C-Suite products
to provide a unified executive dashboard view.

Products:
- Cash Flow Intelligence (CFO) - Port 5101
- App Rationalization Pro (CTO) - Port 5102
- Marketing Intelligence (CMO) - Port 5104
- Security Intelligence (CISO) - Port 5105
- Operations Intelligence (COO) - Port 5106
- Talent Intelligence (CHRO) - Port 5107
"""

import os
import asyncio
import aiohttp
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ProductStatus(Enum):
    """Status of a C-Suite product."""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class HealthLevel(Enum):
    """Health level classification."""
    EXCELLENT = "excellent"  # 90-100
    GOOD = "good"           # 75-89
    FAIR = "fair"           # 60-74
    POOR = "poor"           # 40-59
    CRITICAL = "critical"   # 0-39


@dataclass
class ProductConfig:
    """Configuration for a C-Suite product."""
    name: str
    code: str
    role: str
    port: int
    base_url: str = ""
    health_endpoint: str = "/health"
    summary_endpoint: str = "/api/dashboard"

    def __post_init__(self):
        if not self.base_url:
            self.base_url = f"http://localhost:{self.port}"


@dataclass
class ProductHealth:
    """Health status of a single product."""
    product: str
    role: str
    status: ProductStatus
    health_score: float = 0.0
    response_time_ms: float = 0.0
    last_checked: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            'product': self.product,
            'role': self.role,
            'status': self.status.value,
            'health_score': self.health_score,
            'response_time_ms': round(self.response_time_ms, 2),
            'last_checked': self.last_checked.isoformat(),
            'error': self.error
        }


@dataclass
class ProductSummary:
    """Summary data from a single product."""
    product: str
    role: str
    key_metrics: Dict[str, Any] = field(default_factory=dict)
    alerts: List[Dict] = field(default_factory=list)
    health_score: float = 0.0
    trend: str = "stable"  # improving, stable, declining
    highlights: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            'product': self.product,
            'role': self.role,
            'key_metrics': self.key_metrics,
            'alerts': self.alerts,
            'health_score': self.health_score,
            'trend': self.trend,
            'highlights': self.highlights
        }


@dataclass
class ExecutiveSummary:
    """Aggregated executive summary from all products."""
    overall_health_score: float
    overall_health_level: HealthLevel
    products: List[ProductSummary]
    product_health: List[ProductHealth]
    total_alerts: int
    critical_alerts: int
    aggregated_at: datetime = field(default_factory=datetime.now)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            'overall_health_score': round(self.overall_health_score, 1),
            'overall_health_level': self.overall_health_level.value,
            'overall_grade': self._score_to_grade(self.overall_health_score),
            'products': [p.to_dict() for p in self.products],
            'product_health': [h.to_dict() for h in self.product_health],
            'total_alerts': self.total_alerts,
            'critical_alerts': self.critical_alerts,
            'aggregated_at': self.aggregated_at.isoformat(),
            'recommendations': self.recommendations
        }

    @staticmethod
    def _score_to_grade(score: float) -> str:
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        return 'F'


class CrossProductAggregator:
    """
    Aggregates data from all Fractional C-Suite products.

    Provides unified executive view across:
    - CFO (Cash Flow Intelligence)
    - CTO (App Rationalization Pro)
    - CMO (Marketing Intelligence)
    - CISO (Security Intelligence)
    - COO (Operations Intelligence)
    - CHRO (Talent Intelligence)
    """

    # Product configurations
    PRODUCTS = [
        ProductConfig("Cash Flow Intelligence", "cfo", "CFO", 5101),
        ProductConfig("App Rationalization Pro", "cto", "CTO", 5102),
        ProductConfig("Marketing Intelligence", "cmo", "CMO", 5104),
        ProductConfig("Security Intelligence", "ciso", "CISO", 5105),
        ProductConfig("Operations Intelligence", "coo", "COO", 5106),
        ProductConfig("Talent Intelligence", "chro", "CHRO", 5107),
    ]

    # Role weights for overall health calculation
    ROLE_WEIGHTS = {
        'CFO': 0.20,   # Financial health is critical
        'CTO': 0.15,   # Technology foundation
        'CMO': 0.15,   # Revenue generation
        'CISO': 0.20,  # Security is non-negotiable
        'COO': 0.15,   # Operational efficiency
        'CHRO': 0.15,  # People are the foundation
    }

    def __init__(self, timeout_seconds: float = 5.0):
        """Initialize the aggregator."""
        self.timeout = aiohttp.ClientTimeout(total=timeout_seconds)
        self._cache: Dict[str, Any] = {}
        self._cache_time: Optional[datetime] = None
        self._cache_ttl_seconds = 60  # Cache for 1 minute

    async def check_product_health(self, product: ProductConfig) -> ProductHealth:
        """Check the health of a single product."""
        start_time = datetime.now()

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                url = f"{product.base_url}{product.health_endpoint}"
                async with session.get(url) as response:
                    elapsed = (datetime.now() - start_time).total_seconds() * 1000

                    if response.status == 200:
                        data = await response.json()
                        return ProductHealth(
                            product=product.name,
                            role=product.role,
                            status=ProductStatus.ONLINE,
                            health_score=data.get('health_score', 100.0),
                            response_time_ms=elapsed
                        )
                    else:
                        return ProductHealth(
                            product=product.name,
                            role=product.role,
                            status=ProductStatus.DEGRADED,
                            health_score=50.0,
                            response_time_ms=elapsed,
                            error=f"HTTP {response.status}"
                        )
        except asyncio.TimeoutError:
            return ProductHealth(
                product=product.name,
                role=product.role,
                status=ProductStatus.OFFLINE,
                health_score=0.0,
                error="Connection timeout"
            )
        except Exception as e:
            return ProductHealth(
                product=product.name,
                role=product.role,
                status=ProductStatus.OFFLINE,
                health_score=0.0,
                error=str(e)
            )

    async def check_all_health(self) -> List[ProductHealth]:
        """Check health of all products concurrently."""
        tasks = [self.check_product_health(p) for p in self.PRODUCTS]
        return await asyncio.gather(*tasks)

    async def fetch_product_summary(self, product: ProductConfig, org_id: Optional[str] = None) -> ProductSummary:
        """Fetch summary data from a single product."""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                # Try to get dashboard/summary data
                url = f"{product.base_url}{product.summary_endpoint}"
                if org_id:
                    url = f"{url}/{org_id}"

                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_product_summary(product, data)
                    else:
                        return self._create_offline_summary(product)
        except Exception as e:
            logger.warning(f"Failed to fetch summary from {product.name}: {e}")
            return self._create_offline_summary(product, str(e))

    def _parse_product_summary(self, product: ProductConfig, data: Dict) -> ProductSummary:
        """Parse product-specific response into unified summary."""
        # Each product returns slightly different data, normalize it

        if product.code == 'cfo':
            return self._parse_cfo_summary(product, data)
        elif product.code == 'cto':
            return self._parse_cto_summary(product, data)
        elif product.code == 'cmo':
            return self._parse_cmo_summary(product, data)
        elif product.code == 'ciso':
            return self._parse_ciso_summary(product, data)
        elif product.code == 'coo':
            return self._parse_coo_summary(product, data)
        elif product.code == 'chro':
            return self._parse_chro_summary(product, data)

        return self._create_generic_summary(product, data)

    def _parse_cfo_summary(self, product: ProductConfig, data: Dict) -> ProductSummary:
        """Parse CFO (Cash Flow Intelligence) summary."""
        financial = data.get('financial', {})
        return ProductSummary(
            product=product.name,
            role=product.role,
            key_metrics={
                'revenue_growth': f"{financial.get('revenue_growth', 0)}%",
                'profit_margin': f"{financial.get('profit_margin', 0)}%",
                'cash_runway': f"{financial.get('cash_runway', 0)} months",
                'burn_rate': f"${financial.get('burn_rate', 0):,.0f}/mo"
            },
            health_score=data.get('health', {}).get('score', 75),
            highlights=[
                f"Cash runway: {financial.get('cash_runway', 'N/A')} months",
                f"Revenue growth: {financial.get('revenue_growth', 'N/A')}%"
            ]
        )

    def _parse_cto_summary(self, product: ProductConfig, data: Dict) -> ProductSummary:
        """Parse CTO (App Rationalization) summary."""
        portfolio = data.get('portfolio', {})
        return ProductSummary(
            product=product.name,
            role=product.role,
            key_metrics={
                'total_apps': portfolio.get('total_applications', 0),
                'avg_score': f"{portfolio.get('average_score', 0):.0f}",
                'eliminate_count': portfolio.get('eliminate_count', 0),
                'invest_count': portfolio.get('invest_count', 0)
            },
            health_score=portfolio.get('average_score', 70),
            highlights=[
                f"{portfolio.get('total_applications', 0)} applications in portfolio",
                f"{portfolio.get('eliminate_count', 0)} apps flagged for elimination"
            ]
        )

    def _parse_cmo_summary(self, product: ProductConfig, data: Dict) -> ProductSummary:
        """Parse CMO (Marketing Intelligence) summary."""
        marketing = data.get('marketing', {})
        return ProductSummary(
            product=product.name,
            role=product.role,
            key_metrics={
                'campaign_roi': f"{marketing.get('avg_roi', 0)}%",
                'active_campaigns': marketing.get('active_campaigns', 0),
                'lead_conversion': f"{marketing.get('conversion_rate', 0)}%",
                'cac': f"${marketing.get('cac', 0):,.0f}"
            },
            health_score=marketing.get('performance_score', 72),
            highlights=[
                f"{marketing.get('active_campaigns', 0)} active campaigns",
                f"Average ROI: {marketing.get('avg_roi', 'N/A')}%"
            ]
        )

    def _parse_ciso_summary(self, product: ProductConfig, data: Dict) -> ProductSummary:
        """Parse CISO (Security Intelligence) summary."""
        security = data.get('security', {})
        return ProductSummary(
            product=product.name,
            role=product.role,
            key_metrics={
                'security_score': security.get('posture_score', 0),
                'open_vulns': security.get('open_vulnerabilities', 0),
                'incidents_mtd': security.get('incidents_this_month', 0),
                'compliance': f"{security.get('compliance_score', 0)}%"
            },
            health_score=security.get('posture_score', 74),
            alerts=security.get('critical_alerts', []),
            highlights=[
                f"Security posture: {security.get('posture_score', 'N/A')}/100",
                f"{security.get('open_vulnerabilities', 0)} open vulnerabilities"
            ]
        )

    def _parse_coo_summary(self, product: ProductConfig, data: Dict) -> ProductSummary:
        """Parse COO (Operations Intelligence) summary."""
        ops = data.get('operations', {})
        return ProductSummary(
            product=product.name,
            role=product.role,
            key_metrics={
                'efficiency': f"{ops.get('efficiency_score', 0)}%",
                'utilization': f"{ops.get('resource_utilization', 0)}%",
                'cycle_time': f"{ops.get('avg_cycle_time', 0)} days",
                'quality_rate': f"{ops.get('quality_rate', 0)}%"
            },
            health_score=ops.get('efficiency_score', 76),
            highlights=[
                f"Operational efficiency: {ops.get('efficiency_score', 'N/A')}%",
                f"Resource utilization: {ops.get('resource_utilization', 'N/A')}%"
            ]
        )

    def _parse_chro_summary(self, product: ProductConfig, data: Dict) -> ProductSummary:
        """Parse CHRO (Talent Intelligence) summary."""
        hr = data.get('people', {})
        return ProductSummary(
            product=product.name,
            role=product.role,
            key_metrics={
                'engagement': f"{hr.get('engagement_score', 0)}%",
                'attrition': f"{hr.get('attrition_rate', 0)}%",
                'hiring_velocity': f"{hr.get('hiring_velocity', 0)}/mo",
                'diversity': f"{hr.get('diversity_index', 0) * 100:.0f}%"
            },
            health_score=hr.get('engagement_score', 78) if hr.get('engagement_score', 0) > 0 else 70,
            highlights=[
                f"Employee engagement: {hr.get('engagement_score', 'N/A')}%",
                f"Attrition rate: {hr.get('attrition_rate', 'N/A')}%"
            ]
        )

    def _create_generic_summary(self, product: ProductConfig, data: Dict) -> ProductSummary:
        """Create a generic summary from any product response."""
        return ProductSummary(
            product=product.name,
            role=product.role,
            key_metrics=data.get('metrics', {}),
            health_score=data.get('health', {}).get('score', 70)
        )

    def _create_offline_summary(self, product: ProductConfig, error: Optional[str] = None) -> ProductSummary:
        """Create a summary for an offline product."""
        return ProductSummary(
            product=product.name,
            role=product.role,
            key_metrics={'status': 'offline'},
            health_score=0.0,
            alerts=[{'level': 'critical', 'message': f'{product.name} is offline'}] if error else [],
            highlights=[f"Service unavailable: {error}" if error else "Service unavailable"]
        )

    async def get_executive_summary(self, org_id: Optional[str] = None) -> ExecutiveSummary:
        """
        Get comprehensive executive summary from all products.

        This is the main entry point for the executive dashboard.
        """
        # Check cache
        if self._is_cache_valid():
            return self._cache['executive_summary']

        # Fetch health and summaries concurrently
        health_task = self.check_all_health()
        summary_tasks = [self.fetch_product_summary(p, org_id) for p in self.PRODUCTS]

        all_health = await health_task
        all_summaries = await asyncio.gather(*summary_tasks)

        # Calculate overall health score (weighted by role importance)
        online_scores = []
        for health in all_health:
            if health.status == ProductStatus.ONLINE:
                weight = self.ROLE_WEIGHTS.get(health.role, 0.1)
                online_scores.append((health.health_score, weight))

        if online_scores:
            total_weight = sum(w for _, w in online_scores)
            overall_score = sum(s * w for s, w in online_scores) / total_weight if total_weight > 0 else 0
        else:
            overall_score = 0

        # Also factor in summary scores
        for summary in all_summaries:
            if summary.health_score > 0:
                weight = self.ROLE_WEIGHTS.get(summary.role, 0.1)
                overall_score = (overall_score + summary.health_score * weight) / (1 + weight)

        # Determine health level
        if overall_score >= 90:
            health_level = HealthLevel.EXCELLENT
        elif overall_score >= 75:
            health_level = HealthLevel.GOOD
        elif overall_score >= 60:
            health_level = HealthLevel.FAIR
        elif overall_score >= 40:
            health_level = HealthLevel.POOR
        else:
            health_level = HealthLevel.CRITICAL

        # Count alerts
        total_alerts = sum(len(s.alerts) for s in all_summaries)
        critical_alerts = sum(
            1 for s in all_summaries
            for a in s.alerts
            if a.get('level') == 'critical'
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(all_summaries, all_health)

        summary = ExecutiveSummary(
            overall_health_score=overall_score,
            overall_health_level=health_level,
            products=all_summaries,
            product_health=all_health,
            total_alerts=total_alerts,
            critical_alerts=critical_alerts,
            recommendations=recommendations
        )

        # Cache the result
        self._cache['executive_summary'] = summary
        self._cache_time = datetime.now()

        return summary

    def _generate_recommendations(
        self,
        summaries: List[ProductSummary],
        health: List[ProductHealth]
    ) -> List[str]:
        """Generate executive-level recommendations based on all product data."""
        recommendations = []

        # Check for offline products
        offline = [h for h in health if h.status == ProductStatus.OFFLINE]
        if offline:
            recommendations.append(
                f"Critical: {len(offline)} product(s) offline - "
                f"{', '.join(h.product for h in offline)}"
            )

        # Check for low health scores
        low_health = [s for s in summaries if 0 < s.health_score < 60]
        for s in low_health:
            recommendations.append(
                f"Review {s.role} ({s.product}): Health score {s.health_score:.0f}/100"
            )

        # Product-specific recommendations
        for summary in summaries:
            if summary.role == 'CISO' and summary.health_score < 75:
                recommendations.append(
                    "Security posture needs attention - consider security review"
                )
            elif summary.role == 'CFO':
                metrics = summary.key_metrics
                if 'cash_runway' in str(metrics) and '6' in str(metrics.get('cash_runway', '')):
                    recommendations.append(
                        "Cash runway below 6 months - review financing options"
                    )
            elif summary.role == 'CHRO':
                if summary.health_score < 70:
                    recommendations.append(
                        "Employee engagement declining - consider culture initiatives"
                    )

        return recommendations[:5]  # Limit to top 5

    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if not self._cache_time or 'executive_summary' not in self._cache:
            return False

        elapsed = (datetime.now() - self._cache_time).total_seconds()
        return elapsed < self._cache_ttl_seconds

    def clear_cache(self):
        """Clear the cache."""
        self._cache = {}
        self._cache_time = None


# Synchronous wrapper functions for Flask routes
def get_executive_summary_sync(org_id: Optional[str] = None) -> Dict:
    """Synchronous wrapper for getting executive summary."""
    aggregator = CrossProductAggregator()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        summary = loop.run_until_complete(aggregator.get_executive_summary(org_id))
        return summary.to_dict()
    finally:
        loop.close()


def check_all_health_sync() -> List[Dict]:
    """Synchronous wrapper for checking all product health."""
    aggregator = CrossProductAggregator()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        health = loop.run_until_complete(aggregator.check_all_health())
        return [h.to_dict() for h in health]
    finally:
        loop.close()


def create_demo_cross_product_data() -> Dict:
    """
    Create demo data for when products are not running.

    This provides realistic mock data for demonstration purposes.
    """
    return {
        'overall_health_score': 76.5,
        'overall_health_level': 'good',
        'overall_grade': 'C',
        'products': [
            {
                'product': 'Cash Flow Intelligence',
                'role': 'CFO',
                'key_metrics': {
                    'revenue_growth': '12.5%',
                    'profit_margin': '18.2%',
                    'cash_runway': '24 months',
                    'burn_rate': '$125,000/mo'
                },
                'health_score': 78,
                'trend': 'improving',
                'highlights': [
                    'Cash runway: 24 months',
                    'Revenue growth: 12.5%'
                ],
                'alerts': []
            },
            {
                'product': 'App Rationalization Pro',
                'role': 'CTO',
                'key_metrics': {
                    'total_apps': 47,
                    'avg_score': '68',
                    'eliminate_count': 8,
                    'invest_count': 12
                },
                'health_score': 68,
                'trend': 'stable',
                'highlights': [
                    '47 applications in portfolio',
                    '8 apps flagged for elimination'
                ],
                'alerts': [
                    {'level': 'warning', 'message': '8 applications need retirement'}
                ]
            },
            {
                'product': 'Marketing Intelligence',
                'role': 'CMO',
                'key_metrics': {
                    'campaign_roi': '285%',
                    'active_campaigns': 12,
                    'lead_conversion': '4.2%',
                    'cac': '$1,250'
                },
                'health_score': 82,
                'trend': 'improving',
                'highlights': [
                    '12 active campaigns',
                    'Average ROI: 285%'
                ],
                'alerts': []
            },
            {
                'product': 'Security Intelligence',
                'role': 'CISO',
                'key_metrics': {
                    'security_score': 74,
                    'open_vulns': 23,
                    'incidents_mtd': 2,
                    'compliance': '89%'
                },
                'health_score': 74,
                'trend': 'stable',
                'highlights': [
                    'Security posture: 74/100',
                    '23 open vulnerabilities'
                ],
                'alerts': [
                    {'level': 'warning', 'message': '5 critical vulnerabilities pending'}
                ]
            },
            {
                'product': 'Operations Intelligence',
                'role': 'COO',
                'key_metrics': {
                    'efficiency': '84%',
                    'utilization': '78%',
                    'cycle_time': '4.2 days',
                    'quality_rate': '96.5%'
                },
                'health_score': 81,
                'trend': 'stable',
                'highlights': [
                    'Operational efficiency: 84%',
                    'Resource utilization: 78%'
                ],
                'alerts': []
            },
            {
                'product': 'Talent Intelligence',
                'role': 'CHRO',
                'key_metrics': {
                    'engagement': '78%',
                    'attrition': '8.5%',
                    'hiring_velocity': '12/mo',
                    'diversity': '72%'
                },
                'health_score': 76,
                'trend': 'declining',
                'highlights': [
                    'Employee engagement: 78%',
                    'Attrition rate: 8.5%'
                ],
                'alerts': [
                    {'level': 'info', 'message': 'Engagement trending down 3% from last quarter'}
                ]
            }
        ],
        'product_health': [
            {'product': 'Cash Flow Intelligence', 'role': 'CFO', 'status': 'online', 'health_score': 100, 'response_time_ms': 45},
            {'product': 'App Rationalization Pro', 'role': 'CTO', 'status': 'online', 'health_score': 100, 'response_time_ms': 52},
            {'product': 'Marketing Intelligence', 'role': 'CMO', 'status': 'online', 'health_score': 100, 'response_time_ms': 38},
            {'product': 'Security Intelligence', 'role': 'CISO', 'status': 'online', 'health_score': 100, 'response_time_ms': 61},
            {'product': 'Operations Intelligence', 'role': 'COO', 'status': 'online', 'health_score': 100, 'response_time_ms': 44},
            {'product': 'Talent Intelligence', 'role': 'CHRO', 'status': 'online', 'health_score': 100, 'response_time_ms': 39}
        ],
        'total_alerts': 3,
        'critical_alerts': 0,
        'aggregated_at': datetime.now().isoformat(),
        'recommendations': [
            'Review CTO portfolio: 8 applications flagged for elimination could save costs',
            'Security posture needs attention - 5 critical vulnerabilities pending',
            'Employee engagement declining - consider culture initiatives',
            'Strong marketing ROI (285%) - consider increasing marketing investment',
            'Cash position healthy with 24-month runway'
        ]
    }
