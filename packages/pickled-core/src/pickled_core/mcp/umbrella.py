"""Umbrella MCP server: mounts every leaf package under its own namespace."""

from __future__ import annotations

import logging
from importlib.metadata import entry_points

import click
from fastmcp import FastMCP

from pickled_core.mcp.resources import register_core_resources
from pickled_core.mcp.stdio_logging import setup_logging_for_stdio
from pickled_core.mcp.transport import resolve_transport

logger = logging.getLogger(__name__)


def build_umbrella() -> FastMCP:
    """Discover ``pickled.mcp.subservers`` entry points and mount each child."""
    umbrella = FastMCP("pickled-spec")
    register_core_resources(umbrella)
    eps = entry_points(group="pickled.mcp.subservers")
    for ep in sorted(eps, key=lambda e: e.name):
        build_subserver = ep.load()
        child = build_subserver()
        logger.info("mounting MCP subserver namespace=%s", ep.name)
        umbrella.mount(child, namespace=ep.name)
    return umbrella


@click.group()
def main() -> None:
    """pickled-spec umbrella CLI."""


@main.command("mcp")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "http"]),
    default="stdio",
    show_default=True,
)
@click.option("--host", default=None, help="Bind host for HTTP transport.")
@click.option("--port", type=int, default=None, help="Bind port for HTTP transport.")
@click.option(
    "--allow-public",
    is_flag=True,
    default=False,
    help="Required to bind 0.0.0.0.",
)
def mcp(
    transport: str,
    host: str | None,
    port: int | None,
    allow_public: bool,
) -> None:
    """Run the umbrella MCP server (all family packages mounted)."""
    if transport == "stdio":
        setup_logging_for_stdio()
    umbrella = build_umbrella()
    kwargs = resolve_transport(transport, host, port, allow_public)  # type: ignore[arg-type]
    transport_name = kwargs.pop("transport")
    umbrella.run(transport=transport_name, **kwargs)


# Back-compat alias for console script entry if referenced as ``cli``.
cli = mcp

__all__ = ["build_umbrella", "cli", "main", "mcp"]
