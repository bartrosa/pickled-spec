"""Workspace gate runner for ``pickled-spec check-all``."""

from __future__ import annotations

from pathlib import Path

import yaml
from pickled_bdd.adapters.pytest_bdd import PytestBddAdapter
from pickled_core import GateResult, Verdict

from pickled_rules.gates import coverage_gate_features
from pickled_rules.loader import RuleSetValidationError, load_ruleset


def _workdir_config(root: Path) -> dict:
    cfg_path = root / "pickled.ruleset.yaml"
    if not cfg_path.is_file():
        return {}
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def run_all(workdir: Path | str) -> list[GateResult]:
    """Run coverage gate for each feature against ``pickled.ruleset.yaml``."""
    root = Path(workdir).resolve()
    cfg = _workdir_config(root)
    ruleset_rel = cfg.get("ruleset")
    if not isinstance(ruleset_rel, str):
        return [
            GateResult(
                gate_name="rules.coverage",
                verdict=Verdict.WARN,
                notes="missing pickled.ruleset.yaml or ruleset key",
            )
        ]
    ruleset_path = (root / ruleset_rel).resolve()
    if not ruleset_path.is_file():
        return [
            GateResult(
                gate_name="rules.coverage",
                verdict=Verdict.FAIL,
                notes=f"ruleset not found: {ruleset_path}",
            )
        ]

    short_name = str(cfg.get("ruleset_short_name", ruleset_path.stem))
    try:
        ruleset = load_ruleset(ruleset_path)
    except RuleSetValidationError as exc:
        return [
            GateResult(
                gate_name="rules.load",
                verdict=Verdict.FAIL,
                notes=str(exc),
            )
        ]

    features = sorted(root.glob("features/**/*.feature"))
    if not features:
        return [
            GateResult(
                gate_name="rules.coverage",
                verdict=Verdict.WARN,
                notes="no feature files",
            )
        ]

    adapter = PytestBddAdapter()
    parsed = [adapter.parse_feature_file(path) for path in features]
    report = coverage_gate_features(parsed, ruleset, ruleset_short_name=short_name)
    gr = report.gate_result
    return [
        GateResult(
            gate_name="rules.coverage",
            verdict=gr.verdict,
            findings=gr.findings,
            notes=gr.notes,
            traces=gr.traces,
        )
    ]


__all__ = ["run_all"]
