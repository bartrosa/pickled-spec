"""MCP tool registration for pickled-rules.

The MCP server is reachable over stdio or HTTP and may serve untrusted
clients (per the threat model that motivated PR #18: any caller of a
pickled-* MCP tool should be assumed hostile). Tools therefore accept
feature *text* rather than filesystem paths: an attacker that can pass a
path on the host triggers ``read_text`` on that path and, since
``gherkin``'s parser embeds the offending file contents verbatim into its
``CompositeParserException`` messages, gets an arbitrary-file-read
primitive against the server process (e.g. ``/etc/passwd``, dotenv files,
SSH keys). Forwarding text avoids that entire class of bug.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastmcp import FastMCP
from pickled_bdd.adapters.pytest_bdd import PytestBddAdapter
from pickled_core import Verdict
from pickled_core.llm import LLMClient

from pickled_rules.drafter import RuleSetDrafter
from pickled_rules.gates import coverage_gate
from pickled_rules.loader import load_ruleset_from_text as _load_ruleset_from_text


def register_with_fastmcp(app: FastMCP, *, llm: LLMClient | None = None) -> None:
    """Register rules tools on a FastMCP application."""
    adapter = PytestBddAdapter()
    drafter: RuleSetDrafter | None = RuleSetDrafter(llm) if llm is not None else None

    @app.tool(name="list_rules")
    def list_rules(*, ruleset_yaml_text: str) -> list[dict[str, str]]:
        """List rule summaries from a YAML rule set."""
        ruleset = _load_ruleset_from_text(ruleset_yaml_text)
        return [
            {
                "id": rule.id,
                "title": rule.title,
                "enforcement": rule.enforcement,
                "description": rule.description,
            }
            for rule in ruleset.rules
        ]

    @app.tool(name="check_ruleset_coverage")
    def check_ruleset_coverage(
        *,
        ruleset_yaml_text: str,
        feature_texts: list[str],
        ruleset_short_name: str,
    ) -> dict[str, Any]:
        """Check Gherkin features against a YAML rule set (coverage gate).

        ``feature_texts`` are the **contents** of ``.feature`` files. The
        previous version accepted server-side filesystem paths, which gave
        any MCP client an arbitrary-file-read primitive via parser error
        messages — see the module docstring.
        """
        ruleset = _load_ruleset_from_text(ruleset_yaml_text)
        reports: list[dict[str, Any]] = []
        verdicts: list[Verdict] = []
        for index, text in enumerate(feature_texts):
            feature = adapter.parse_feature_text(text, path=f"<feature-{index}>")
            report = coverage_gate(
                feature,
                ruleset,
                ruleset_short_name=ruleset_short_name,
            )
            gr = report.gate_result
            verdicts.append(gr.verdict)
            reports.append(
                {
                    "feature_index": index,
                    "verdict": gr.verdict.value,
                    "notes": gr.notes,
                    "referenced_rule_ids": [r.id for r in report.referenced_rules],
                    "unreferenced_rule_ids": [r.id for r in report.unreferenced_rules],
                    "unknown_references": [
                        {"ruleset": rs, "rule_id": rid} for rs, rid in report.unknown_references
                    ],
                }
            )
        if Verdict.FAIL in verdicts:
            overall = Verdict.FAIL
        elif Verdict.WARN in verdicts:
            overall = Verdict.WARN
        else:
            overall = Verdict.PASS
        return {
            "verdict": overall.value,
            "notes": f"checked {len(reports)} feature(s)",
            "reports": reports,
        }

    if drafter is None:

        @app.tool(name="draft_ruleset_from_brief")
        def _draft_ruleset_from_brief_stub(
            *,
            brief_text: str,
            ruleset_short_name: str,
            source_id: str,
            applies_to: str,
            active_from: str,
        ) -> dict[str, Any]:
            _ = (
                brief_text,
                ruleset_short_name,
                source_id,
                applies_to,
                active_from,
            )
            msg = (
                "LLM client not configured (set pickled.config.yaml or "
                "PICKLED_RULES_LLM_FACTORY)"
            )
            raise RuntimeError(msg)

    else:

        @app.tool(name="draft_ruleset_from_brief")
        def _draft_ruleset_from_brief(
            *,
            brief_text: str,
            ruleset_short_name: str,
            source_id: str,
            applies_to: str,
            active_from: str,
        ) -> dict[str, Any]:
            """Draft a YAML rule set from a natural-language brief."""
            result = drafter.draft_from_brief(
                brief_text=brief_text,
                ruleset_short_name=ruleset_short_name,
                source_id=source_id,
                applies_to=applies_to,
                active_from=active_from,
            )
            return {
                "ruleset_yaml_text": result.text,
                "rationale": result.rationale,
                "warnings": list(result.warnings),
            }


__all__ = ["register_with_fastmcp"]
