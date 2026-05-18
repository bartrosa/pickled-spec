"""Command-line interface for pickled-rules."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from pickled_bdd.adapters.pytest_bdd import PytestBddAdapter
from pickled_core import Verdict

from pickled_rules.builtin import BUILTIN_RULESETS, resolve_ruleset_name
from pickled_rules.gates import coverage_gate
from pickled_rules.loader import load_ruleset
from pickled_rules.report import render_coverage_json, render_coverage_markdown


def _resolve_ruleset_path(ruleset: str) -> Path:
    if ruleset in BUILTIN_RULESETS:
        return resolve_ruleset_name(ruleset)
    path = Path(ruleset)
    if not path.is_file():
        raise click.ClickException(f"Rule set file not found: {ruleset}")
    return path


@click.group()
@click.version_option()
def main() -> None:
    """pickled-rules: rule coverage analysis for project artifacts."""


@main.command()
@click.option(
    "--ruleset",
    required=True,
    help="Built-in rule set name or path to a YAML rule set file.",
)
@click.option(
    "--feature",
    "feature_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    required=True,
    help="Gherkin feature file to analyse.",
)
@click.option(
    "--ruleset-name",
    default=None,
    help="Short name for tag prefix (default: built-in name or file stem).",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["markdown", "json"], case_sensitive=False),
    default="markdown",
    show_default=True,
    help="Report output format.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Write the report to this path. Default: stdout.",
)
@click.option(
    "--quiet",
    is_flag=True,
    help="Suppress report on stdout; print only the verdict line. "
    "If --output is set, the report is still written to the file.",
)
def check(
    ruleset: str,
    feature_path: Path,
    ruleset_name: str | None,
    output_format: str,
    output: Path | None,
    quiet: bool,
) -> None:
    """Check feature coverage against a YAML rule set."""
    try:
        resolved_path = _resolve_ruleset_path(ruleset)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc

    if ruleset_name is not None:
        short_name = ruleset_name.lower()
    elif ruleset in BUILTIN_RULESETS:
        short_name = ruleset.lower()
    else:
        short_name = resolved_path.stem.lower()

    ruleset_obj = load_ruleset(resolved_path)
    feature = PytestBddAdapter().parse_feature_file(feature_path)

    report = coverage_gate(feature, ruleset_obj, ruleset_short_name=short_name)

    if output_format.lower() == "json":
        body = render_coverage_json(
            report, ruleset_obj, feature_path=str(feature_path)
        )
    else:
        body = render_coverage_markdown(
            report, ruleset_obj, feature_path=str(feature_path)
        )

    if quiet:
        v = report.gate_result.verdict
        label = "PASS" if v == Verdict.PASS else "FAIL"
        click.echo(f"{label}: {report.gate_result.notes}")
        if output is not None:
            output.write_text(body, encoding="utf-8")
            click.echo(f"Report written to {output}", err=True)
    elif output is not None:
        output.write_text(body, encoding="utf-8")
        click.echo(f"Report written to {output}", err=True)
        click.echo(report.gate_result.notes, err=True)
    else:
        click.echo(body)

    if report.gate_result.verdict != Verdict.PASS:
        sys.exit(1)


if __name__ == "__main__":
    main()
