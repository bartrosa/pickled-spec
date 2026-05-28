"""Click CLI for callgraph inventory tests."""

from __future__ import annotations

import click

from callgraph_target.chain import entry
from callgraph_target.cycle import ping


@click.group()
def main() -> None:
    """Callgraph fixture CLI."""


@main.command("run-chain")
def run_chain() -> None:
    """Execute the linear chain entrypoint for mining tests (significant help)."""
    click.echo(entry())


@main.command("run-cycle")
def run_cycle() -> None:
    """Execute the ping/pong cycle entrypoint for mining tests (significant help)."""
    ping()
