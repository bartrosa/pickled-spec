from __future__ import annotations

import yaml
from pickled_core import Verdict
from pickled_data.gates import MigrationDriftGate


def test_drift_pass(migration_file, expected_users_schema) -> None:
    sql = migration_file.read_text(encoding="utf-8")
    expected = yaml.safe_load(expected_users_schema.read_text(encoding="utf-8"))
    result = MigrationDriftGate().run(
        sql,
        context={"expected_schema": expected, "dialect": "postgres"},
    )
    assert result.verdict is Verdict.PASS


def test_drift_fail(migration_file) -> None:
    sql = migration_file.read_text(encoding="utf-8")
    expected = {"tables": [{"name": "orders", "columns": []}]}
    result = MigrationDriftGate().run(
        sql,
        context={"expected_schema": expected, "dialect": "postgres"},
    )
    assert result.verdict is Verdict.FAIL
