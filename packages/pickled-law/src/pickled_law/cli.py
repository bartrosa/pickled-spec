"""Command-line interface for pickled-law."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from pickled_bdd.adapters.pytest_bdd import PytestBddAdapter
from pickled_core import Verdict

from pickled_law import load_corpus, resolve_corpus_name
from pickled_law.gates import coverage_gate
from pickled_law.rtm import render_rtm_markdown


@click.group()
@click.version_option()
def main() -> None:
    """pickled-law: regulatory traceability for the pickled-* family."""


@main.command()
@click.option(
    "--corpus",
    "corpus_name",
    type=str,
    default=None,
    help="Built-in corpus short name (e.g. 'hipaa-164.312').",
)
@click.option(
    "--corpus-path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Path to a custom corpus YAML.",
)
@click.option(
    "--feature",
    "feature_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Gherkin feature file to analyse.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Write the RTM to this path. Default: stdout.",
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Suppress RTM on stdout; print only the verdict line. "
    "If --output is set, the RTM is still written to the file.",
)
def check(
    corpus_name: str | None,
    corpus_path: Path | None,
    feature_path: Path,
    output: Path | None,
    quiet: bool,
) -> None:
    """Check feature coverage against a regulatory corpus."""
    has_named = corpus_name is not None
    has_path = corpus_path is not None
    if has_named == has_path:
        raise click.UsageError("Provide exactly one of --corpus or --corpus-path.")

    if corpus_name is not None:
        try:
            resolved_path = resolve_corpus_name(corpus_name)
        except KeyError as exc:
            raise click.UsageError(str(exc)) from exc
        short_name = corpus_name.split("-", 1)[0].lower()
    else:
        assert corpus_path is not None
        resolved_path = corpus_path
        short_name = resolved_path.stem.lower()

    corpus = load_corpus(resolved_path)
    adapter = PytestBddAdapter()
    feature = adapter.parse_feature_file(feature_path)

    report = coverage_gate(feature, corpus, corpus_short_name=short_name)

    rtm = render_rtm_markdown(
        report,
        corpus,
        feature_path=str(feature_path),
    )

    if quiet:
        v = report.gate_result.verdict
        label = "PASS" if v == Verdict.PASS else "FAIL"
        click.echo(f"{label}: {report.gate_result.notes}")
        if output is not None:
            output.write_text(rtm, encoding="utf-8")
            click.echo(f"RTM written to {output}", err=True)
    elif output is not None:
        output.write_text(rtm, encoding="utf-8")
        click.echo(f"RTM written to {output}", err=True)
        click.echo(report.gate_result.notes, err=True)
    else:
        click.echo(rtm)

    if report.gate_result.verdict != Verdict.PASS:
        sys.exit(1)


if __name__ == "__main__":
    main()
