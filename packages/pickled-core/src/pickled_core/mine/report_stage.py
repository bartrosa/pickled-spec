"""Stage 6: render mining-report.md from pipeline artifacts."""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pickled_core.mine.io import read_json_optional, write_text
from pickled_core.mine.types import MiningPaths


def _inventory_cli_table(data: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for pkg_name in sorted(data.get("packages", {})):
        pkg = data["packages"][pkg_name]
        for cmd in pkg.get("cli_commands", []):
            full = cmd.get("full_name", "")
            help_text = str(cmd.get("help", ""))[:80]
            lines.append(f"| `{pkg_name}` | `{full}` | {help_text} |")
    return lines


def render_mining_report(output_dir: Path, *, target_label: str | None = None) -> str:
    """Build markdown report from whichever stage outputs exist."""
    paths = MiningPaths(output_dir.resolve())
    inventory = read_json_optional(paths.inventory_json)

    lines: list[str] = [
        "# Mining report",
        "",
        f"Generated: `{datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
    ]
    if target_label:
        lines.append(f"Target: `{target_label}`")
    lines.append(f"Output: `{paths.root}`")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    if inventory:
        totals = inventory.get("totals", {})
        lines.append(f"- Packages: {totals.get('packages', 0)}")
        lines.append(f"- CLI commands: {totals.get('cli_commands', 0)}")
        lines.append(f"- MCP tools: {totals.get('mcp_tools', 0)}")
        lines.append(f"- Gates: {totals.get('gates', 0)}")
        lines.append(f"- ADRs: {totals.get('adrs', 0)}")
        lines.append(f"- Workspaces: {totals.get('workspaces', 0)}")
        if inventory.get("warnings"):
            lines.append(f"- Inventory warnings: {len(inventory['warnings'])}")
    else:
        lines.append("- Inventory: *not run*")
    lines.append("")

    stories = sorted(paths.stories_dir.glob("*.story.md")) if paths.stories_dir.is_dir() else []
    features = sorted(paths.features_dir.glob("*.feature")) if paths.features_dir.is_dir() else []
    lines.append(f"- Stories on disk: {len(stories)}")
    lines.append(f"- Features on disk: {len(features)}")
    tags = read_json_optional(paths.tags_proposals)
    lines.append(f"- Tag proposals: {'yes' if tags else 'no'}")
    coverage = read_json_optional(paths.coverage_json)
    ambiguity = read_json_optional(paths.ambiguity_json)
    lines.append(f"- Coverage evaluation: {'yes' if coverage else 'no'}")
    lines.append(f"- Ambiguity evaluation: {'yes' if ambiguity else 'no'}")
    lines.append("")

    if inventory:
        lines.append("## Inventory highlights")
        lines.append("")
        lines.append("| Package | CLI commands | MCP tools | Gates |")
        lines.append("|---------|-------------:|----------:|------:|")
        for pkg_name in sorted(inventory.get("packages", {})):
            pkg = inventory["packages"][pkg_name]
            lines.append(
                f"| {pkg_name} | {len(pkg.get('cli_commands', []))} | "
                f"{len(pkg.get('mcp_tools', []))} | {len(pkg.get('gates', []))} |"
            )
        lines.append("")
        if inventory.get("adrs"):
            lines.append("### ADRs")
            lines.append("")
            lines.append("| # | Title | Status |")
            lines.append("|---|-------|--------|")
            for adr in inventory["adrs"]:
                num = adr.get("number", "")
                title = adr.get("title", "")
                status = adr.get("status", "")
                lines.append(f"| {num} | {title} | {status} |")
            lines.append("")
        cli_rows = _inventory_cli_table(inventory)
        if cli_rows:
            lines.append("### CLI commands")
            lines.append("")
            lines.append("| Package | Command | Help |")
            lines.append("|---------|---------|------|")
            lines.extend(cli_rows[:50])
            if len(cli_rows) > 50:
                lines.append(f"| … | … | ({len(cli_rows) - 50} more) |")
            lines.append("")

    if stories:
        lines.append("## Stories generated")
        lines.append("")
        lines.append("| Surface | Path |")
        lines.append("|---------|------|")
        for path in stories:
            lines.append(f"| {path.stem} | `{path.relative_to(paths.root)}` |")
        lines.append("")

    if features:
        lines.append("## Features generated")
        lines.append("")
        lines.append("| Surface | Scenarios | Path |")
        lines.append("|---------|----------:|------|")
        for path in features:
            text = path.read_text(encoding="utf-8")
            scenario_count = text.count("Scenario:")
            lines.append(
                f"| {path.stem} | {scenario_count} | `{path.relative_to(paths.root)}` |"
            )
        lines.append("")

    if coverage:
        lines.append("## Coverage by rule set")
        lines.append("")
        for entry in coverage.get("rulesets", []):
            lines.append(
                f"- **{entry.get('short_name', '')}**: {entry.get('verdict', 'unknown')} "
                f"— {entry.get('notes', '')}"
            )
        lines.append("")

    if ambiguity:
        lines.append("## Ambiguity")
        lines.append("")
        for entry in ambiguity.get("features", []):
            lines.append(
                f"- `{entry.get('feature', '')}`: {entry.get('verdict', 'unknown')} "
                f"— {entry.get('notes', '')}"
            )
        lines.append("")

    lines.append("## Suggested next moves")
    lines.append("")
    if not inventory:
        lines.append("- Run `pickled-spec mine inventory <target>` first.")
    elif inventory.get("totals", {}).get("cli_commands", 0) == 0:
        lines.append("- No CLI commands found; verify the target exposes Click entry points.")
    else:
        lines.append("- Run remaining stages: `stories`, `features`, `tag`, `evaluate`.")
    if not stories:
        lines.append("- Generate stories from inventory surfaces.")
    if not features:
        lines.append("- Draft features from generated stories.")
    lines.append("")

    return "\n".join(lines)


def run_report(
    output_dir: Path,
    *,
    target_label: str | None = None,
    verbose: bool = False,
) -> Path:
    """Write ``mining-report.md`` and return its path."""
    paths = MiningPaths(output_dir.resolve())
    paths.root.mkdir(parents=True, exist_ok=True)
    report = render_mining_report(paths.root, target_label=target_label)
    write_text(paths.mining_report, report)
    if verbose:
        sys.stderr.write(f"[INFO] Wrote {paths.mining_report}\n")
    return paths.mining_report


def print_stdout_summary(output_dir: Path, *, target_label: str) -> None:
    """Brief summary for CI (stderr only except this is called from report with format json)."""
    paths = MiningPaths(output_dir.resolve())
    inventory = read_json_optional(paths.inventory_json)
    stories = len(list(paths.stories_dir.glob("*.story.md"))) if paths.stories_dir.is_dir() else 0
    features = len(list(paths.features_dir.glob("*.feature"))) if paths.features_dir.is_dir() else 0
    cli_count = 0
    if inventory:
        cli_count = inventory.get("totals", {}).get("cli_commands", 0)
    sys.stderr.write(
        f"mining of {target_label} complete: cli_commands={cli_count} "
        f"stories={stories} features={features}\n"
        f"report: {paths.mining_report}\n"
    )


__all__ = ["render_mining_report", "run_report", "print_stdout_summary"]
