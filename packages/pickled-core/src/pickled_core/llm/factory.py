"""Construct a concrete :class:`LLMClient` from :class:`PickledConfig`."""

from __future__ import annotations

import os
from collections.abc import Mapping

from pickled_core.cost.catalogue import PricingCatalogue, load_default_catalogue
from pickled_core.llm.base import LLMClient
from pickled_core.llm.cache import LLMCache
from pickled_core.llm.config import (
    ConfigError,
    LLMProviderType,
    PickledConfig,
    load_config,
)


def _require_env(var_name: str) -> str:
    v = os.environ.get(var_name)
    if not v:
        msg = f"environment variable {var_name!r} is not set (required for this provider)"
        raise ConfigError(msg)
    return v


def build_client(
    provider_name: str,
    *,
    config: PickledConfig | None = None,
    cache: LLMCache | None = None,
    pricing: PricingCatalogue | None = None,
) -> LLMClient:
    """Return a live client; resolve API keys from the environment now."""
    cfg = config or load_config()
    cat = pricing or load_default_catalogue()
    if provider_name not in cfg.providers:
        raise ConfigError(f"unknown provider name {provider_name!r}")
    entry = cfg.providers[provider_name]

    extras_headers: Mapping[str, str] = entry.extra_headers

    if entry.type is LLMProviderType.ANTHROPIC:
        from pickled_core.llm.providers.anthropic import AnthropicClient

        if not entry.api_key_env:
            raise ConfigError("anthropic provider requires api_key_env")
        key = _require_env(entry.api_key_env)
        return AnthropicClient(
            api_key=key,
            catalogue=cat,
            cache=cache,
            default_headers=extras_headers,
        )
    if entry.type is LLMProviderType.OPENAI:
        from pickled_core.llm.providers.openai import OpenAIClient

        if not entry.api_key_env:
            raise ConfigError("openai provider requires api_key_env")
        key = _require_env(entry.api_key_env)
        return OpenAIClient(
            api_key=key,
            catalogue=cat,
            cache=cache,
            default_headers=extras_headers,
        )
    if entry.type is LLMProviderType.GEMINI:
        from pickled_core.llm.providers.gemini import GeminiClient

        if not entry.api_key_env:
            raise ConfigError("gemini provider requires api_key_env")
        key = _require_env(entry.api_key_env)
        return GeminiClient(api_key=key, catalogue=cat, cache=cache)
    if entry.type is LLMProviderType.OPENAI_COMPAT:
        from pickled_core.llm.providers.openai_compat import OpenAICompatClient

        assert entry.base_url is not None
        key = _require_env(entry.api_key_env) if entry.api_key_env else "not-needed"
        return OpenAICompatClient(
            api_key=key,
            base_url=entry.base_url,
            catalogue=cat,
            cache=cache,
        )

    raise ConfigError(f"unsupported provider type {entry.type!r}")


__all__ = ["build_client"]
