"""Workspace gate runner for ``pickled-spec check-all``."""

from __future__ import annotations

from pathlib import Path

from pickled_core import GateResult, Verdict

from pickled_schema.gates import SchemaCoverageGate
from pickled_schema.openapi.parser import load_openapi_file
from pickled_schema.openapi.validator import validate_openapi_dict
from pickled_schema.types import SchemaValidationError


def run_all(workdir: Path | str) -> list[GateResult]:
    """Validate OpenAPI under ``specs/`` and run schema coverage on features."""
    root = Path(workdir).resolve()
    results: list[GateResult] = []

    spec_candidates = sorted(root.glob("specs/*.yaml")) + sorted(
        root.glob("specs/*.yml")
    )
    if not spec_candidates:
        results.append(
            GateResult(
                gate_name="schema.openapi",
                verdict=Verdict.WARN,
                notes="no specs/*.yaml",
            )
        )
        return results

    valid_specs: list[tuple[Path, dict]] = []
    for spec_path in spec_candidates:
        try:
            spec_dict, _, _ = load_openapi_file(spec_path)
            validate_openapi_dict(spec_dict)
        except (SchemaValidationError, OSError, ValueError, TypeError) as exc:
            results.append(
                GateResult(
                    gate_name=f"schema.openapi.validate.{spec_path.name}",
                    verdict=Verdict.FAIL,
                    notes=str(exc),
                )
            )
        else:
            valid_specs.append((spec_path, spec_dict))
            results.append(
                GateResult(
                    gate_name=f"schema.openapi.validate.{spec_path.name}",
                    verdict=Verdict.PASS,
                    notes=str(spec_path.relative_to(root)),
                )
            )

    if not valid_specs:
        return results

    if len(valid_specs) > 1:
        results.append(
            GateResult(
                gate_name="schema.openapi.note",
                verdict=Verdict.WARN,
                notes=(
                    f"{len(valid_specs)} OpenAPI files under specs/; "
                    f"coverage uses {valid_specs[0][0].name}"
                ),
            )
        )

    spec_path, spec_dict = valid_specs[0]
    feature_paths = sorted(root.glob("features/**/*.feature"))
    if feature_paths:
        gate = SchemaCoverageGate()
        gr = gate.run(spec_dict, context={"feature_paths": feature_paths})
        results.append(
            GateResult(
                gate_name="schema.coverage",
                verdict=gr.verdict,
                findings=gr.findings,
                notes=gr.notes or str(spec_path.relative_to(root)),
            )
        )
    return results


__all__ = ["run_all"]
