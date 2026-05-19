from __future__ import annotations

import pytest
from pickled_data.parser import load_sql_file, parse_sql
from pickled_data.types import SQLParseError


def test_parse_create_table(migration_file) -> None:
    sql = migration_file.read_text(encoding="utf-8")
    ast = parse_sql(sql, dialect="postgres")
    assert "users" in ast.sql().lower()


def test_parse_syntax_error() -> None:
    with pytest.raises(SQLParseError):
        parse_sql("SELECT FROM", dialect="postgres")


def test_load_sql_file(migration_file) -> None:
    artifact = load_sql_file(migration_file)
    assert artifact.dialect == "postgres"
    assert artifact.ast is not None
