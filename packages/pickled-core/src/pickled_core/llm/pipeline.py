"""Shared cache, telemetry, and budget wiring for provider adapters."""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from decimal import Decimal
from typing import Any

from pickled_core.cost.catalogue import PricingCatalogue
from pickled_core.cost.estimator import estimate_cost
from pickled_core.cost.models import CostBreakdown, TokenUsage
from pickled_core.llm.base import Completion, LLMError, Message
from pickled_core.llm.budget_context import active_budget_guard
from pickled_core.llm.cache import CacheMode, LLMCache
from pickled_core.telemetry.llm_calls import extras_summary_from, log_llm_call


def _zero_cost() -> CostBreakdown:
    z = Decimal("0")
    return CostBreakdown(
        total_usd=z,
        input_usd=z,
        output_usd=z,
        reasoning_usd=z,
        cache_read_usd=z,
        cache_write_5m_usd=z,
        cache_write_1h_usd=z,
        pricing_source="cache",
    )


def run_completion(
    *,
    provider_catalog_key: str,
    provider_label: str,
    model_alias: str,
    messages: list[Message],
    max_tokens: int,
    temperature: float | None,
    stop: list[str] | None,
    extras: Mapping[str, Any] | None,
    cache: LLMCache | None,
    catalogue: PricingCatalogue,
    uncached: Callable[[], Completion],
) -> Completion:
    """Handle cache lookup/miss, telemetry, and budget recording."""
    t0 = time.perf_counter_ns()
    summary = extras_summary_from(extras)

    guard = active_budget_guard()
    if guard is not None:
        guard.check_before_call(provider=provider_label)

    if cache is not None and cache.mode is not CacheMode.OFF:
        key = cache.key_for(
            provider=provider_catalog_key,
            model=model_alias,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=stop,
            extras=extras,
        )
        if cache.mode is CacheMode.READ_ONLY:
            try:
                hit = cache.get(key)
            except LLMError:
                lat = int((time.perf_counter_ns() - t0) / 1_000_000)
                log_llm_call(
                    provider=provider_label,
                    model_id_resolved=model_alias,
                    usage=TokenUsage(),
                    cost=_zero_cost(),
                    latency_ms=lat,
                    cache_hit=False,
                    error_code="other",
                    extras_summary=summary,
                )
                raise
        else:
            hit = cache.get(key)
        if hit is not None:
            lat = int((time.perf_counter_ns() - t0) / 1_000_000)
            log_llm_call(
                provider=provider_label,
                model_id_resolved=hit.model_id_resolved,
                usage=hit.usage,
                cost=_zero_cost(),
                latency_ms=lat,
                cache_hit=True,
                error_code=None,
                extras_summary=summary,
            )
            return hit

    try:
        result = uncached()
    except LLMError as exc:
        lat = int((time.perf_counter_ns() - t0) / 1_000_000)
        log_llm_call(
            provider=provider_label,
            model_id_resolved=model_alias,
            usage=TokenUsage(),
            cost=_zero_cost(),
            latency_ms=lat,
            cache_hit=False,
            error_code=exc.code,
            extras_summary=summary,
        )
        raise

    cost = estimate_cost(
        result.usage,
        provider=provider_catalog_key,
        model_id=result.model_id_resolved,
        catalogue=catalogue,
    )

    if guard is not None:
        guard.record(cost=cost, usage=result.usage, provider=provider_label)

    lat = int((time.perf_counter_ns() - t0) / 1_000_000)
    log_llm_call(
        provider=provider_label,
        model_id_resolved=result.model_id_resolved,
        usage=result.usage,
        cost=cost,
        latency_ms=lat,
        cache_hit=False,
        error_code=None,
        extras_summary=summary,
    )

    if cache is not None and cache.mode is CacheMode.READ_WRITE:
        key = cache.key_for(
            provider=provider_catalog_key,
            model=model_alias,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=stop,
            extras=extras,
        )
        cache.set(key, provider=provider_catalog_key, completion=result)

    return result


__all__ = ["run_completion"]
