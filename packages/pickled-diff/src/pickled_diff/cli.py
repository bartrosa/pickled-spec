"""CLI entry point for pickled-diff."""

from __future__ import annotations

import json
import shlex
import sys
from pathlib import Path
from typing import Any

import click
from pickled_core import Verdict

from pickled_diff.comparator import ExactEqComparator, StructuralJsonComparator
from pickled_diff.corpus import CorpusItem, InMemoryCorpus
from pickled_diff.gate import DifferentialOracleGate
from pickled_diff.runner import SubprocessRunner


def _comparator(name: str) -> ExactEqComparator | StructuralJsonComparator:
    if name == "structural_json":
        return StructuralJsonComparator()
    return ExactEqComparator()


def _gate_result_to_json(result: Any) -> dict[str, Any]:
    from pickled_diff.types import DifferentialFinding

    return {
        "gate": result.gate_name,
        "verdict": result.verdict.value,
        "notes": result.notes,
        "findings": [
            {
                "input_repr": f.input_repr,
                "oracle_output": f.oracle_output,
                "candidate_output": f.candidate_output,
                "diff_summary": f.diff_summary,
            }
            for f in result.findings
            if isinstance(f, DifferentialFinding)
        ],
    }


@click.group()
@click.version_option()
def main() -> None:
    """pickled-diff — differential oracle verification."""


@main.command()
@click.option("--oracle", required=True, help="Reference command (shell-quoted argv).")
@click.option("--candidate", required=True, help="Candidate command (shell-quoted argv).")
@click.option(
    "--corpus",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="JSON file: [{\"name\": \"...\", \"payload\": \"...\"}, ...]",
)
@click.option(
    "--comparator",
    type=click.Choice(["exact", "structural_json"], case_sensitive=False),
    default="exact",
    show_default=True,
)
@click.option("--timeout", "timeout_seconds", default=30.0, show_default=True)
def verify(
    oracle: str,
    candidate: str,
    corpus: Path,
    comparator: str,
    timeout_seconds: float,
) -> None:
    """Compare candidate vs reference across a JSON input corpus."""
    raw = json.loads(corpus.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise click.ClickException("Corpus JSON must be a list of {name, payload} objects")
    items = [
        CorpusItem(name=str(entry["name"]), payload=str(entry["payload"]))
        for entry in raw
        if isinstance(entry, dict)
    ]
    gate = DifferentialOracleGate(
        oracle=SubprocessRunner(
            shlex.split(oracle),
            name="oracle",
            timeout_seconds=timeout_seconds,
        ),
        candidate=SubprocessRunner(
            shlex.split(candidate),
            name="candidate",
            timeout_seconds=timeout_seconds,
        ),
        comparator=_comparator(comparator),
    )
    result = gate.run(InMemoryCorpus(items))
    click.echo(json.dumps(_gate_result_to_json(result), indent=2, ensure_ascii=False))
    exit_codes = {Verdict.PASS: 0, Verdict.WARN: 1, Verdict.FAIL: 2}
    sys.exit(exit_codes[result.verdict])


@main.group()
def mcp() -> None:
    """MCP server commands."""


@mcp.command("serve")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "http"]),
    default="stdio",
    show_default=True,
)
@click.option("--host", default=None)
@click.option("--port", type=int, default=None)
@click.option("--allow-public", is_flag=True, default=False)
def mcp_serve(
    transport: str,
    host: str | None,
    port: int | None,
    allow_public: bool,
) -> None:
    """Run the pickled-diff MCP server."""
    from pickled_diff.mcp_cli import cli as mcp_cli_main

    mcp_cli_main.main(
        args=[
            "--transport",
            transport,
            *(["--host", host] if host else []),
            *(["--port", str(port)] if port is not None else []),
            *(["--allow-public"] if allow_public else []),
        ],
        standalone_mode=False,
    )


@main.command()
def serve() -> None:
    """Deprecated alias for ``pickled-diff mcp serve``."""
    click.echo(
        "Warning: `pickled-diff serve` is deprecated; use `pickled-diff mcp serve`.",
        err=True,
    )
    mcp_serve(transport="stdio", host=None, port=None, allow_public=False)


if __name__ == "__main__":
    main()
