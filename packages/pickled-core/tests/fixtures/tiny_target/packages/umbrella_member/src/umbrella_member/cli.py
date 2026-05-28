"""Umbrella-style CLI placeholder for MCP detection tests."""

from __future__ import annotations

import click


@click.group()
def main() -> None:
    """Umbrella member CLI."""


@main.group()
def mcp() -> None:
    """MCP subcommands."""


@mcp.command("serve")
def mcp_serve() -> None:
    """Plumbing: start MCP server."""
    click.echo("serve")
