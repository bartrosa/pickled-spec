from __future__ import annotations

# YAML schema (``pickled.config.yaml``):
#
# - ``providers:`` map; each entry has ``type`` (anthropic|openai|gemini|
#   openai_compat), ``default_model``, optional ``api_key_env``, ``base_url``
#   (required for openai_compat), optional ``extra_headers``.
# - optional ``cache:`` block with ``dir`` (default ``.pickled-cache``) and
#   ``mode`` (default ``read_write``; one of ``off``, ``read_write``,
#   ``read_only``).
# - optional ``budget:`` block with ``max_cost_usd`` (decimal string or null).
import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml


class LLMProviderType(StrEnum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GEMINI = "gemini"
    OPENAI_COMPAT = "openai_compat"


@dataclass(frozen=True, slots=True)
class ProviderConfigEntry:
    name: str
    type: LLMProviderType
    api_key_env: str | None
    base_url: str | None
    default_model: str
    extra_headers: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CacheSettings:
    dir: str = ".pickled-cache"
    mode: str = "read_write"


@dataclass(frozen=True, slots=True)
class BudgetSettings:
    max_cost_usd: str | None = None


@dataclass(frozen=True, slots=True)
class PickledConfig:
    providers: Mapping[str, ProviderConfigEntry]
    cache: CacheSettings = field(default_factory=CacheSettings)
    budget: BudgetSettings = field(default_factory=BudgetSettings)
    source_path: Path | None = None


class ConfigError(Exception):
    """Invalid ``pickled.config.yaml`` or provider definition."""


def _xdg_config_candidates() -> list[Path]:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    home = Path.home()
    if xdg:
        return [Path(xdg) / "pickled" / "config.yaml"]
    return [home / ".config" / "pickled" / "config.yaml"]


def _empty_config() -> PickledConfig:
    return PickledConfig(providers={})


def _parse_entry(name: str, blob: Mapping[str, Any]) -> ProviderConfigEntry:
    try:
        t_raw = blob["type"]
        default_model = str(blob["default_model"])
    except KeyError as exc:
        raise ConfigError(f"provider {name!r} missing {exc.args[0]}") from exc

    try:
        ptype = LLMProviderType(str(t_raw))
    except ValueError as exc:
        raise ConfigError(f"provider {name!r}: unknown type {t_raw!r}") from exc

    api_key_env = blob.get("api_key_env")
    if api_key_env is not None:
        api_key_env = str(api_key_env)
    base_url = blob.get("base_url")
    if base_url is not None:
        base_url = str(base_url)

    if ptype is LLMProviderType.OPENAI_COMPAT and not base_url:
        raise ConfigError(f"provider {name!r}: openai_compat requires base_url")

    extra = blob.get("extra_headers") or {}
    if extra is not None and not isinstance(extra, Mapping):
        raise ConfigError(f"provider {name!r}: extra_headers must be a mapping")

    return ProviderConfigEntry(
        name=name,
        type=ptype,
        api_key_env=api_key_env,
        base_url=base_url,
        default_model=default_model,
        extra_headers=dict(extra) if isinstance(extra, Mapping) else {},
    )


def load_config(path: str | Path | None = None) -> PickledConfig:
    """Load YAML configuration (see module docstring)."""
    if path is not None:
        p = Path(path).resolve()
        if not p.is_file():
            raise ConfigError(f"config file not found: {p}")
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
        return _config_from_mapping(data, source=str(p), source_path=p)

    local = Path("pickled.config.yaml")
    if local.is_file():
        resolved = local.resolve()
        data = yaml.safe_load(resolved.read_text(encoding="utf-8"))
        return _config_from_mapping(data, source=str(resolved), source_path=resolved)

    for cand in _xdg_config_candidates():
        if cand.is_file():
            resolved = cand.resolve()
            data = yaml.safe_load(resolved.read_text(encoding="utf-8"))
            return _config_from_mapping(
                data, source=str(resolved), source_path=resolved
            )

    return _empty_config()


_CACHE_MODES = frozenset({"off", "read_write", "read_only"})


def _parse_cache(data: Any, source: str) -> CacheSettings:
    """Parse the optional ``cache:`` mapping from YAML."""
    if not isinstance(data, Mapping):
        raise ConfigError(f"{source}: cache must be a mapping")
    dir_val = ".pickled-cache"
    if "dir" in data:
        dir_val = str(data["dir"])
    mode = "read_write"
    if "mode" in data:
        raw_mode = data["mode"]
        if raw_mode is False:
            mode = "off"
        elif isinstance(raw_mode, bool):
            raise ConfigError(
                f"{source}: cache.mode must be one of {sorted(_CACHE_MODES)}"
            )
        else:
            mode = str(raw_mode)
    if mode not in _CACHE_MODES:
        raise ConfigError(
            f"{source}: cache.mode must be one of {sorted(_CACHE_MODES)}"
        )
    return CacheSettings(dir=dir_val, mode=mode)


def _parse_budget(data: Any, source: str) -> BudgetSettings:
    """Parse the optional ``budget:`` mapping from YAML."""
    if not isinstance(data, Mapping):
        raise ConfigError(f"{source}: budget must be a mapping")
    if "max_cost_usd" not in data:
        return BudgetSettings(max_cost_usd=None)
    raw = data["max_cost_usd"]
    if raw is None:
        return BudgetSettings(max_cost_usd=None)
    if not isinstance(raw, str):
        raise ConfigError(f"{source}: budget.max_cost_usd must be a decimal string")
    from decimal import Decimal, InvalidOperation

    try:
        Decimal(raw)
    except InvalidOperation as exc:
        raise ConfigError(
            f"{source}: budget.max_cost_usd must be a decimal string"
        ) from exc
    return BudgetSettings(max_cost_usd=raw)


def _config_from_mapping(
    data: Any,
    *,
    source: str,
    source_path: Path | None = None,
) -> PickledConfig:
    if data is None:
        return PickledConfig(providers={}, source_path=source_path)
    if not isinstance(data, Mapping):
        raise ConfigError(f"{source}: root must be a mapping")
    cache = CacheSettings()
    raw_cache = data.get("cache")
    if raw_cache is not None:
        cache = _parse_cache(raw_cache, source)
    budget = BudgetSettings()
    raw_budget = data.get("budget")
    if raw_budget is not None:
        budget = _parse_budget(raw_budget, source)
    prov = data.get("providers")
    if prov is None:
        return PickledConfig(
            providers={}, cache=cache, budget=budget, source_path=source_path
        )
    if not isinstance(prov, Mapping):
        raise ConfigError(f"{source}: providers must be a mapping")
    out: dict[str, ProviderConfigEntry] = {}
    for name, blob in prov.items():
        if not isinstance(blob, Mapping):
            raise ConfigError(f"{source}: providers.{name} must be a mapping")
        entry = _parse_entry(str(name), blob)
        out[entry.name] = entry
    return PickledConfig(
        providers=out, cache=cache, budget=budget, source_path=source_path
    )


__all__ = [
    "BudgetSettings",
    "CacheSettings",
    "ConfigError",
    "LLMProviderType",
    "PickledConfig",
    "ProviderConfigEntry",
    "load_config",
]
