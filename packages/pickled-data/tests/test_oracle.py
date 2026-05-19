from __future__ import annotations

import yaml
from pickled_data.oracle import apply_migration


def test_apply_migration_schema(migration_file) -> None:
    sql = migration_file.read_text(encoding="utf-8")
    schema = apply_migration(sql, dialect="postgres")
    names = {t["name"] for t in schema["tables"]}
    assert "users" in names
    users = next(t for t in schema["tables"] if t["name"] == "users")
    col_names = {c["name"] for c in users["columns"]}
    assert {"id", "email", "name", "deleted_at"} <= col_names


def test_apply_matches_expected_yaml(migration_file, expected_users_schema) -> None:
    sql = migration_file.read_text(encoding="utf-8")
    actual = apply_migration(sql, dialect="postgres")
    expected = yaml.safe_load(expected_users_schema.read_text(encoding="utf-8"))
    from pickled_data.gates import _normalize_columns

    assert _normalize_columns(expected) == _normalize_columns(actual)
