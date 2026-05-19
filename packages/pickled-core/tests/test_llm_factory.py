"""Factory wiring tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from pickled_core.cost.catalogue import load_default_catalogue
from pickled_core.llm.base import LLMClient
from pickled_core.llm.config import ConfigError, LLMProviderType, PickledConfig, ProviderConfigEntry
from pickled_core.llm.factory import build_client


def test_make_anthropic(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("SK", "secret-key")
    cfg = PickledConfig(
        providers={
            "mine": ProviderConfigEntry(
                name="mine",
                type=LLMProviderType.ANTHROPIC,
                api_key_env="SK",
                base_url=None,
                default_model="claude-3-5-sonnet-20241022",
            ),
        },
    )
    client = build_client("mine", config=cfg, pricing=load_default_catalogue())
    assert isinstance(client, LLMClient)


def test_missing_key_raises(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("MISSING", raising=False)
    cfg = PickledConfig(
        providers={
            "x": ProviderConfigEntry(
                name="x",
                type=LLMProviderType.OPENAI,
                api_key_env="MISSING",
                base_url=None,
                default_model="gpt-4o",
            ),
        },
    )
    with pytest.raises(ConfigError, match="MISSING"):
        build_client("x", config=cfg)


def test_openai_compat_optional_key(monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = PickledConfig(
        providers={
            "loc": ProviderConfigEntry(
                name="loc",
                type=LLMProviderType.OPENAI_COMPAT,
                api_key_env=None,
                base_url="http://localhost:11434/v1",
                default_model="llama",
            ),
        },
    )
    c = build_client("loc", config=cfg)
    from pickled_core.llm.providers.openai_compat import OpenAICompatClient

    assert isinstance(c, OpenAICompatClient)


def test_unknown_provider_name() -> None:
    with pytest.raises(ConfigError, match="unknown"):
        build_client("nope", config=PickledConfig(providers={}))
