"""CLI for ``pickled-spec mine``."""

from __future__ import annotations

from pathlib import Path

import click

from pickled_core.mine.inventory_stage import run_inventory
from pickled_core.mine.report_stage import print_stdout_summary, run_report

_OUTPUT_OPT = click.option(
    "--output",
    "output_dir",
    type=click.Path(file_okay=False, path_type=Path),
    default="./mining-output/",
    help="Mining output directory.",
)
_QUICK_OPT = click.option(
    "--quick/--interactive",
    default=True,
    help="Quick mode (default) or interactive prompts.",
)
_VERBOSE_OPT = click.option("--verbose", is_flag=True, help="Extra logging to stderr.")


@click.group()
def mine() -> None:
    """Mine a Python project for surfaces, stories, features, and gate results."""


@mine.command()
@click.argument(
    "target",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@_OUTPUT_OPT
@_QUICK_OPT
@_VERBOSE_OPT
@click.option("--no-mcp", is_flag=True, help="Skip MCP tools/list.")
@click.option("--mcp-timeout", type=float, default=30.0, show_default=True)
def inventory(
    target: Path,
    output_dir: Path,
    quick: bool,  # noqa: ARG001
    verbose: bool,
    no_mcp: bool,
    mcp_timeout: float,
) -> None:
    """Stage 1: introspect target and write inventory.json."""
    _ = quick
    run_inventory(
        target.resolve(),
        output_dir.resolve(),
        include_mcp=not no_mcp,
        mcp_timeout=mcp_timeout,
        verbose=verbose,
    )


@mine.command()
@click.argument(
    "target",
    type=click.Path(exists=True, file_okay=True, path_type=Path),
)
@_OUTPUT_OPT
@_QUICK_OPT
@_VERBOSE_OPT
def report(
    target: Path,
    output_dir: Path,
    quick: bool,  # noqa: ARG001
    verbose: bool,
) -> None:
    """Stage 6: render mining-report.md from pipeline outputs."""
    _ = quick
    out = output_dir.resolve()
    label = str(target)
    if target.is_dir() and (target / "inventory.json").is_file():
        out = target.resolve()
    run_report(out, target_label=label, verbose=verbose)
    print_stdout_summary(out, target_label=label)


@mine.command()
@click.argument("target", type=click.Path(exists=True, file_okay=False, path_type=Path))
@_OUTPUT_OPT
@_QUICK_OPT
@_VERBOSE_OPT
def stories(target: Path, output_dir: Path, quick: bool, verbose: bool) -> None:  # noqa: ARG001
    """Stage 2: emit stories (Phase 8b)."""
    _ = target, output_dir, quick, verbose
    click.echo("mine stories is not implemented yet (Phase 8b)", err=True)
    raise SystemExit(2)


@mine.command()
@click.argument("target", type=click.Path(exists=True, file_okay=False, path_type=Path))
@_OUTPUT_OPT
@_QUICK_OPT
@_VERBOSE_OPT
def features(target: Path, output_dir: Path, quick: bool, verbose: bool) -> None:  # noqa: ARG001
    """Stage 3: draft features (Phase 8b)."""
    _ = target, output_dir, quick, verbose
    click.echo("mine features is not implemented yet (Phase 8b)", err=True)
    raise SystemExit(2)


@mine.command()
@click.argument("target", type=click.Path(exists=True, file_okay=False, path_type=Path))
@_OUTPUT_OPT
@_QUICK_OPT
@_VERBOSE_OPT
@click.option("--ruleset-dir", type=click.Path(path_type=Path), default=None)
@click.option("--ruleset-config", type=click.Path(path_type=Path), default=None)
def tag(
    target: Path,
    output_dir: Path,
    quick: bool,  # noqa: ARG001
    verbose: bool,  # noqa: ARG001
    ruleset_dir: Path | None,
    ruleset_config: Path | None,
) -> None:
    """Stage 4: tag scenarios (Phase 8b)."""
    _ = target, output_dir, quick, verbose, ruleset_dir, ruleset_config
    click.echo("mine tag is not implemented yet (Phase 8b)", err=True)
    raise SystemExit(2)


@mine.command()
@click.argument("target", type=click.Path(exists=True, file_okay=False, path_type=Path))
@_OUTPUT_OPT
@_QUICK_OPT
@_VERBOSE_OPT
def evaluate(target: Path, output_dir: Path, quick: bool, verbose: bool) -> None:  # noqa: ARG001
    """Stage 5: evaluate gates (Phase 8c)."""
    _ = target, output_dir, quick, verbose
    click.echo("mine evaluate is not implemented yet (Phase 8c)", err=True)
    raise SystemExit(2)


@mine.command(name="all")
@click.argument("target", type=click.Path(exists=True, file_okay=False, path_type=Path))
@_OUTPUT_OPT
@_QUICK_OPT
@_VERBOSE_OPT
@click.option("--no-mcp", is_flag=True, default=False)
@click.option("--mcp-timeout", type=float, default=30.0, show_default=True)
@click.option("--ruleset-dir", type=click.Path(path_type=Path), default=None)
@click.option("--ruleset-config", type=click.Path(path_type=Path), default=None)
@click.option("--overwrite-stories", is_flag=True, default=False)
@click.option("--overwrite-features", is_flag=True, default=False)
def mine_all(
    target: Path,
    output_dir: Path,
    quick: bool,  # noqa: ARG001
    verbose: bool,
    no_mcp: bool,
    mcp_timeout: float,
    ruleset_dir: Path | None,
    ruleset_config: Path | None,
    overwrite_stories: bool,
    overwrite_features: bool,
) -> None:
    """Run inventory then report (Phase 8a subset of full pipeline)."""
    _ = ruleset_dir, ruleset_config, overwrite_stories, overwrite_features, quick
    out = output_dir.resolve()
    tgt = target.resolve()
    run_inventory(tgt, out, include_mcp=not no_mcp, mcp_timeout=mcp_timeout, verbose=verbose)
    run_report(out, target_label=str(tgt), verbose=verbose)
    print_stdout_summary(out, target_label=str(tgt))


__all__ = ["mine"]
