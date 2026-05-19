from __future__ import annotations

from decimal import Decimal

from pickled_core.cost import TokenUsage, estimate_cost, load_default_catalogue


def test_claude_opus_4_7_input_only() -> None:
    cat = load_default_catalogue()
    u = TokenUsage(input=1_000_000, output=0)
    out = estimate_cost(
        u,
        provider="anthropic",
        model_id="claude-opus-4-7",
        catalogue=cat,
    )
    assert out.total_usd == Decimal("15.00")
    assert out.pricing_source == "catalogue"


def test_gpt_4o_input_only() -> None:
    cat = load_default_catalogue()
    u = TokenUsage(input=1_000_000, output=0)
    out = estimate_cost(
        u,
        provider="openai",
        model_id="gpt-4o",
        catalogue=cat,
    )
    assert out.total_usd == Decimal("2.50")


def test_gemini_2_5_pro_input_only() -> None:
    cat = load_default_catalogue()
    u = TokenUsage(input=1_000_000, output=0)
    out = estimate_cost(
        u,
        provider="gemini",
        model_id="gemini-2.5-pro",
        catalogue=cat,
    )
    assert out.total_usd == Decimal("1.25")


def test_openai_compat_self_hosted_zero() -> None:
    cat = load_default_catalogue()
    u = TokenUsage(input=1_000_000, output=1_000_000)
    out = estimate_cost(
        u,
        provider="openai_compat",
        model_id="any-model",
        catalogue=cat,
    )
    assert out.total_usd == 0
    assert out.pricing_source == "self_hosted"
