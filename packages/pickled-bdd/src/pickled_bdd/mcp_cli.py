"""MCP server CLI for pickled-bdd."""

from __future__ import annotations

import contextlib

import click
from fastmcp import FastMCP
from pickled_core.llm import LLMClient
from pickled_core.mcp.stdio_logging import setup_logging_for_stdio
from pickled_core.mcp.transport import resolve_transport

from pickled_bdd.mcp_tools import register_with_fastmcp


def _build_llm_client() -> LLMClient:
    from pickled_core.llm.bootstrap import build_default_client
    from pickled_core.llm.config import ConfigError

    try:
        return build_default_client(factory_env="PICKLED_BDD_LLM_FACTORY")
    except ConfigError as exc:
        raise click.ClickException(str(exc)) from exc


def build_server() -> FastMCP:
    """Entry point for ``pickled.mcp.subservers`` (returns FastMCP app)."""
    app = FastMCP("pickled-bdd")
    llm: LLMClient | None = None
    with contextlib.suppress(click.ClickException):
        llm = _build_llm_client()
    register_with_fastmcp(app, llm=llm)
    return app


@click.command()
@click.option(
    "--transport",
    type=click.Choice(["stdio", "http"]),
    default="stdio",
    show_default=True,
)
@click.option("--host", default=None)
@click.option("--port", type=int, default=None)
@click.option("--allow-public", is_flag=True, default=False)
def cli(
    transport: str,
    host: str | None,
    port: int | None,
    allow_public: bool,
) -> None:
    """Run the pickled-bdd MCP server."""
    if transport == "stdio":
        setup_logging_for_stdio()
    app = FastMCP("pickled-bdd")
    register_with_fastmcp(app, llm=_build_llm_client())
    kwargs = resolve_transport(transport, host, port, allow_public)  # type: ignore[arg-type]
    transport_name = kwargs.pop("transport")
    app.run(transport=transport_name, **kwargs)


__all__ = ["build_server", "cli"]
