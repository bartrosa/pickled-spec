"""MCP server CLI for pickled-iac."""

from __future__ import annotations

import contextlib
import importlib
import os
from typing import cast

import click
from fastmcp import FastMCP
from pickled_core import LLMClient
from pickled_core.mcp.stdio_logging import setup_logging_for_stdio
from pickled_core.mcp.transport import resolve_transport

from pickled_iac.mcp_tools import register_with_fastmcp


def _build_llm_client() -> LLMClient:
    factory = os.environ.get("PICKLED_IAC_LLM_FACTORY")
    if factory:
        module_name, sep, attr = factory.partition(":")
        if not sep:
            raise click.ClickException(
                "PICKLED_IAC_LLM_FACTORY must be 'module:callable'"
            )
        module = importlib.import_module(module_name)
        return cast(LLMClient, getattr(module, attr)())

    from pickled_core.llm.config import ConfigError, load_config
    from pickled_core.llm.factory import build_client

    provider = os.environ.get("PICKLED_LLM_PROVIDER", "anthropic")
    try:
        return build_client(provider, config=load_config())
    except ConfigError as exc:
        raise click.ClickException(str(exc)) from exc


def build_server() -> FastMCP:
    app = FastMCP("pickled-iac")
    llm: LLMClient | None = None
    with contextlib.suppress(click.ClickException):
        llm = _build_llm_client()
    register_with_fastmcp(app, llm=llm)
    return app


@click.command()
@click.option("--transport", type=click.Choice(["stdio", "http"]), default="stdio")
@click.option("--host", default=None)
@click.option("--port", type=int, default=None)
@click.option("--allow-public", is_flag=True, default=False)
def cli(
    transport: str,
    host: str | None,
    port: int | None,
    allow_public: bool,
) -> None:
    if transport == "stdio":
        setup_logging_for_stdio()
    app = FastMCP("pickled-iac")
    register_with_fastmcp(app, llm=_build_llm_client())
    kwargs = resolve_transport(transport, host, port, allow_public)  # type: ignore[arg-type]
    transport_name = kwargs.pop("transport")
    app.run(transport=transport_name, **kwargs)


__all__ = ["build_server", "cli"]
