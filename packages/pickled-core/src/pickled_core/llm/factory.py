"""Construct a concrete :class:`LLMClient` from :class:`PickledConfig`."""

from __future__ import annotations

import importlib
import os
from collections.abc import Mapping
from types import ModuleType
from typing import cast

from pickled_core.cost.catalogue import PricingCatalogue, load_default_catalogue
from pickled_core.llm.base import LLMClient
from pickled_core.llm.cache import LLMCache
from pickled_core.llm.config import (
    ConfigError,
    LLMProviderType,
    PickledConfig,
    load_config,
)

_PROVIDER_EXTRAS: dict[LLMProviderType, str] = {
    LLMProviderType.ANTHROPIC: "anthropic",
    LLMProviderType.OPENAI: "openai",
    LLMProviderType.GEMINI: "gemini",
    LLMProviderType.OPENAI_COMPAT: "openai",
}


def _import_provider_module(module: str, provider_type: LLMProviderType) -> ModuleType:
    extra = _PROVIDER_EXTRAS[provider_type]
    try:
        return importlib.import_module(module)
    except ImportError as exc:
        msg = (
            f"provider {provider_type.value!r} requires optional dependency "
            f"'{extra}'; install with: pip install 'pickled-core[{extra}]'"
        )
        raise ConfigError(msg) from exc


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
        if not entry.api_key_env:
            raise ConfigError("anthropic provider requires api_key_env")
        key = _require_env(entry.api_key_env)
        mod = _import_provider_module(
            "pickled_core.llm.providers.anthropic",
            LLMProviderType.ANTHROPIC,
        )
        AnthropicClient = mod.AnthropicClient

        return cast(
            LLMClient,
            AnthropicClient(
                api_key=key,
                catalogue=cat,
                cache=cache,
                default_headers=extras_headers,
                default_model=entry.default_model,
            ),
        )
    if entry.type is LLMProviderType.OPENAI:
        if not entry.api_key_env:
            raise ConfigError("openai provider requires api_key_env")
        key = _require_env(entry.api_key_env)
        mod = _import_provider_module(
            "pickled_core.llm.providers.openai",
            LLMProviderType.OPENAI,
        )
        OpenAIClient = mod.OpenAIClient

        return cast(
            LLMClient,
            OpenAIClient(
                api_key=key,
                catalogue=cat,
                cache=cache,
                default_headers=extras_headers,
                default_model=entry.default_model,
            ),
        )
    if entry.type is LLMProviderType.GEMINI:
        if not entry.api_key_env:
            raise ConfigError("gemini provider requires api_key_env")
        key = _require_env(entry.api_key_env)
        mod = _import_provider_module(
            "pickled_core.llm.providers.gemini",
            LLMProviderType.GEMINI,
        )
        GeminiClient = mod.GeminiClient

        return cast(
            LLMClient,
            GeminiClient(
                api_key=key,
                catalogue=cat,
                cache=cache,
                default_model=entry.default_model,
            ),
        )
    if entry.type is LLMProviderType.OPENAI_COMPAT:
        assert entry.base_url is not None
        key = _require_env(entry.api_key_env) if entry.api_key_env else "not-needed"
        mod = _import_provider_module(
            "pickled_core.llm.providers.openai_compat",
            LLMProviderType.OPENAI_COMPAT,
        )
        OpenAICompatClient = mod.OpenAICompatClient

        return cast(
            LLMClient,
            OpenAICompatClient(
                api_key=key,
                base_url=entry.base_url,
                catalogue=cat,
                cache=cache,
                default_model=entry.default_model,
            ),
        )

    raise ConfigError(f"unsupported provider type {entry.type!r}")


__all__ = ["build_client"]
