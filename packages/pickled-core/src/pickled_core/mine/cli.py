"""CLI for ``pickled-spec mine``."""

from __future__ import annotations

import functools
import sys
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

import click

from pickled_core.llm.bootstrap import build_default_client
from pickled_core.llm.config import ConfigError, load_config
from pickled_core.mine.code_stage import load_inventory_for_code, run_code
from pickled_core.mine.errors import MineError
from pickled_core.mine.evaluate_stage import run_evaluate
from pickled_core.mine.features_stage import run_features
from pickled_core.mine.inventory_stage import run_inventory
from pickled_core.mine.io import ensure_output_dir, parse_surfaces_filter
from pickled_core.mine.report_stage import print_stdout_summary, run_report
from pickled_core.mine.stories_stage import load_inventory_from_output, run_stories
from pickled_core.mine.tag_stage import resolve_ruleset_sources, run_tag

if TYPE_CHECKING:
    from pickled_core.llm.base import LLMClient

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
_SURFACES_OPT = click.option(
    "--surfaces",
    default=None,
    help="Comma-separated filter on package name or surface-id substring.",
)
_MAX_PARALLEL_OPT = click.option(
    "--max-parallel",
    type=int,
    default=4,
    show_default=True,
    help="Max parallel LLM calls in quick mode (stories, features).",
)
_RULESET_DIR_OPT = click.option("--ruleset-dir", type=click.Path(path_type=Path), default=None)
_RULESET_CONFIG_OPT = click.option(
    "--ruleset-config", type=click.Path(path_type=Path), default=None
)
_OVERWRITE_STORIES_OPT = click.option("--overwrite-stories", is_flag=True, default=False)
_OVERWRITE_FEATURES_OPT = click.option("--overwrite-features", is_flag=True, default=False)
_DEPTH_OPT = click.option(
    "--depth",
    type=click.Choice(["signature", "body", "callgraph"], case_sensitive=False),
    default="body",
    show_default=True,
    help="How much source to collect per surface.",
)
_CALLEE_SCOPE_OPT = click.option(
    "--callee-scope",
    type=click.Choice(["self", "same-package", "any-pickled"], case_sensitive=False),
    default="same-package",
    show_default=True,
    help="Which intra-project callees to follow.",
)
_MAX_HOPS_OPT = click.option(
    "--max-hops",
    type=int,
    default=2,
    show_default=True,
    help="Callee expansion depth (callgraph only).",
)
_MAX_CALLEES_OPT = click.option(
    "--max-callees",
    type=int,
    default=8,
    show_default=True,
    help="Hard cap on collected callee units per surface.",
)
_MAX_CODE_LINES_OPT = click.option(
    "--max-code-lines",
    type=int,
    default=400,
    show_default=True,
    help="Hard cap on total source lines per surface.",
)
_DETECT_CYCLES_OPT = click.option(
    "--detect-cycles/--no-detect-cycles",
    default=True,
    show_default=True,
    help="Write code-context/_cycles.json from observed edges.",
)
_CODE_CONTEXT_OPT = click.option(
    "--code-context",
    "code_context_dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help=(
        "Directory with code-context/*.md (default: <output>/code-context when present)."
    ),
)

_F = TypeVar("_F", bound=Callable[..., Any])


def _build_llm(target: Path) -> LLMClient | None:
    cfg_path = target / "pickled.config.yaml"
    try:
        if cfg_path.is_file():
            return build_default_client(config=load_config(cfg_path))
        return build_default_client()
    except ConfigError:
        return None


def _catch_mine_errors(fn: _F) -> _F:
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return fn(*args, **kwargs)
        except (MineError, ValueError) as exc:
            click.echo(str(exc), err=True)
            raise SystemExit(2) from None

    return wrapper  # type: ignore[return-value]


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
@_SURFACES_OPT
def report(
    target: Path,
    output_dir: Path,
    quick: bool,  # noqa: ARG001
    verbose: bool,
    surfaces: str | None,
) -> None:
    """Stage 7: render mining-report.md from pipeline outputs."""
    _ = quick
    out = output_dir.resolve()
    label = str(target)
    if target.is_dir() and (target / "inventory.json").is_file():
        out = target.resolve()
    run_report(
        out,
        target_label=label,
        verbose=verbose,
        surfaces_filter=parse_surfaces_filter(surfaces),
    )
    print_stdout_summary(out, target_label=label)


@mine.command()
@click.argument("target", type=click.Path(exists=True, file_okay=False, path_type=Path))
@_OUTPUT_OPT
@_VERBOSE_OPT
@_SURFACES_OPT
@_DEPTH_OPT
@_CALLEE_SCOPE_OPT
@_MAX_HOPS_OPT
@_MAX_CALLEES_OPT
@_MAX_CODE_LINES_OPT
@_DETECT_CYCLES_OPT
@_catch_mine_errors
def code(
    target: Path,
    output_dir: Path,
    verbose: bool,
    surfaces: str | None,
    depth: str,
    callee_scope: str,
    max_hops: int,
    max_callees: int,
    max_code_lines: int,
    detect_cycles: bool,
) -> None:
    """Stage 2: extract code context per surface from inventory.json."""
    tgt = target.resolve()
    out = output_dir.resolve()
    inventory = load_inventory_for_code(out)
    run_code(
        inventory,
        tgt,
        out,
        depth=depth,  # type: ignore[arg-type]
        scope=callee_scope,  # type: ignore[arg-type]
        max_hops=max_hops,
        max_callees=max_callees,
        max_code_lines=max_code_lines,
        detect_cycles=detect_cycles,
        surfaces=parse_surfaces_filter(surfaces),
        verbose=verbose,
    )


@mine.command()
@click.argument("target", type=click.Path(exists=True, file_okay=False, path_type=Path))
@_OUTPUT_OPT
@_QUICK_OPT
@_VERBOSE_OPT
@_SURFACES_OPT
@_MAX_PARALLEL_OPT
@_OVERWRITE_STORIES_OPT
@_CODE_CONTEXT_OPT
@_catch_mine_errors
def stories(
    target: Path,
    output_dir: Path,
    quick: bool,
    verbose: bool,  # noqa: ARG001
    surfaces: str | None,
    max_parallel: int,
    overwrite_stories: bool,
    code_context_dir: Path | None,
) -> None:
    """Stage 3: emit stories from inventory.json."""
    _ = target
    out = output_dir.resolve()
    inventory = load_inventory_from_output(out)
    llm = _build_llm(target.resolve())
    ctx_dir = code_context_dir.resolve() if code_context_dir else None
    run_stories(
        inventory,
        out,
        llm=llm,
        quick=quick,
        overwrite=overwrite_stories,
        surfaces=parse_surfaces_filter(surfaces),
        max_parallel=max_parallel,
        code_context_dir=ctx_dir,
    )


@mine.command()
@click.argument("target", type=click.Path(exists=True, file_okay=False, path_type=Path))
@_OUTPUT_OPT
@_QUICK_OPT
@_VERBOSE_OPT
@_SURFACES_OPT
@_MAX_PARALLEL_OPT
@_OVERWRITE_FEATURES_OPT
@_catch_mine_errors
def features(
    target: Path,
    output_dir: Path,
    quick: bool,
    verbose: bool,  # noqa: ARG001
    surfaces: str | None,
    max_parallel: int,
    overwrite_features: bool,
) -> None:
    """Stage 4: draft features from stories."""
    _ = target
    out = output_dir.resolve()
    llm = _build_llm(target.resolve())
    run_features(
        out,
        llm=llm,
        quick=quick,
        overwrite=overwrite_features,
        surfaces=parse_surfaces_filter(surfaces),
        max_parallel=max_parallel,
    )


@mine.command()
@click.argument("target", type=click.Path(exists=True, file_okay=False, path_type=Path))
@_OUTPUT_OPT
@_QUICK_OPT
@_VERBOSE_OPT
@_SURFACES_OPT
@_RULESET_DIR_OPT
@_RULESET_CONFIG_OPT
@_catch_mine_errors
def tag(
    target: Path,
    output_dir: Path,
    quick: bool,
    verbose: bool,  # noqa: ARG001
    surfaces: str | None,
    ruleset_dir: Path | None,
    ruleset_config: Path | None,
) -> None:
    """Stage 5: tag scenarios in generated features."""
    tgt = target.resolve()
    out = output_dir.resolve()
    sources = resolve_ruleset_sources(
        tgt,
        ruleset_config=ruleset_config.resolve() if ruleset_config else None,
        ruleset_dir=ruleset_dir.resolve() if ruleset_dir else None,
    )
    run_tag(
        out,
        ruleset_sources=sources,
        quick=quick,
        surfaces=parse_surfaces_filter(surfaces),
    )


@mine.command()
@click.argument("target", type=click.Path(exists=True, file_okay=False, path_type=Path))
@_OUTPUT_OPT
@_VERBOSE_OPT
@_SURFACES_OPT
@_RULESET_DIR_OPT
@_RULESET_CONFIG_OPT
@_catch_mine_errors
def evaluate(
    target: Path,
    output_dir: Path,
    verbose: bool,  # noqa: ARG001
    surfaces: str | None,
    ruleset_dir: Path | None,
    ruleset_config: Path | None,
) -> None:
    """Stage 6: evaluate coverage and ambiguity gates."""
    tgt = target.resolve()
    out = output_dir.resolve()
    sources = resolve_ruleset_sources(
        tgt,
        ruleset_config=ruleset_config.resolve() if ruleset_config else None,
        ruleset_dir=ruleset_dir.resolve() if ruleset_dir else None,
    )
    llm = _build_llm(tgt)
    run_evaluate(
        out,
        ruleset_sources=sources,
        llm=llm,
        surfaces=parse_surfaces_filter(surfaces),
    )


@mine.command(name="all")
@click.argument("target", type=click.Path(exists=True, file_okay=False, path_type=Path))
@_OUTPUT_OPT
@_QUICK_OPT
@_VERBOSE_OPT
@_SURFACES_OPT
@_MAX_PARALLEL_OPT
@click.option("--no-mcp", is_flag=True, default=False)
@click.option("--mcp-timeout", type=float, default=30.0, show_default=True)
@_RULESET_DIR_OPT
@_RULESET_CONFIG_OPT
@_OVERWRITE_STORIES_OPT
@_OVERWRITE_FEATURES_OPT
@_DEPTH_OPT
@_CALLEE_SCOPE_OPT
@_MAX_HOPS_OPT
@_MAX_CALLEES_OPT
@_MAX_CODE_LINES_OPT
@_DETECT_CYCLES_OPT
@_catch_mine_errors
def mine_all(
    target: Path,
    output_dir: Path,
    quick: bool,
    verbose: bool,
    surfaces: str | None,
    max_parallel: int,
    no_mcp: bool,
    mcp_timeout: float,
    ruleset_dir: Path | None,
    ruleset_config: Path | None,
    overwrite_stories: bool,
    overwrite_features: bool,
    depth: str,
    callee_scope: str,
    max_hops: int,
    max_callees: int,
    max_code_lines: int,
    detect_cycles: bool,
) -> None:
    """Run inventory → code → stories → features → tag → evaluate → report."""
    tgt = target.resolve()
    out = output_dir.resolve()
    surface_tokens = parse_surfaces_filter(surfaces)
    run_inventory(
        tgt,
        out,
        include_mcp=not no_mcp,
        mcp_timeout=mcp_timeout,
        verbose=verbose,
    )
    inventory = load_inventory_from_output(out)
    code_result = run_code(
        inventory,
        tgt,
        out,
        depth=depth,  # type: ignore[arg-type]
        scope=callee_scope,  # type: ignore[arg-type]
        max_hops=max_hops,
        max_callees=max_callees,
        max_code_lines=max_code_lines,
        detect_cycles=detect_cycles,
        surfaces=surface_tokens,
        verbose=verbose,
    )
    if verbose and code_result.cycle_count:
        sys.stderr.write(
            f"[INFO] code stage: {code_result.cycle_count} cycle(s) in "
            f"{code_result.cycles_path}\n"
        )
    llm = _build_llm(tgt)
    run_stories(
        inventory,
        out,
        llm=llm,
        quick=quick,
        overwrite=overwrite_stories,
        surfaces=surface_tokens,
        max_parallel=max_parallel,
    )
    feat_result = run_features(
        out,
        llm=llm,
        quick=quick,
        overwrite=overwrite_features,
        surfaces=surface_tokens,
        max_parallel=max_parallel,
    )
    paths = ensure_output_dir(out)
    has_features = bool(list(paths.features_dir.glob("*.feature")))
    sources = resolve_ruleset_sources(
        tgt,
        ruleset_config=ruleset_config.resolve() if ruleset_config else None,
        ruleset_dir=ruleset_dir.resolve() if ruleset_dir else None,
    )
    if has_features and not feat_result.skipped_entire_stage:
        run_tag(out, ruleset_sources=sources, quick=quick, surfaces=surface_tokens)
        run_evaluate(out, ruleset_sources=sources, llm=llm, surfaces=surface_tokens)
    else:
        sys.stderr.write("[WARN] tag and evaluate skipped (no feature files)\n")
    run_report(
        out,
        target_label=str(tgt),
        verbose=verbose,
        surfaces_filter=surface_tokens,
    )
    print_stdout_summary(out, target_label=str(tgt))


__all__ = ["mine"]
