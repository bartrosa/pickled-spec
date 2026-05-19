"""Workspace gate runner for ``pickled-spec check-all``."""

from __future__ import annotations

from pathlib import Path

from pickled_core import GateResult, Verdict

from pickled_iac.gates import SecurityBaselineGate
from pickled_iac.oracle import validate
from pickled_iac.types import IaCToolMissingError


def run_all(workdir: Path | str) -> list[GateResult]:
    """``terraform validate`` and optional Trivy scan on ``infra/``."""
    root = Path(workdir).resolve()
    infra = root / "infra"
    if not infra.is_dir():
        return [
            GateResult(
                gate_name="iac.infra",
                verdict=Verdict.WARN,
                notes="no infra/ directory",
            )
        ]

    results: list[GateResult] = []
    try:
        vr = validate(infra)
    except IaCToolMissingError as exc:
        results.append(
            GateResult(
                gate_name="iac.validate",
                verdict=Verdict.WARN,
                notes=str(exc),
            )
        )
    except Exception as exc:
        results.append(
            GateResult(
                gate_name="iac.validate",
                verdict=Verdict.FAIL,
                notes=str(exc),
            )
        )
    else:
        results.append(
            GateResult(
                gate_name="iac.validate",
                verdict=Verdict.PASS if vr.valid else Verdict.FAIL,
                notes="; ".join(vr.diagnostics) or "ok",
            )
        )

    sec = SecurityBaselineGate().run(infra)
    results.append(
        GateResult(
            gate_name=sec.gate_name,
            verdict=sec.verdict,
            findings=sec.findings,
            notes=sec.notes,
        )
    )
    return results


__all__ = ["run_all"]
