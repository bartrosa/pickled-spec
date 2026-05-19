"""Token usage and monetary breakdown using :class:`~decimal.Decimal`."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

PricingSource = Literal["catalogue", "self_hosted", "unknown", "cache"]


@dataclass(frozen=True, slots=True)
class TokenUsage:
    """Normalized token buckets across providers."""

    input: int = 0
    output: int = 0
    reasoning: int = 0
    cache_read: int = 0
    cache_write_5m: int = 0
    cache_write_1h: int = 0

    def total_non_cache(self) -> int:
        return self.input + self.output + self.reasoning

    def total_cache_write(self) -> int:
        return self.cache_write_5m + self.cache_write_1h

    def total_all(self) -> int:
        return (
            self.input
            + self.output
            + self.reasoning
            + self.cache_read
            + self.total_cache_write()
        )


@dataclass(frozen=True, slots=True)
class CostBreakdown:
    """USD cost split by pricing bucket (all fields are Decimal)."""

    total_usd: Decimal
    input_usd: Decimal
    output_usd: Decimal
    reasoning_usd: Decimal
    cache_read_usd: Decimal
    cache_write_5m_usd: Decimal
    cache_write_1h_usd: Decimal
    pricing_source: PricingSource
