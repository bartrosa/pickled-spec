"""CLI entry point for pickled-bdd."""

from __future__ import annotations

import importlib
import os
from pathlib import Path
from typing import cast

import click
from pickled_core.llm.client import LLMClient

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
    import sys

    from pickled_core import AmbiguityFinding, Verdict

    from pickled_bdd.adapters.pytest_bdd import PytestBddAdapter
    from pickled_bdd.gates.ambiguity import AmbiguityGate

    _ = gate  # v0.1: only ambiguity; "all" resolves to the same gate.

    feature = PytestBddAdapter().parse_feature_file(feature_file)
    llm = _build_llm_client()

    gate_impl = AmbiguityGate(llm)
    result = gate_impl.run(feature)

    output = {
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
    click.echo(_json.dumps(output, indent=2, ensure_ascii=False))

    exit_codes = {Verdict.PASS: 0, Verdict.WARN: 1, Verdict.FAIL: 2}
    sys.exit(exit_codes[result.verdict])


@main.command()
def serve() -> None:
    """Start the MCP server. Implemented in PR-09 and v0.1.1."""
    raise click.ClickException("`serve` lands in PR-09 and v0.1.1")


def _build_llm_client() -> LLMClient:
    """Build an LLM client. Override via PICKLED_BDD_LLM_FACTORY for tests."""
    factory = os.environ.get("PICKLED_BDD_LLM_FACTORY")
    if factory:
        module_name, sep, attr = factory.partition(":")
        if not sep:
            raise click.ClickException(
                "PICKLED_BDD_LLM_FACTORY must be 'module:callable' "
                "(e.g. pickled_bdd.testing:build_fake_llm)"
            )
        module = importlib.import_module(module_name)
        builder = getattr(module, attr)
        return cast(LLMClient, builder())

    from pickled_core.llm.anthropic import AnthropicClient

    return AnthropicClient()


if __name__ == "__main__":
    main()
