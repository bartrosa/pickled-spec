"""Budget guard tests."""

from __future__ import annotations

from decimal import Decimal

import pytest
from pickled_core.cost.models import CostBreakdown, TokenUsage
from pickled_core.llm.base import BudgetExceededError
from pickled_core.llm.budget import Budget, BudgetGuard


def _cost(usd: str) -> CostBreakdown:
    z = Decimal("0")
    d = Decimal(usd)
    return CostBreakdown(
        total_usd=d,
        input_usd=d,
        output_usd=z,
        reasoning_usd=z,
        cache_read_usd=z,
        cache_write_5m_usd=z,
        cache_write_1h_usd=z,
        pricing_source="catalogue",
    )


def test_max_calls_exact(monkeypatch: pytest.MonkeyPatch) -> None:
    g = BudgetGuard(Budget(max_calls=1))
    g.record(cost=_cost("0"), usage=TokenUsage(input=1, output=1), provider="anthropic")
    with pytest.raises(BudgetExceededError):
        g.record(cost=_cost("0"), usage=TokenUsage(input=1, output=1), provider="anthropic")


def test_max_cost_threshold() -> None:
    g = BudgetGuard(Budget(max_cost_usd=Decimal("1.00")))
    g.record(cost=_cost("0.50"), usage=TokenUsage(input=1), provider="openai")
    with pytest.raises(BudgetExceededError):
        g.record(cost=_cost("0.60"), usage=TokenUsage(input=1), provider="openai")


def test_max_tokens_total() -> None:
    g = BudgetGuard(Budget(max_total_tokens=5))
    g.record(cost=_cost("0"), usage=TokenUsage(input=3, output=2), provider="gemini")
    with pytest.raises(BudgetExceededError):
        g.record(cost=_cost("0"), usage=TokenUsage(input=1), provider="gemini")


def test_check_before_call_blocks_next() -> None:
    g = BudgetGuard(Budget(max_calls=1))
    g.record(cost=_cost("0"), usage=TokenUsage(input=1), provider="p")
    with pytest.raises(BudgetExceededError):
        g.check_before_call(provider="p")


def test_state_snapshot() -> None:
    g = BudgetGuard(Budget(max_cost_usd=Decimal("10")))
    g.record(cost=_cost("1.5"), usage=TokenUsage(input=2, output=3), provider="p")
    s = g.state
    assert s.calls == 1
    assert s.spent_usd == Decimal("1.5")
    assert s.total_tokens == 5
