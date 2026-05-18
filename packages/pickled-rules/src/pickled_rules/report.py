"""Render a rule coverage report in Markdown or JSON."""

from __future__ import annotations

import json

from pickled_core import Verdict

from pickled_rules.gates.coverage import CoverageReport
from pickled_rules.types import RuleSet


def render_coverage_markdown(
    report: CoverageReport,
    ruleset: RuleSet,
    *,
    feature_path: str | None = None,
) -> str:
    """Render a coverage report as a Markdown string."""
    lines: list[str] = []
    lines.append(f"# Coverage report — {ruleset.source_title}")
    lines.append("")
    lines.append(f"**Rule set:** {ruleset.source_title}")
    lines.append(f"**Source ID:** `{ruleset.source_id}`")
    lines.append(f"**Version:** {ruleset.source_version}")
    lines.append(f"**Applies to:** {ruleset.applies_to}")
    lines.append(f"**Maintainer:** {ruleset.maintainer}")
    lines.append(f"**Active from:** {ruleset.active_from.isoformat()}")
    if ruleset.source_url:
        lines.append(f"**Source:** <{ruleset.source_url}>")
    if feature_path:
        lines.append(f"**Feature analysed:** `{feature_path}`")
    lines.append("")

    verdict = report.gate_result.verdict
    badge = "✅ PASS" if verdict == Verdict.PASS else "❌ FAIL"
    lines.append(f"## Verdict: {badge}")
    lines.append("")
    lines.append(report.gate_result.notes)
    lines.append("")

    lines.append("## Referenced rules")
    lines.append("")
    lines.append("| Rule | Title | Enforcement | Referenced |")
    lines.append("|------|-------|-------------|------------|")
    referenced_ids = {r.id for r in report.referenced_rules}
    for rule in ruleset.rules:
        referenced = "✅" if rule.id in referenced_ids else "❌"
        safe_title = rule.title.replace("|", r"\|")
        lines.append(
            f"| `{rule.id}` | {safe_title} | {rule.enforcement} | {referenced} |"
        )
    lines.append("")

    strict_gaps = [r for r in report.unreferenced_rules if r.enforcement == "strict"]
    advisory_gaps = [r for r in report.unreferenced_rules if r.enforcement == "advisory"]
    informational_gaps = [
        r for r in report.unreferenced_rules if r.enforcement == "informational"
    ]

    if strict_gaps:
        lines.append("## Unreferenced strict rules")
        lines.append("")
        lines.append(
            "These rules are marked strict in the rule set but no scenario "
            "references them. Add scenarios with the appropriate tag, or "
            "document why the rule does not apply."
        )
        lines.append("")
        for rule in strict_gaps:
            lines.append(f"### `{rule.id}` — {rule.title}")
            lines.append("")
            lines.append("> " + rule.description.strip().replace("\n", "\n> "))
            lines.append("")

    if advisory_gaps:
        lines.append("## Unreferenced advisory rules")
        lines.append("")
        lines.append(
            "These rules are advisory — teams may implement them, defer them, "
            "or record an explicit decision not to apply them."
        )
        lines.append("")
        for rule in advisory_gaps:
            lines.append(f"- `{rule.id}` — {rule.title}")
        lines.append("")

    if informational_gaps:
        lines.append("## Unreferenced informational rules")
        lines.append("")
        for rule in informational_gaps:
            lines.append(f"- `{rule.id}` — {rule.title}")
        lines.append("")

    if report.unknown_references:
        lines.append("## Unknown references")
        lines.append("")
        lines.append(
            "These reference tags were found in scenarios but do not match "
            "any rule in the rule set. Likely a typo or a stale reference."
        )
        lines.append("")
        for ruleset_name, rule_id in report.unknown_references:
            lines.append(f"- `@{ruleset_name}:{rule_id}`")
        lines.append("")

    return "\n".join(lines)


def render_coverage_json(
    report: CoverageReport,
    ruleset: RuleSet,
    *,
    feature_path: str | None = None,
) -> str:
    """Serialize the coverage report as JSON."""
    payload = {
        "ruleset": {
            "source_id": ruleset.source_id,
            "source_title": ruleset.source_title,
            "source_version": ruleset.source_version,
        },
        "feature_path": feature_path,
        "verdict": report.gate_result.verdict.value,
        "notes": report.gate_result.notes,
        "referenced_rule_ids": [r.id for r in report.referenced_rules],
        "unreferenced_rule_ids": [r.id for r in report.unreferenced_rules],
        "unknown_references": [
            {"ruleset": rs, "rule_id": rid} for rs, rid in report.unknown_references
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)
