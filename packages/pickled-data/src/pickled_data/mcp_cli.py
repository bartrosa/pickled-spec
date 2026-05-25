"""MCP server CLI for pickled-data."""

from __future__ import annotations

import click
from fastmcp import FastMCP
from pickled_core.mcp.llm_client import build_llm_client, optional_llm_client
from pickled_core.mcp.stdio_logging import setup_logging_for_stdio
from pickled_core.mcp.transport import resolve_transport

from pickled_data.mcp_tools import register_with_fastmcp

_FACTORY_ENV = "PICKLED_DATA_LLM_FACTORY"


def build_server() -> FastMCP:
    app = FastMCP("pickled-data")
    register_with_fastmcp(app, llm=optional_llm_client(factory_env=_FACTORY_ENV))
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
    app = FastMCP("pickled-data")
    register_with_fastmcp(app, llm=build_llm_client(factory_env=_FACTORY_ENV))
    kwargs = resolve_transport(transport, host, port, allow_public)  # type: ignore[arg-type]
    transport_name = kwargs.pop("transport")
    app.run(transport=transport_name, **kwargs)


__all__ = ["build_server", "cli"]
