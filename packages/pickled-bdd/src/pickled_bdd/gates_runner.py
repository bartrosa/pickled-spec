"""Workspace gate runner for ``pickled-spec check-all``."""

from __future__ import annotations

from pathlib import Path

from pickled_core import GateResult, Verdict

from pickled_bdd.adapters.pytest_bdd import PytestBddAdapter


def run_all(workdir: Path | str) -> list[GateResult]:
    """Parse Gherkin under ``features/`` (AmbiguityGate skipped without LLM)."""
    root = Path(workdir).resolve()
    features = sorted(root.glob("features/**/*.feature"))
    if not features:
        return [
            GateResult(
                gate_name="bdd.features",
                verdict=Verdict.PASS,
                notes="no features/ directory",
            )
        ]

    adapter = PytestBddAdapter()
    results: list[GateResult] = []
    for path in features:
        try:
            adapter.parse_feature_file(path)
        except Exception as exc:
            results.append(
                GateResult(
                    gate_name=f"bdd.parse.{path.name}",
                    verdict=Verdict.FAIL,
                    notes=str(exc),
                )
            )
        else:
            results.append(
                GateResult(
                    gate_name=f"bdd.parse.{path.name}",
                    verdict=Verdict.PASS,
                    notes=f"parsed {path.relative_to(root)}",
                )
            )

    results.append(
        GateResult(
            gate_name="bdd.ambiguity",
            verdict=Verdict.PASS,
            notes="skipped — set PICKLED_BDD_LLM_FACTORY to enable AmbiguityGate",
        )
    )
    return results


__all__ = ["run_all"]
