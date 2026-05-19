from __future__ import annotations

from decimal import Decimal

from pickled_core.cost.models import CostBreakdown, TokenUsage


def test_token_usage_no_float() -> None:
    u = TokenUsage(input=1, output=2)
    assert type(u.input) is int


def test_cost_breakdown_decimal_only() -> None:
    z = Decimal("0")
    b = CostBreakdown(
        total_usd=Decimal("1.5"),
        input_usd=Decimal("1.5"),
        output_usd=z,
        reasoning_usd=z,
        cache_read_usd=z,
        cache_write_5m_usd=z,
        cache_write_1h_usd=z,
        pricing_source="catalogue",
    )
    assert b.total_usd == Decimal("1.5")
    assert not isinstance(b.total_usd, float)
