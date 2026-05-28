"""Stage 5: run coverage and ambiguity gates over generated features."""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pickled_bdd.adapters.pytest_bdd import PytestBddAdapter
from pickled_rules.gates.coverage import coverage_gate_features

from pickled_core import GateResult
from pickled_core.llm.base import LLMClient
from pickled_core.mine.io import (
    ensure_output_dir,
    require_features_dir,
    surface_matches,
    write_json,
)
from pickled_core.mine.types import (
    AmbiguityFeatureResult,
    CoverageRulesetResult,
    EvaluationResult,
    RulesetSources,
)


def _import_run_ambiguity_gate() -> (
    Callable[[str | Path, LLMClient | None], GateResult] | None
):
    try:
        from pickled_bdd.cli import run_ambiguity_gate

        return run_ambiguity_gate
    except ImportError:  # pragma: no cover
        return None


def _surface_id_from_feature(path: Path) -> str:
    return path.stem


def _package_hint_from_surface_id(surface_id: str) -> str:
    if "_" in surface_id:
        return surface_id.split("_", 1)[0]
    return surface_id


def _filter_feature_paths(
    feature_paths: list[Path],
    surfaces: tuple[str, ...],
) -> list[Path]:
    if not surfaces:
        return feature_paths
    filtered: list[Path] = []
    for path in feature_paths:
        surface_id = _surface_id_from_feature(path)
        package = _package_hint_from_surface_id(surface_id)
        if surface_matches(surface_id=surface_id, package=package, tokens=surfaces):
            filtered.append(path)
    return filtered


def run_evaluate(
    output_dir: Path,
    *,
    ruleset_sources: RulesetSources | None,
    llm: LLMClient | None,
    surfaces: tuple[str, ...] = (),
) -> EvaluationResult:
    """Run coverage and ambiguity gates over generated features."""
    paths = ensure_output_dir(output_dir)
    features_dir = require_features_dir(output_dir, needed_by="evaluate")
    feature_paths = _filter_feature_paths(
        sorted(features_dir.glob("*.feature")),
        surfaces,
    )
    if not feature_paths:
        msg = "no features match --surfaces filter"
        raise ValueError(msg)

    coverage_entries: list[CoverageRulesetResult]
    if ruleset_sources is None:
        sys.stderr.write("[WARN] evaluate: no rule sets configured; coverage skipped\n")
        coverage_entries = []
    else:
        adapter = PytestBddAdapter()
        parsed = []
        for path in feature_paths:
            try:
                parsed.append(adapter.parse_feature_file(path))
            except Exception as exc:
                sys.stderr.write(
                    f"[WARN] evaluate: skip unparseable feature {path.name}: "
                    f"{type(exc).__name__}: {exc}\n"
                )
        coverage_entries = []
        for ruleset_entry in ruleset_sources.rulesets:
            report = coverage_gate_features(
                parsed,
                ruleset_entry.ruleset,
                ruleset_short_name=ruleset_entry.short_name,
            )
            strict_unref = [
                r.id
                for r in report.unreferenced_rules
                if r.enforcement == "strict"
            ]
            coverage_entries.append(
                CoverageRulesetResult(
                    short_name=ruleset_entry.short_name,
                    verdict=report.gate_result.verdict.value,
                    notes=report.gate_result.notes or "",
                    referenced_rule_ids=sorted(r.id for r in report.referenced_rules),
                    unreferenced_strict_rule_ids=sorted(strict_unref),
                    unknown_references=[
                        {"ruleset": rs, "rule_id": rid}
                        for rs, rid in report.unknown_references
                    ],
                )
            )

    ambiguity_runner = _import_run_ambiguity_gate()
    if ambiguity_runner is None:
        msg = "pickled-bdd is not installed; install pickled-core[mine]"
        raise RuntimeError(msg)

    ambiguity_entries: list[AmbiguityFeatureResult] = []
    for path in feature_paths:
        try:
            result = ambiguity_runner(path, llm)
        except Exception as exc:
            sys.stderr.write(
                f"[WARN] evaluate: ambiguity skipped for {path.name}: "
                f"{type(exc).__name__}: {exc}\n"
            )
            ambiguity_entries.append(
                AmbiguityFeatureResult(
                    feature_path=str(path.relative_to(paths.root)),
                    verdict="error",
                    finding_count=0,
                    skipped=True,
                    notes=f"unparseable feature: {exc}",
                )
            )
            continue
        skipped = llm is None
        ambiguity_entries.append(
            AmbiguityFeatureResult(
                feature_path=str(path.relative_to(paths.root)),
                verdict=result.verdict.value,
                finding_count=len(result.findings),
                skipped=skipped,
                notes=result.notes or "",
            )
        )

    coverage_doc: dict[str, Any] = {"schema_version": "1", "rulesets": []}
    for cov in coverage_entries:
        coverage_doc["rulesets"].append(
            {
                "short_name": cov.short_name,
                "verdict": cov.verdict,
                "notes": cov.notes,
                "referenced_rule_ids": cov.referenced_rule_ids,
                "unreferenced_strict_rule_ids": cov.unreferenced_strict_rule_ids,
                "unknown_references": cov.unknown_references,
            }
        )

    ambiguity_doc: dict[str, Any] = {"schema_version": "1", "features": []}
    for amb in ambiguity_entries:
        ambiguity_doc["features"].append(
            {
                "feature": amb.feature_path,
                "verdict": amb.verdict,
                "finding_count": amb.finding_count,
                "skipped": amb.skipped,
                "notes": amb.notes,
            }
        )

    write_json(paths.coverage_json, coverage_doc)
    write_json(paths.ambiguity_json, ambiguity_doc)

    return EvaluationResult(
        coverage_path=paths.coverage_json,
        ambiguity_path=paths.ambiguity_json,
        coverage=coverage_entries,
        ambiguity=ambiguity_entries,
        surfaces_filter=surfaces,
    )


__all__ = ["run_evaluate"]
