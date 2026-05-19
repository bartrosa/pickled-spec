"""Turn token usage + catalogue row into USD :class:`CostBreakdown`."""

from __future__ import annotations

from decimal import Decimal

from pickled_core.cost.catalogue import PricingCatalogue
from pickled_core.cost.models import CostBreakdown, PricingSource, TokenUsage

_MTOK = Decimal("1000000")


def estimate_cost(
    usage: TokenUsage,
    *,
    provider: str,
    model_id: str,
    catalogue: PricingCatalogue,
) -> CostBreakdown:
    """Compute USD cost using catalogue rates (zeros for self-hosted wildcard)."""
    row = catalogue.row_for(provider, model_id)
    if row is None:
        z = Decimal("0")
        return CostBreakdown(
            total_usd=z,
            input_usd=z,
            output_usd=z,
            reasoning_usd=z,
            cache_read_usd=z,
            cache_write_5m_usd=z,
            cache_write_1h_usd=z,
            pricing_source="unknown",
        )

    src: PricingSource = "self_hosted" if provider == "openai_compat" else "catalogue"

    inp_u = Decimal(usage.input) / _MTOK * row.input_per_mtok
    out_u = Decimal(usage.output) / _MTOK * row.output_per_mtok
    rsn_u = Decimal(usage.reasoning) / _MTOK * row.reasoning_per_mtok
    cr_u = Decimal(usage.cache_read) / _MTOK * row.cache_read_per_mtok
    cw5_u = Decimal(usage.cache_write_5m) / _MTOK * row.cache_write_5m_per_mtok
    cw1_u = Decimal(usage.cache_write_1h) / _MTOK * row.cache_write_1h_per_mtok
    total = inp_u + out_u + rsn_u + cr_u + cw5_u + cw1_u

    return CostBreakdown(
        total_usd=total,
        input_usd=inp_u,
        output_usd=out_u,
        reasoning_usd=rsn_u,
        cache_read_usd=cr_u,
        cache_write_5m_usd=cw5_u,
        cache_write_1h_usd=cw1_u,
        pricing_source=src,
    )


__all__ = ["estimate_cost"]
