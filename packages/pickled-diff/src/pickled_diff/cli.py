"""CLI entry point for pickled-diff."""

from __future__ import annotations

import json
import shlex
import sys
from pathlib import Path
from typing import Any

import click
from pickled_core import Verdict
from pickled_core.llm import LLMClient

from pickled_diff.comparator import ExactEqComparator, StructuralJsonComparator
from pickled_diff.corpus import CorpusItem, InMemoryCorpus
from pickled_diff.drafter import CorpusDrafter
from pickled_diff.gate import DifferentialOracleGate
from pickled_diff.runner import SubprocessRunner


def _comparator(name: str) -> ExactEqComparator | StructuralJsonComparator:
    if name == "structural_json":
        return StructuralJsonComparator()
    return ExactEqComparator()


def _build_llm_client() -> LLMClient:
    from pickled_core.llm.bootstrap import build_default_client
    from pickled_core.llm.config import ConfigError

    try:
        return build_default_client(factory_env="PICKLED_DIFF_LLM_FACTORY")
    except ConfigError as exc:
        raise click.ClickException(str(exc)) from exc


def _read_text_arg(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def _emit_corpus_output(
    *,
    items: tuple[dict[str, str], ...],
    rationale: str,
    warnings: tuple[str, ...],
    output: Path | None,
) -> None:
    body = json.dumps(list(items), indent=2, ensure_ascii=False) + "\n"
    if output is not None:
        output.write_text(body, encoding="utf-8")
    else:
        click.echo(body, nl=False)
        if not body.endswith("\n"):
            click.echo()
    if rationale:
        for line in rationale.splitlines():
            click.echo(f"rationale: {line}", err=True)
    for warning in warnings:
        click.echo(f"warning: {warning}", err=True)
    if warnings:
        raise SystemExit(1)


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


@main.command("draft-corpus")
@click.option(
    "--seeds",
    required=True,
    help="JSON file with seed items, or '-' for stdin.",
)
@click.option("--target-size", required=True, type=int, help="Total corpus size.")
@click.option(
    "--notes",
    default=None,
    help="Optional notes file path or '-' for stdin.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Write corpus JSON to this path. Default: stdout.",
)
def draft_corpus(
    seeds: str,
    target_size: int,
    notes: str | None,
    output: Path | None,
) -> None:
    """Expand seed examples into a larger differential corpus."""
    if target_size < 1:
        raise click.ClickException("--target-size must be a positive integer")
    raw = json.loads(_read_text_arg(seeds))
    if not isinstance(raw, list):
        raise click.ClickException("seeds JSON must be a list")
    seed_examples: list[dict[str, str]] = []
    for entry in raw:
        if not isinstance(entry, dict):
            raise click.ClickException("each seed must be an object")
        name = entry.get("name")
        payload = entry.get("payload")
        if not isinstance(name, str) or not isinstance(payload, str):
            raise click.ClickException("each seed needs string name and payload")
        seed_examples.append({"name": name, "payload": payload})
    notes_text: str | None = None
    if notes is not None:
        notes_text = _read_text_arg(notes)
    try:
        llm = _build_llm_client()
        result = CorpusDrafter(llm).draft_from_examples(
            seed_examples=seed_examples,
            target_size=target_size,
            notes=notes_text,
        )
    except click.ClickException:
        raise
    except Exception as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(2) from exc
    _emit_corpus_output(
        items=result.items,
        rationale=result.rationale,
        warnings=result.warnings,
        output=output,
    )


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
