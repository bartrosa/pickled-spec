"""Render a Requirements Traceability Matrix in Markdown."""

from __future__ import annotations

from pickled_core import Verdict

from pickled_law.gates.coverage import CoverageReport
from pickled_law.types import Corpus


def render_rtm_markdown(
    report: CoverageReport,
    corpus: Corpus,
    *,
    feature_path: str | None = None,
) -> str:
    """Render an RTM as a Markdown string."""
    lines: list[str] = []
    lines.append("# Requirements Traceability Matrix")
    lines.append("")
    lines.append(f"**Corpus:** {corpus.source_title}")
    lines.append(f"**Source ID:** `{corpus.source_id}`")
    lines.append(f"**Version:** {corpus.source_version}")
    lines.append(f"**Jurisdiction:** {corpus.jurisdiction}")
    lines.append(f"**Authority:** {corpus.authority}")
    lines.append(f"**Effective from:** {corpus.effective_from.isoformat()}")
    if corpus.source_url:
        lines.append(f"**Source:** <{corpus.source_url}>")
    if feature_path:
        lines.append(f"**Feature analysed:** `{feature_path}`")
    lines.append("")

    verdict = report.gate_result.verdict
    badge = "✅ PASS" if verdict == Verdict.PASS else "❌ FAIL"
    lines.append(f"## Verdict: {badge}")
    lines.append("")
    lines.append(report.gate_result.notes)
    lines.append("")

    lines.append("## Coverage")
    lines.append("")
    lines.append("| Rule | Title | Obligation | Covered |")
    lines.append("|------|-------|------------|---------|")
    cited_ids = {r.id for r in report.cited_rules}
    for rule in corpus.rules:
        covered = "✅" if rule.id in cited_ids else "❌"
        safe_title = rule.title.replace("|", r"\|")
        lines.append(
            f"| `{rule.id}` | {safe_title} | {rule.obligation} | {covered} |"
        )
    lines.append("")

    required_gaps = [r for r in report.uncited_rules if r.obligation == "required"]
    addressable_gaps = [
        r for r in report.uncited_rules if r.obligation == "addressable"
    ]

    if required_gaps:
        lines.append("## Required gaps")
        lines.append("")
        lines.append(
            "These rules are mandated by the corpus but no scenario "
            "cites them. Add scenarios with the appropriate tag, or "
            "document a justified exemption."
        )
        lines.append("")
        for rule in required_gaps:
            lines.append(f"### `{rule.id}` — {rule.title}")
            lines.append("")
            lines.append("> " + rule.text.strip().replace("\n", "\n> "))
            lines.append("")

    if addressable_gaps:
        lines.append("## Addressable gaps")
        lines.append("")
        lines.append(
            "These rules are addressable — your organisation may "
            "implement them, document an alternative measure, or "
            "justify why they do not apply. Each gap below requires "
            "a documented decision."
        )
        lines.append("")
        for rule in addressable_gaps:
            lines.append(f"- `{rule.id}` — {rule.title}")
        lines.append("")

    if report.unknown_citations:
        lines.append("## Unknown citations")
        lines.append("")
        lines.append(
            "These citation tags were found in scenarios but do not "
            "match any rule in the corpus. Likely a typo or a stale "
            "reference."
        )
        lines.append("")
        for corpus_name, rule_id in report.unknown_citations:
            lines.append(f"- `@{corpus_name}:{rule_id}`")
        lines.append("")

    return "\n".join(lines)
