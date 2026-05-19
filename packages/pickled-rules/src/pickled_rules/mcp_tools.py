"""MCP tool registration for pickled-rules."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

if TYPE_CHECKING:
    from fastmcp import FastMCP
from pickled_bdd.adapters.pytest_bdd import PytestBddAdapter
from pickled_core import Verdict

from pickled_rules.gates import coverage_gate
from pickled_rules.loader import RuleSetValidationError, load_ruleset


def _load_ruleset_from_text(ruleset_yaml_text: str) -> Any:
    data = yaml.safe_load(ruleset_yaml_text)
    if not isinstance(data, dict):
        raise RuleSetValidationError("YAML root must be a mapping")
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".yaml",
        delete=False,
        encoding="utf-8",
    ) as fp:
        fp.write(ruleset_yaml_text)
        path = Path(fp.name)
    try:
        return load_ruleset(path)
    finally:
        path.unlink(missing_ok=True)


def register_with_fastmcp(app: FastMCP) -> None:
    """Register rules tools on a FastMCP application."""
    adapter = PytestBddAdapter()

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
        feature_file_paths: list[str],
        ruleset_short_name: str,
    ) -> dict[str, Any]:
        """Check Gherkin features against a YAML rule set (coverage gate)."""
        ruleset = _load_ruleset_from_text(ruleset_yaml_text)
        reports: list[dict[str, Any]] = []
        verdicts: list[Verdict] = []
        for path_str in feature_file_paths:
            feature = adapter.parse_feature_file(path_str)
            report = coverage_gate(
                feature,
                ruleset,
                ruleset_short_name=ruleset_short_name,
            )
            gr = report.gate_result
            verdicts.append(gr.verdict)
            reports.append(
                {
                    "feature_path": path_str,
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


__all__ = ["register_with_fastmcp"]
