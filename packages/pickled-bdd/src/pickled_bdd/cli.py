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
def check() -> None:
    """Run gates against a .feature file. Implemented in PR-08."""
    raise click.ClickException("`check` lands in PR-08")


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
