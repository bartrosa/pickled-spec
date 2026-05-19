"""Workspace gate runner for ``pickled-spec check-all``."""

from __future__ import annotations

from pathlib import Path

import yaml
from pickled_core import GateResult, Verdict

from pickled_data.gates import MigrationDriftGate
from pickled_data.parser import load_sql_file
from pickled_data.types import SQLParseError


def run_all(workdir: Path | str) -> list[GateResult]:
    """Parse migrations and run drift gate vs ``expected_schema.yaml``."""
    root = Path(workdir).resolve()
    migrations = sorted(root.glob("migrations/*.sql"))
    expected_path = root / "expected_schema.yaml"

    if not migrations:
        return [
            GateResult(
                gate_name="data.migrations",
                verdict=Verdict.WARN,
                notes="no migrations/*.sql",
            )
        ]

    results: list[GateResult] = []
    dialect = "sqlite"
    for mig in migrations:
        try:
            load_sql_file(mig, dialect=dialect)
        except SQLParseError as exc:
            results.append(
                GateResult(
                    gate_name=f"data.parse.{mig.name}",
                    verdict=Verdict.FAIL,
                    notes=str(exc),
                )
            )
        else:
            results.append(
                GateResult(
                    gate_name=f"data.parse.{mig.name}",
                    verdict=Verdict.PASS,
                    notes="parsed",
                )
            )

    if len(migrations) > 1:
        results.append(
            GateResult(
                gate_name="data.migrations.note",
                verdict=Verdict.WARN,
                notes=f"applying {len(migrations)} migrations in filename order for drift",
            )
        )

    if expected_path.is_file() and migrations:
        combined_sql = "\n\n".join(
            mig.read_text(encoding="utf-8") for mig in migrations
        )
        expected = yaml.safe_load(expected_path.read_text(encoding="utf-8"))
        if isinstance(expected, dict):
            gr = MigrationDriftGate().run(
                combined_sql,
                context={"expected_schema": expected, "dialect": dialect},
            )
            results.append(
                GateResult(
                    gate_name="data.migration_drift",
                    verdict=gr.verdict,
                    notes=gr.notes,
                )
            )
    return results


__all__ = ["run_all"]
