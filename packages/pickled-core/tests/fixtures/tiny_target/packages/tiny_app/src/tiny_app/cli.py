"""Minimal Click CLI for mine inventory tests."""

from __future__ import annotations

import click


@click.group()
def main() -> None:
    """Tiny target CLI."""


@main.command()
@click.argument("name")
def greet(name: str) -> None:
    """Greet someone by name (required argument for significance)."""
    click.echo(f"Hello, {name}!")


@main.command()
def ping() -> None:
    """Return pong for health checks."""
    click.echo("pong")
