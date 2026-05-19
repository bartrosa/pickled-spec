"""Append-only ``llm_calls.jsonl`` records on the active run."""

from __future__ import annotations

import time
from collections.abc import Mapping
from typing import Any

from ulid import ULID

from pickled_core.cost.models import CostBreakdown, TokenUsage
from pickled_core.telemetry.jsonl_logger import append_jsonl_record
from pickled_core.telemetry.run_context import current_run


def log_llm_call(
    *,
    provider: str,
    model_id_resolved: str,
    usage: TokenUsage,
    cost: CostBreakdown,
    latency_ms: int,
    cache_hit: bool,
    error_code: str | None,
    extras_summary: Mapping[str, Any],
) -> str | None:
    """Write one JSON line to ``runs/<run_id>/llm_calls.jsonl`` when a run is active."""
    ctx = current_run()
    if ctx is None:
        return None
    path = ctx.run_dir / "llm_calls.jsonl"
    call_id = str(ULID())
    record = {
        "call_id": call_id,
        "ts_ms": int(time.time() * 1000),
        "provider": provider,
        "model_id_resolved": model_id_resolved,
        "usage": {
            "input": usage.input,
            "output": usage.output,
            "reasoning": usage.reasoning,
            "cache_read": usage.cache_read,
            "cache_write_5m": usage.cache_write_5m,
            "cache_write_1h": usage.cache_write_1h,
        },
        "cost_usd": str(cost.total_usd),
        "cost_detail": {
            "input_usd": str(cost.input_usd),
            "output_usd": str(cost.output_usd),
            "reasoning_usd": str(cost.reasoning_usd),
            "cache_read_usd": str(cost.cache_read_usd),
            "cache_write_5m_usd": str(cost.cache_write_5m_usd),
            "cache_write_1h_usd": str(cost.cache_write_1h_usd),
            "pricing_source": cost.pricing_source,
        },
        "latency_ms": latency_ms,
        "cache_hit": cache_hit,
        "error_code": error_code,
        "extras_summary": dict(extras_summary),
    }
    append_jsonl_record(path, record)
    return call_id


def extras_summary_from(mapping: Mapping[str, Any] | None) -> dict[str, Any]:
    """Pick reproducibility-relevant extras for JSONL."""
    if not mapping:
        return {}
    keys = (
        "extended_thinking_budget_tokens",
        "reasoning_effort",
        "cache_control",
    )
    return {k: mapping[k] for k in keys if k in mapping}


__all__ = ["extras_summary_from", "log_llm_call"]
