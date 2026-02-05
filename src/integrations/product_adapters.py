"""Product Adapters for Cross-Product Data Access"""
import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class AdapterConfig:
    """Configuration for a product adapter."""
    base_url: str
    api_key: Optional[str] = None
    timeout: int = 30
    verify_ssl: bool = True


class ProductAdapter(ABC):
    """Base class for product adapters."""

    def __init__(self, config: AdapterConfig):
        self.config = config
        self.session = requests.Session()
        if config.api_key:
            self.session.headers['Authorization'] = f'Bearer {config.api_key}'

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an HTTP request to the product API."""
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        kwargs.setdefault('timeout', self.config.timeout)
        kwargs.setdefault('verify', self.config.verify_ssl)

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'success': False}

    @abstractmethod
    def get_organization_data(self, org_id: str) -> Dict[str, Any]:
        """Fetch organization data from the product."""
        pass

    @abstractmethod
    def get_health_metrics(self, org_id: str) -> Dict[str, Any]:
        """Fetch health metrics from the product."""
        pass

    def check_health(self) -> bool:
        """Check if the product is healthy."""
        try:
            result = self._request('GET', '/health')
            return result.get('status') == 'healthy'
        except Exception:
            return False


class MarketingAdapter(ProductAdapter):
    """Adapter for Marketing Intelligence product."""

    def __init__(self, base_url: str = "http://localhost:5001", api_key: str = None):
        super().__init__(AdapterConfig(base_url=base_url, api_key=api_key))

    def get_organization_data(self, org_id: str) -> Dict[str, Any]:
        """Fetch marketing organization data."""
        org = self._request('GET', f'/api/organizations/{org_id}')
        channels = self._request('GET', f'/api/organizations/{org_id}/channels')
        campaigns = self._request('GET', f'/api/organizations/{org_id}/campaigns')

        return {
            'organization': org,
            'channels': channels if isinstance(channels, list) else [],
            'campaigns': campaigns if isinstance(campaigns, list) else []
        }

    def get_health_metrics(self, org_id: str) -> Dict[str, Any]:
        """Fetch marketing health metrics."""
        data = self.get_organization_data(org_id)

        # Calculate metrics from channels
        channels = data.get('channels', [])
        campaigns = data.get('campaigns', [])

        if not channels:
            return {'error': 'No channel data available'}

        total_spend = sum(c.get('spend', 0) for c in channels)
        total_revenue = sum(c.get('revenue', 0) for c in channels)
        total_conversions = sum(c.get('conversions', 0) for c in channels)

        roas = total_revenue / total_spend if total_spend > 0 else 0
        roi = (total_revenue - total_spend) / total_spend * 100 if total_spend > 0 else 0

        # Calculate health score
        health_score = min(100, max(0,
            (min(roas / 3, 1) * 40) +
            (min(roi / 100, 1) * 30 if roi > 0 else 0) +
            30  # Base score
        ))

        return {
            'organization_id': org_id,
            'metrics_summary': {
                'total_spend': total_spend,
                'total_revenue': total_revenue,
                'roas': round(roas, 2),
                'roi_percentage': round(roi, 1),
                'total_conversions': total_conversions,
                'active_campaigns': len([c for c in campaigns if c.get('status') == 'active']),
                'active_channels': len([c for c in channels if c.get('status') == 'active']),
                'health_score': round(health_score)
            },
            'channels': channels,
            'campaigns': campaigns,
            'context_for_ai': {
                'roas': round(roas, 2),
                'roi_percentage': round(roi, 1),
                'health_score': round(health_score),
                'total_spend': total_spend
            }
        }

    def get_benchmark_results(self, org_id: str) -> Dict[str, Any]:
        """Fetch latest benchmark results."""
        return self._request('GET', f'/api/organizations/{org_id}/benchmark')

    def generate_demo_data(self, org_name: str = None, seed: int = None) -> Dict[str, Any]:
        """Generate demo marketing data."""
        return self._request('POST', '/api/demo/generate', json={
            'organization_name': org_name,
            'seed': seed
        })


class SecurityAdapter(ProductAdapter):
    """Adapter for Security Intelligence product."""

    def __init__(self, base_url: str = "http://localhost:5002", api_key: str = None):
        super().__init__(AdapterConfig(base_url=base_url, api_key=api_key))

    def get_organization_data(self, org_id: str) -> Dict[str, Any]:
        """Fetch security organization data."""
        org = self._request('GET', f'/api/organizations/{org_id}')
        vulns = self._request('GET', f'/api/organizations/{org_id}/vulnerabilities')
        incidents = self._request('GET', f'/api/organizations/{org_id}/incidents')

        return {
            'organization': org,
            'vulnerabilities': vulns if isinstance(vulns, list) else [],
            'incidents': incidents if isinstance(incidents, list) else []
        }

    def get_health_metrics(self, org_id: str) -> Dict[str, Any]:
        """Fetch security health metrics."""
        data = self.get_organization_data(org_id)

        vulnerabilities = data.get('vulnerabilities', [])
        incidents = data.get('incidents', [])

        # Count vulnerabilities by severity
        vuln_counts = {
            'critical': len([v for v in vulnerabilities if v.get('severity') == 'critical' and v.get('status') != 'remediated']),
            'high': len([v for v in vulnerabilities if v.get('severity') == 'high' and v.get('status') != 'remediated']),
            'medium': len([v for v in vulnerabilities if v.get('severity') == 'medium' and v.get('status') != 'remediated']),
            'low': len([v for v in vulnerabilities if v.get('severity') == 'low' and v.get('status') != 'remediated'])
        }

        open_incidents = len([i for i in incidents if i.get('status') in ['open', 'investigating', 'contained']])

        # Calculate posture score
        posture_score = max(0, 100 - (
            vuln_counts['critical'] * 20 +
            vuln_counts['high'] * 5 +
            open_incidents * 5
        ))

        return {
            'organization_id': org_id,
            'metrics_summary': {
                'posture_score': posture_score,
                'vulnerabilities': vuln_counts,
                'total_vulnerabilities': sum(vuln_counts.values()),
                'open_incidents': open_incidents,
                'total_incidents': len(incidents),
                'mttr_hours': 0,  # Would calculate from resolved incidents
                'avg_compliance_score': 80,  # Would fetch from compliance data
                'mfa_adoption': 85,  # Would fetch from access data
                'privileged_users': 25  # Would fetch from access data
            },
            'vulnerabilities': vulnerabilities,
            'incidents': incidents,
            'context_for_ai': {
                'posture_score': posture_score,
                'vulnerabilities': vuln_counts,
                'open_incidents': open_incidents
            }
        }

    def get_compliance_status(self, org_id: str) -> Dict[str, Any]:
        """Fetch compliance status."""
        # This would fetch from /api/organizations/{org_id}/compliance
        return self._request('GET', f'/api/organizations/{org_id}/compliance')

    def get_risk_register(self, org_id: str) -> Dict[str, Any]:
        """Fetch risk register."""
        return self._request('GET', f'/api/organizations/{org_id}/risks')

    def generate_demo_data(self, org_name: str = None, seed: int = None) -> Dict[str, Any]:
        """Generate demo security data."""
        return self._request('POST', '/api/demo/generate', json={
            'organization_name': org_name,
            'seed': seed
        })


class MockMarketingAdapter(MarketingAdapter):
    """Mock adapter for testing without actual Marketing Intelligence service."""

    def __init__(self):
        # Don't call super().__init__ - we don't need HTTP session
        self.config = AdapterConfig(base_url="mock://marketing")
        self._demo_data = None

    def _load_demo(self, org_name: str = None):
        """Load demo data using the demo generator."""
        from src.demo.data_generator import create_marketing_demo_generator
        generator = create_marketing_demo_generator(42)
        self._demo_data = generator.generate_full_demo(org_name or "Demo Marketing Co")

    def get_health_metrics(self, org_id: str) -> Dict[str, Any]:
        """Return mock marketing metrics."""
        if not self._demo_data:
            self._load_demo()
        return self._demo_data

    def check_health(self) -> bool:
        return True


class MockSecurityAdapter(SecurityAdapter):
    """Mock adapter for testing without actual Security Intelligence service."""

    def __init__(self):
        self.config = AdapterConfig(base_url="mock://security")
        self._demo_data = None

    def _load_demo(self, org_name: str = None):
        """Load demo data using the demo generator."""
        from src.demo.data_generator import create_security_demo_generator
        generator = create_security_demo_generator(42)
        self._demo_data = generator.generate_full_demo(org_name or "Demo Security Corp")

    def get_health_metrics(self, org_id: str) -> Dict[str, Any]:
        """Return mock security metrics."""
        if not self._demo_data:
            self._load_demo()
        return self._demo_data

    def check_health(self) -> bool:
        return True


def create_marketing_adapter(
    base_url: str = None,
    use_mock: bool = False
) -> MarketingAdapter:
    """Factory function to create a marketing adapter."""
    if use_mock:
        return MockMarketingAdapter()
    return MarketingAdapter(base_url or "http://localhost:5001")


def create_security_adapter(
    base_url: str = None,
    use_mock: bool = False
) -> SecurityAdapter:
    """Factory function to create a security adapter."""
    if use_mock:
        return MockSecurityAdapter()
    return SecurityAdapter(base_url or "http://localhost:5002")
