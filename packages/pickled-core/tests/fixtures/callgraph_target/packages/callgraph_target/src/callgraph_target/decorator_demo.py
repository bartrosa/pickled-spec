"""Decorator registration must not appear as behavioral callees."""

from __future__ import annotations

import click


@click.group()
def main() -> None:
    """CLI root."""


@main.command()
def entry() -> None:
    """Surface under test."""
