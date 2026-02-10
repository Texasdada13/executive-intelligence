"""Cross-product integrations for Executive Intelligence."""
from .unified_context import UnifiedContextBuilder, UnifiedHealthScore
from .product_adapters import MarketingAdapter, SecurityAdapter
from .cross_product_aggregator import (
    CrossProductAggregator,
    ProductStatus,
    HealthLevel,
    ProductConfig,
    ProductHealth,
    ProductSummary,
    ExecutiveSummary,
    get_executive_summary_sync,
    check_all_health_sync,
    create_demo_cross_product_data
)

__all__ = [
    'UnifiedContextBuilder',
    'UnifiedHealthScore',
    'MarketingAdapter',
    'SecurityAdapter',
    # Cross-product aggregator
    'CrossProductAggregator',
    'ProductStatus',
    'HealthLevel',
    'ProductConfig',
    'ProductHealth',
    'ProductSummary',
    'ExecutiveSummary',
    'get_executive_summary_sync',
    'check_all_health_sync',
    'create_demo_cross_product_data'
]
