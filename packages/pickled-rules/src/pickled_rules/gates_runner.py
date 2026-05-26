"""Workspace gate runner for ``pickled-spec check-all``."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from pickled_bdd.adapters.pytest_bdd import PytestBddAdapter
from pickled_core import GateResult, Verdict

from pickled_rules.gates import coverage_gate_features
from pickled_rules.loader import RuleSetValidationError, load_ruleset


@dataclass(frozen=True, slots=True)
class _RulesetEntry:
    path: Path
    short_name: str


def _workdir_config(root: Path) -> dict[str, Any]:
    cfg_path = root / "pickled.ruleset.yaml"
    if not cfg_path.is_file():
        return {}
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _resolve_ruleset_entries(root: Path, cfg: dict[str, Any]) -> list[_RulesetEntry]:
    has_singular = "ruleset" in cfg
    has_plural = "rulesets" in cfg
    if has_singular and has_plural:
        msg = (
            "pickled.ruleset.yaml: keys 'ruleset' and 'rulesets' are mutually exclusive"
        )
        raise RuleSetValidationError(msg)

    if has_singular:
        ruleset_rel = cfg.get("ruleset")
        if not isinstance(ruleset_rel, str):
            msg = "pickled.ruleset.yaml: 'ruleset' must be a string path"
            raise RuleSetValidationError(msg)
        path = (root / ruleset_rel).resolve()
        short_name = str(cfg.get("ruleset_short_name", path.stem))
        return [_RulesetEntry(path=path, short_name=short_name)]

    if has_plural:
        raw_list = cfg.get("rulesets")
        if not isinstance(raw_list, list):
            msg = "pickled.ruleset.yaml: 'rulesets' must be a list"
            raise RuleSetValidationError(msg)
        if not raw_list:
            msg = "pickled.ruleset.yaml: at least one ruleset entry required"
            raise RuleSetValidationError(msg)

        entries: list[_RulesetEntry] = []
        seen_short_names: dict[str, int] = {}
        for index, item in enumerate(raw_list):
            if not isinstance(item, dict):
                msg = f"pickled.ruleset.yaml: rulesets[{index}] must be a mapping"
                raise RuleSetValidationError(msg)
            path_raw = item.get("path")
            if not isinstance(path_raw, str):
                msg = f"pickled.ruleset.yaml: rulesets[{index}].path must be a string"
                raise RuleSetValidationError(msg)
            short_raw = item.get("short_name")
            if short_raw is not None and not isinstance(short_raw, str):
                msg = (
                    f"pickled.ruleset.yaml: rulesets[{index}].short_name must be a string"
                )
                raise RuleSetValidationError(msg)
            resolved = (root / path_raw).resolve()
            short_name = str(short_raw) if short_raw is not None else Path(path_raw).stem
            if short_name in seen_short_names:
                prior = seen_short_names[short_name]
                msg = (
                    f"duplicate short_name {short_name!r} at positions "
                    f"[{prior}, {index}]"
                )
                raise RuleSetValidationError(msg)
            seen_short_names[short_name] = index
            entries.append(_RulesetEntry(path=resolved, short_name=short_name))
        return entries

    return []


def run_all(workdir: Path | str) -> list[GateResult]:
    """Run coverage gate for each feature against ``pickled.ruleset.yaml``."""
    root = Path(workdir).resolve()
    cfg = _workdir_config(root)
    try:
        entries = _resolve_ruleset_entries(root, cfg)
    except RuleSetValidationError as exc:
        return [
            GateResult(
                gate_name="rules.coverage",
                verdict=Verdict.FAIL,
                notes=str(exc),
            )
        ]

    if not entries:
        return [
            GateResult(
                gate_name="rules.coverage",
                verdict=Verdict.WARN,
                notes="missing pickled.ruleset.yaml or ruleset/rulesets key",
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

    results: list[GateResult] = []
    for entry in entries:
        gate_name = (
            "rules.coverage"
            if len(entries) == 1
            else f"rules.coverage.{entry.short_name}"
        )
        if not entry.path.is_file():
            results.append(
                GateResult(
                    gate_name=gate_name,
                    verdict=Verdict.FAIL,
                    notes=f"ruleset not found: {entry.path}",
                )
            )
            continue
        try:
            ruleset = load_ruleset(entry.path)
        except RuleSetValidationError as exc:
            results.append(
                GateResult(
                    gate_name=f"rules.load.{entry.short_name}",
                    verdict=Verdict.FAIL,
                    notes=str(exc),
                )
            )
            continue
        report = coverage_gate_features(
            parsed, ruleset, ruleset_short_name=entry.short_name
        )
        gr = report.gate_result
        results.append(
            GateResult(
                gate_name=gate_name,
                verdict=gr.verdict,
                findings=gr.findings,
                notes=gr.notes,
                traces=gr.traces,
            )
        )
    return results


__all__ = ["run_all"]
