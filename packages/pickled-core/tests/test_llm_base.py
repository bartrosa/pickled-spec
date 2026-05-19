from __future__ import annotations

from decimal import Decimal

from pickled_core.cost.models import TokenUsage
from pickled_core.llm.base import BudgetExceededError, Completion, LLMError


def test_completion_fields() -> None:
    usage = TokenUsage(input=1, output=2, reasoning=0, cache_read=0)
    c = Completion(
        text="hi",
        usage=usage,
        model_id_resolved="m",
        raw_response={"ok": True},
        cache_hit=False,
    )
    assert c.text == "hi"
    assert c.usage.input == 1


def test_llm_error_attributes() -> None:
    err = LLMError(
        provider="anthropic",
        code="rate_limit",
        message="slow",
        retriable=True,
    )
    assert err.code == "rate_limit"
    assert err.retriable is True


def test_budget_exceeded_error() -> None:
    err = BudgetExceededError(provider="openai", message="over")
    assert err.code == "budget_exceeded"
    assert err.retriable is False


def test_token_usage_total_all() -> None:
    u = TokenUsage(input=1, output=2, cache_write_5m=3, cache_write_1h=4)
    assert u.total_all() == 10


def test_cost_breakdown_is_decimal() -> None:
    from pickled_core.cost.models import CostBreakdown

    z = Decimal("0")
    b = CostBreakdown(
        total_usd=z,
        input_usd=z,
        output_usd=z,
        reasoning_usd=z,
        cache_read_usd=z,
        cache_write_5m_usd=z,
        cache_write_1h_usd=z,
        pricing_source="catalogue",
    )
    assert isinstance(b.total_usd, Decimal)
