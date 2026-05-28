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


def _count_scenarios(features: list[Path]) -> int:
    total = 0
    for path in features:
        total += path.read_text(encoding="utf-8").count("Scenario:")
    return total


def _count_tagged_scenarios(tags: dict[str, Any] | None) -> int:
    if not tags:
        return 0
    count = 0
    for entry in tags.get("features", []):
        if not isinstance(entry, dict):
            continue
        for scenario in entry.get("scenarios", []):
            if isinstance(scenario, dict) and scenario.get("selected"):
                count += 1
    return count


def _next_moves(
    *,
    inventory: dict[str, Any] | None,
    stories: list[Path],
    features: list[Path],
    tags: dict[str, Any] | None,
    coverage: dict[str, Any] | None,
    ambiguity: dict[str, Any] | None,
    surfaces_filter: tuple[str, ...],
) -> list[str]:
    moves: list[str] = []
    if surfaces_filter:
        joined = ", ".join(surfaces_filter)
        moves.append(
            f"This run covered only surfaces matching `--surfaces {joined}`; "
            "run without `--surfaces` for full coverage."
        )
    if not inventory:
        moves.append("Run `pickled-spec mine inventory <target>` first.")
        return moves

    if coverage:
        for entry in coverage.get("rulesets", []):
            if not isinstance(entry, dict):
                continue
            if entry.get("verdict") != "pass":
                unref = entry.get("unreferenced_strict_rule_ids", [])
                if unref:
                    ids = ", ".join(str(r) for r in unref[:10])
                    moves.append(f"Add a story/feature covering strict rules: {ids}")

    if ambiguity:
        for entry in ambiguity.get("features", []):
            if not isinstance(entry, dict):
                continue
            if entry.get("verdict") == "fail":
                feature = entry.get("feature", "")
                surface_id = Path(feature).stem
                moves.append(
                    f"Re-draft `{surface_id}` with tighter scope; see "
                    "evaluation/ambiguity.json findings."
                )

    if tags and features:
        tagged = _count_tagged_scenarios(tags)
        scenario_total = _count_scenarios(features)
        if tagged < scenario_total:
            moves.append(
                "Manually review tag proposals for scenarios without a selected tag."
            )

    if not stories:
        moves.append("Generate stories from inventory surfaces.")
    if not features:
        moves.append("Draft features from generated stories (requires LLM).")
    elif not coverage and not ambiguity:
        moves.append("Run `pickled-spec mine evaluate` for coverage and ambiguity gates.")

    return moves


def render_mining_report(
    output_dir: Path,
    *,
    target_label: str | None = None,
    surfaces_filter: tuple[str, ...] = (),
) -> str:
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
    if surfaces_filter:
        lines.append(f"Surface filter: `{', '.join(surfaces_filter)}`")
    lines.append("")

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
    tags = read_json_optional(paths.tags_proposals)
    coverage = read_json_optional(paths.coverage_json)
    ambiguity = read_json_optional(paths.ambiguity_json)

    lines.append(f"- Stories on disk: {len(stories)}")
    lines.append(f"- Features on disk: {len(features)}")
    lines.append(f"- Tag proposals: {'yes' if tags else 'no'}")
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

    if tags:
        lines.append("## Tag proposals")
        lines.append("")
        feature_entries = tags.get("features", [])
        if isinstance(feature_entries, list):
            for entry in feature_entries:
                if not isinstance(entry, dict):
                    continue
                feature_path = entry.get("feature_path", "")
                scenarios = entry.get("scenarios", [])
                count = len(scenarios) if isinstance(scenarios, list) else 0
                lines.append(f"- `{feature_path}`: {count} scenario(s)")
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
        lines.append("| Rule set | Verdict | Unreferenced strict |")
        lines.append("|----------|---------|--------------------:|")
        for entry in coverage.get("rulesets", []):
            if not isinstance(entry, dict):
                continue
            short_name = entry.get("short_name", "")
            verdict = entry.get("verdict", "unknown")
            unref = entry.get("unreferenced_strict_rule_ids", [])
            count = len(unref) if isinstance(unref, list) else 0
            lines.append(f"| {short_name} | {verdict} | {count} |")
            if unref and verdict != "pass":
                lines.append("")
                lines.append(f"Unreferenced strict rules in `{short_name}`:")
                for rule_id in unref:
                    lines.append(f"- `{rule_id}`")
                lines.append("")
        lines.append("")

    if ambiguity:
        lines.append("## Ambiguity by feature")
        lines.append("")
        lines.append("| Feature | Verdict | Findings | Skipped |")
        lines.append("|---------|---------|----------:|---------|")
        for entry in ambiguity.get("features", []):
            if not isinstance(entry, dict):
                continue
            lines.append(
                f"| `{entry.get('feature', '')}` | {entry.get('verdict', '')} | "
                f"{entry.get('finding_count', 0)} | "
                f"{'yes' if entry.get('skipped') else 'no'} |"
            )
        lines.append("")

    moves = _next_moves(
        inventory=inventory,
        stories=stories,
        features=features,
        tags=tags,
        coverage=coverage,
        ambiguity=ambiguity,
        surfaces_filter=surfaces_filter,
    )
    lines.append("## Suggested next moves")
    lines.append("")
    if moves:
        lines.extend(f"- {move}" for move in moves)
    else:
        lines.append("- Mining pipeline complete for this output directory.")
    lines.append("")

    return "\n".join(lines)


def run_report(
    output_dir: Path,
    *,
    target_label: str | None = None,
    verbose: bool = False,
    surfaces_filter: tuple[str, ...] = (),
) -> Path:
    """Write ``mining-report.md`` and return its path."""
    paths = MiningPaths(output_dir.resolve())
    paths.root.mkdir(parents=True, exist_ok=True)
    report = render_mining_report(
        paths.root,
        target_label=target_label,
        surfaces_filter=surfaces_filter,
    )
    write_text(paths.mining_report, report)
    if verbose:
        sys.stderr.write(f"[INFO] Wrote {paths.mining_report}\n")
    return paths.mining_report


def print_stdout_summary(output_dir: Path, *, target_label: str) -> None:
    """Brief stderr summary for CI."""
    paths = MiningPaths(output_dir.resolve())
    stories = list(paths.stories_dir.glob("*.story.md")) if paths.stories_dir.is_dir() else []
    features = list(paths.features_dir.glob("*.feature")) if paths.features_dir.is_dir() else []
    tags = read_json_optional(paths.tags_proposals)
    coverage = read_json_optional(paths.coverage_json)
    ambiguity = read_json_optional(paths.ambiguity_json)

    scenario_count = _count_scenarios(features)
    tagged_count = _count_tagged_scenarios(tags)

    coverage_pass = coverage_fail = 0
    if coverage:
        for entry in coverage.get("rulesets", []):
            if isinstance(entry, dict) and entry.get("verdict") == "pass":
                coverage_pass += 1
            elif isinstance(entry, dict):
                coverage_fail += 1

    ambiguity_pass = ambiguity_fail = 0
    if ambiguity:
        for entry in ambiguity.get("features", []):
            if not isinstance(entry, dict):
                continue
            if entry.get("verdict") == "pass":
                ambiguity_pass += 1
            else:
                ambiguity_fail += 1

    sys.stderr.write(f"mining of {target_label} complete:\n")
    sys.stderr.write(
        f"  surfaces={len(stories)} stories={len(stories)} "
        f"features={len(features)} scenarios={scenario_count} tagged={tagged_count}\n"
    )
    if coverage:
        total = coverage_pass + coverage_fail
        sys.stderr.write(
            f"  coverage: {coverage_pass}/{total} rulesets pass, {coverage_fail} fail\n"
        )
    if ambiguity:
        total = ambiguity_pass + ambiguity_fail
        sys.stderr.write(
            f"  ambiguity: {ambiguity_pass}/{total} features pass, {ambiguity_fail} fail\n"
        )
    sys.stderr.write(f"report: {paths.mining_report}\n")


__all__ = ["render_mining_report", "run_report", "print_stdout_summary"]
