"""Command-line interface for pickled-rules."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from pickled_bdd.adapters.pytest_bdd import PytestBddAdapter
from pickled_core import Verdict

from pickled_rules.builtin import BUILTIN_RULESETS, resolve_ruleset_name
from pickled_rules.gates import coverage_gate, coverage_gate_features
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


@main.command("list-rules")
@click.option(
    "--ruleset",
    required=True,
    help="Built-in rule set name or path to a YAML rule set file.",
)
def list_rules(ruleset: str) -> None:
    """List rule ids from a YAML rule set."""
    try:
        resolved_path = _resolve_ruleset_path(ruleset)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc
    ruleset_obj = load_ruleset(resolved_path)
    for rule in ruleset_obj.rules:
        click.echo(f"{rule.id}\t{rule.enforcement}\t{rule.title}")


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
    default=None,
    help="Single Gherkin feature file to analyse.",
)
@click.option(
    "--feature-glob",
    default=None,
    help="Glob of feature files; multiple matches are checked as one union "
    "(strict rules must appear across the set, not in each file).",
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
    feature_path: Path | None,
    feature_glob: str | None,
    ruleset_name: str | None,
    output_format: str,
    output: Path | None,
    quiet: bool,
) -> None:
    """Check feature coverage against a YAML rule set."""
    if feature_path is None and feature_glob is None:
        raise click.ClickException("Provide --feature or --feature-glob")
    if feature_path is not None and feature_glob is not None:
        raise click.ClickException("Use only one of --feature or --feature-glob")

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
    if feature_glob:
        from glob import glob

        paths = [Path(p) for p in glob(feature_glob, recursive=True)]
        paths = [p for p in paths if p.is_file()]
    else:
        assert feature_path is not None
        paths = [feature_path]

    if not paths:
        raise click.ClickException("No feature files matched")

    adapter = PytestBddAdapter()
    parsed = [adapter.parse_feature_file(fp) for fp in sorted(paths)]

    if len(parsed) == 1:
        report = coverage_gate(parsed[0], ruleset_obj, ruleset_short_name=short_name)
        worst = report.gate_result.verdict
        if output_format.lower() == "json":
            body = render_coverage_json(report, ruleset_obj, feature_path=str(paths[0]))
        else:
            body = render_coverage_markdown(report, ruleset_obj, feature_path=str(paths[0]))
    else:
        report = coverage_gate_features(
            parsed, ruleset_obj, ruleset_short_name=short_name
        )
        worst = report.gate_result.verdict
        label = ", ".join(str(p) for p in sorted(paths))
        if output_format.lower() == "json":
            body = render_coverage_json(report, ruleset_obj, feature_path=label)
        else:
            body = render_coverage_markdown(report, ruleset_obj, feature_path=label)
        if not quiet:
            click.echo(
                f"Union coverage across {len(paths)} feature file(s).",
                err=True,
            )

    if quiet:
        label = "PASS" if worst == Verdict.PASS else "FAIL"
        click.echo(f"{label}: checked {len(paths)} feature(s)")
        if output is not None:
            output.write_text(body, encoding="utf-8")
    elif output is not None:
        output.write_text(body, encoding="utf-8")
        click.echo(f"Report written to {output}", err=True)
    else:
        click.echo(body)

    if worst != Verdict.PASS:
        sys.exit(1)


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
    """Run the pickled-rules MCP server."""
    from pickled_rules.mcp_cli import cli as mcp_cli_main

    args = ["--transport", transport]
    if host:
        args.extend(["--host", host])
    if port is not None:
        args.extend(["--port", str(port)])
    if allow_public:
        args.append("--allow-public")
    mcp_cli_main.main(args=args, standalone_mode=True)


if __name__ == "__main__":
    main()
