"""Shared LLM bootstrap helpers for pickled-* MCP CLIs."""

from __future__ import annotations

import click

from pickled_core.llm.base import LLMClient


def build_llm_client(*, factory_env: str) -> LLMClient:
    """Build an LLM client or raise :class:`click.ClickException` on config errors."""
    from pickled_core.llm.bootstrap import build_default_client
    from pickled_core.llm.config import ConfigError

    try:
        return build_default_client(factory_env=factory_env)
    except ConfigError as exc:
        raise click.ClickException(str(exc)) from exc


def optional_llm_client(*, factory_env: str) -> LLMClient | None:
    """Return an LLM client when config and provider extras are available."""
    from pickled_core.llm.bootstrap import build_default_client
    from pickled_core.llm.config import ConfigError

    try:
        return build_default_client(factory_env=factory_env)
    except ConfigError:
        return None


__all__ = ["build_llm_client", "optional_llm_client"]
