"""Umbrella CLI for pickled-spec."""

from __future__ import annotations

from pathlib import Path

import click

from pickled_core.check_all import format_table, run_check_all
from pickled_core.mcp.umbrella import mcp
from pickled_core.mine.cli import mine


@click.group()
def main() -> None:
    """pickled-spec — umbrella CLI for the pickled-* family."""


main.add_command(mcp, name="mcp")
main.add_command(mine)


@main.command(name="check-all")
@click.option(
    "--workdir",
    default=".",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Workspace root (features/, specs/, infra/, migrations/).",
)
@click.option(
    "--warn-ok",
    is_flag=True,
    help="Exit 0 when only WARN verdicts occur (e.g. terraform or LLM not configured).",
)
def check_all(workdir: Path, warn_ok: bool) -> None:
    """Run workspace gates from every pickled-* package against a directory."""
    rows, exit_code = run_check_all(workdir.resolve(), warn_ok=warn_ok)
    click.echo(format_table(rows))
    raise SystemExit(exit_code)


__all__ = ["main"]
