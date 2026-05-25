"""High-level bootstrap: wires provider, cache, and budget from config + env."""

from __future__ import annotations

import importlib
import os
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import cast

from pickled_core.llm.base import LLMClient
from pickled_core.llm.budget import Budget, BudgetGuard
from pickled_core.llm.budget_context import set_budget_guard
from pickled_core.llm.cache import CacheMode, LLMCache
from pickled_core.llm.config import (
    BudgetSettings,
    CacheSettings,
    ConfigError,
    PickledConfig,
    load_config,
)
from pickled_core.llm.factory import build_client

_VALID_CACHE_MODES = frozenset({"off", "read_write", "read_only"})


def _resolve_cache_dir(cfg_cache: CacheSettings, source_path: Path | None) -> str:
    """Resolve relative cache.dir against the config file's directory.

    If ``cache.dir`` is absolute, return it unchanged. Otherwise:
    - if ``source_path`` is set, resolve against ``source_path.parent``
    - else, return the relative value as-is (CWD-relative)
    """
    env_dir = os.environ.get("PICKLED_CACHE_DIR")
    candidate = env_dir or cfg_cache.dir
    p = Path(candidate)
    if p.is_absolute():
        return str(p)
    if env_dir is not None:
        return str(Path.cwd() / p)
    if source_path is not None:
        return str(source_path.parent / p)
    return str(p)


def _resolve_cache_mode(cfg_cache: CacheSettings) -> str:
    mode = os.environ.get("PICKLED_CACHE_MODE") or cfg_cache.mode
    if mode not in _VALID_CACHE_MODES:
        raise ConfigError(
            f"PICKLED_CACHE_MODE={mode!r}; must be one of {sorted(_VALID_CACHE_MODES)}"
        )
    return mode


def _maybe_build_cache(
    cfg_cache: CacheSettings, source_path: Path | None
) -> LLMCache | None:
    mode = _resolve_cache_mode(cfg_cache)
    if mode == "off":
        return None
    resolved_dir = _resolve_cache_dir(cfg_cache, source_path)
    return LLMCache(resolved_dir, mode=CacheMode(mode))


def _maybe_install_budget(cfg_budget: BudgetSettings) -> None:
    env_value = os.environ.get("PICKLED_MAX_COST_USD")
    raw = env_value if env_value is not None else cfg_budget.max_cost_usd
    if raw is None:
        return
    try:
        cap = Decimal(raw)
    except InvalidOperation as exc:
        raise ConfigError(
            f"max_cost_usd must be a decimal string (got {raw!r})"
        ) from exc
    guard = BudgetGuard(Budget(max_cost_usd=cap))
    set_budget_guard(guard)


def build_default_client(
    *,
    factory_env: str | None = None,
    provider_env: str = "PICKLED_LLM_PROVIDER",
    default_provider: str = "anthropic",
    config: PickledConfig | None = None,
) -> LLMClient:
    """Build an LLMClient honoring config, env, cache, and budget.

    Resolution order:

    1. If ``factory_env`` is set and the named env var is non-empty, import
       ``module:callable`` and return its result. The factory owns its own
       client; no cache or budget is wired (used for tests).
    2. Else: load config (unless passed in), install BudgetGuard if a cap is
       configured, build LLMCache unless mode is ``off``, and return
       ``build_client(provider, config=cfg, cache=cache)``. ``entry.default_model``
       from the chosen provider is passed to the client by ``build_client``.

    Raises ``ConfigError`` on bad factory format, unknown provider, invalid
    cache mode, or non-decimal budget cap.
    """
    if factory_env:
        factory_value = os.environ.get(factory_env)
        if factory_value:
            module_name, sep, attr = factory_value.partition(":")
            if not sep:
                raise ConfigError(
                    f"{factory_env} must be 'module:callable' (got {factory_value!r})"
                )
            module = importlib.import_module(module_name)
            return cast(LLMClient, getattr(module, attr)())

    cfg = config or load_config()
    _maybe_install_budget(cfg.budget)
    cache = _maybe_build_cache(cfg.cache, cfg.source_path)
    provider = os.environ.get(provider_env, default_provider)
    return build_client(provider, config=cfg, cache=cache)


__all__ = ["build_default_client"]
