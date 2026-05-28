"""CLI entry point for pickled-bdd."""

from __future__ import annotations

import click
from pathlib import Path

from pickled_core import AmbiguityFinding, GateResult, LLMClient, Verdict

from pickled_bdd.drafter import FeatureDrafter


@click.group()
@click.version_option()
def main() -> None:
    """pickled-bdd — LLM-to-Gherkin bridge."""


@main.command()
@click.argument("story_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "-o",
    "--output",
    type=click.Path(dir_okay=False),
    help="Write the drafted feature to this path. Defaults to stdout.",
)
def draft(story_file: str, output: str | None) -> None:
    """Draft a .feature file from a user story (Markdown)."""
    story = Path(story_file).read_text(encoding="utf-8")
    llm = _build_llm_client()
    result = FeatureDrafter(llm).draft_from_story(story)

    if output:
        Path(output).write_text(result.text, encoding="utf-8")
        click.echo(f"Wrote {output}", err=True)
    else:
        click.echo(result.text)


def run_ambiguity_gate(feature_file: str | Path, llm: LLMClient | None) -> GateResult:
    """Canonical ambiguity gate entry point (CLI, alias, mine evaluate)."""
    from pickled_bdd.adapters.pytest_bdd import PytestBddAdapter
    from pickled_bdd.gates.ambiguity import AmbiguityGate

    feature = PytestBddAdapter().parse_feature_file(str(feature_file))
    if llm is None:
        return GateResult(
            gate_name="ambiguity",
            verdict=Verdict.PASS,
            notes="LLM unavailable; ambiguity gate skipped",
        )
    return AmbiguityGate(llm).run(feature)


def _ambiguity_result_to_json(result: GateResult) -> dict[str, object]:
    return {
        "gate": result.gate_name,
        "verdict": result.verdict.value,
        "notes": result.notes,
        "findings": [
            {
                "scenario": f.target_name,
                "alternatives": list(f.alternatives),
                "suggested_fix": f.suggested_fix,
            }
            for f in result.findings
            if isinstance(f, AmbiguityFinding)
        ],
    }


def _exit_for_verdict(verdict: Verdict) -> None:
    import sys

    exit_codes = {Verdict.PASS: 0, Verdict.WARN: 1, Verdict.FAIL: 2}
    sys.exit(exit_codes[verdict])


@main.command()
@click.argument("feature_file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--gate",
    type=click.Choice(["ambiguity", "all"]),
    default="ambiguity",
    show_default=True,
    help="Which gate to run.",
)
def check(feature_file: str, gate: str) -> None:
    """Run compensating gates against a .feature file."""
    import json as _json

    _ = gate  # v0.1: only ambiguity; "all" resolves to the same gate.
    llm = _build_llm_client()
    result = run_ambiguity_gate(feature_file, llm)
    click.echo(_json.dumps(_ambiguity_result_to_json(result), indent=2, ensure_ascii=False))
    _exit_for_verdict(result.verdict)


@main.command()
@click.argument("feature_file", type=click.Path(exists=True, dir_okay=False))
def ambiguity(feature_file: str) -> None:
    """Run the ambiguity gate (alias for ``check --gate ambiguity``)."""
    import json as _json

    click.echo("(equivalent to: pickled-bdd check --gate ambiguity)", err=True)
    llm = _build_llm_client()
    result = run_ambiguity_gate(feature_file, llm)
    click.echo(_json.dumps(_ambiguity_result_to_json(result), indent=2, ensure_ascii=False))
    _exit_for_verdict(result.verdict)


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
    """Run the pickled-bdd MCP server."""
    from pickled_bdd.mcp_cli import cli as mcp_cli_main

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
    """Deprecated alias for ``pickled-bdd mcp serve``."""
    click.echo(
        "Warning: `pickled-bdd serve` is deprecated; use `pickled-bdd mcp serve`.",
        err=True,
    )
    from pickled_bdd.mcp_cli import cli as mcp_cli_main

    mcp_cli_main.main(args=["--transport", "stdio"], standalone_mode=True)


def _build_llm_client() -> LLMClient:
    """Build an LLM client. Override via PICKLED_BDD_LLM_FACTORY for tests."""
    from pickled_core.llm.bootstrap import build_default_client
    from pickled_core.llm.config import ConfigError

    try:
        return build_default_client(factory_env="PICKLED_BDD_LLM_FACTORY")
    except ConfigError as exc:
        raise click.ClickException(str(exc)) from exc


if __name__ == "__main__":
    main()
