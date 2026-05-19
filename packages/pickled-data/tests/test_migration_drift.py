"""MigrationDriftGate comparison behaviour."""

from __future__ import annotations

from pickled_core import Verdict
from pickled_data.gates import MigrationDriftGate, _compare_schemas, _normalize_columns


def test_compare_schemas_ignores_nullable_only_drift() -> None:
    expected = {
        "users": {
            ("email", "TEXT", True),
            ("name", "TEXT", False),
        }
    }
    actual = {
        "users": {
            ("email", "TEXT", False),
            ("name", "TEXT", False),
        }
    }
    ok, notes = _compare_schemas(expected, actual)
    assert ok is True
    assert "nullable differs" in notes


def test_compare_schemas_fails_on_missing_column() -> None:
    expected = {"t": {("a", "TEXT", True)}}
    actual: dict[str, set[tuple[str, str, bool]]] = {"t": set()}
    ok, _ = _compare_schemas(expected, actual)
    assert ok is False


def test_migration_drift_gate_passes_with_nullable_mismatch() -> None:
    gate = MigrationDriftGate()
    sql = "CREATE TABLE t (id TEXT PRIMARY KEY, x TEXT NOT NULL DEFAULT 'a');"
    expected = {
        "tables": [
            {
                "name": "t",
                "columns": [
                    {"name": "id", "type": "TEXT", "nullable": True},
                    {"name": "x", "type": "TEXT", "nullable": True},
                ],
            }
        ]
    }
    result = gate.run(sql, context={"expected_schema": expected, "dialect": "sqlite"})
    assert result.verdict is Verdict.PASS
    assert "nullable differs" in result.notes or "matches" in result.notes


def test_normalize_columns_from_yaml_shape() -> None:
    schema = {
        "tables": [
            {"name": "u", "columns": [{"name": "id", "type": "text", "nullable": False}]}
        ]
    }
    out = _normalize_columns(schema)
    assert out["u"] == {("id", "TEXT", False)}
