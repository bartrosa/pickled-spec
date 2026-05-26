"""Minimal Click CLI for mine inventory tests."""

from __future__ import annotations

import click


@click.group()
def main() -> None:
    """Tiny target CLI for mining tests."""


@main.command()
@click.option("--name", required=True, help="Name to greet in the output message.")
def greet(name: str) -> None:
    """Greet someone by name."""
    click.echo(f"hello {name}")


@main.command()
def ping() -> None:
    """Health check."""
    click.echo("pong")
