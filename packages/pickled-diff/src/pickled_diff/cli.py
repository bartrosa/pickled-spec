"""CLI entry point for pickled-diff."""

from __future__ import annotations

import json
import shlex
import sys
from pathlib import Path
from typing import Any

import click
from pickled_core import PickledMCPServer, Verdict

from pickled_diff import mcp_tools
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


@main.command()
def serve() -> None:
    """Run the pickled-diff MCP server (stdio)."""
    server = PickledMCPServer("pickled-diff")
    mcp_tools.register(server)
    server.serve()


if __name__ == "__main__":
    main()
