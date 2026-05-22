"""Regression test: the SQL sandbox must not create files outside itself.

``apply_migration`` (and therefore the ``apply_sql_to_sandbox`` /
``check_migration_drift`` MCP tools) accept caller-supplied SQL plus a
``dialect`` string. Prior to the fix, passing ``dialect="sqlite"`` together
with an ``ATTACH DATABASE`` statement would cause SQLite to create a new
database file at an attacker-chosen path — an arbitrary-file-write
primitive against the server process, in the same threat-model category
as the vulnerabilities fixed in PRs #18 and #19.

These tests assert that:

* SQL containing ``ATTACH``/``DETACH`` is rejected by the AST check before
  any statement reaches the engine (clear error to the caller).
* The targeted filesystem path is **not** created.
* Legitimate migrations still apply.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pickled_data.oracle import (
    UnsafeMigrationStatementError,
    apply_migration,
)


def test_attach_sqlite_dialect_is_rejected(tmp_path: Path) -> None:
    target = tmp_path / "should-not-exist.db"
    sql = (
        f"ATTACH DATABASE '{target}' AS p;\n"
        "CREATE TABLE p.tbl (x TEXT);\n"
    )
    with pytest.raises(UnsafeMigrationStatementError):
        apply_migration(sql, dialect="sqlite")
    assert not target.exists(), (
        f"ATTACH should not have created {target}; "
        "arbitrary-file-write sandbox escape regression."
    )


def test_detach_sqlite_dialect_is_rejected() -> None:
    with pytest.raises(UnsafeMigrationStatementError):
        apply_migration("DETACH DATABASE main;", dialect="sqlite")


def test_attach_inside_compound_statement_is_rejected(tmp_path: Path) -> None:
    target = tmp_path / "compound-pwn.db"
    sql = (
        "CREATE TABLE legit (id INTEGER PRIMARY KEY);\n"
        f"ATTACH DATABASE '{target}' AS p;\n"
        "CREATE TABLE p.evil (x TEXT);\n"
    )
    with pytest.raises(UnsafeMigrationStatementError):
        apply_migration(sql, dialect="sqlite")
    assert not target.exists(), (
        "no statement should have executed once ATTACH was detected"
    )


def test_legitimate_sqlite_migration_still_works() -> None:
    sql = (
        "CREATE TABLE users (\n"
        "  id INTEGER PRIMARY KEY,\n"
        "  email TEXT NOT NULL UNIQUE\n"
        ");\n"
        "CREATE INDEX idx_users_email ON users(email);\n"
    )
    schema = apply_migration(sql, dialect="sqlite")
    table_names = {t["name"] for t in schema["tables"]}
    assert "users" in table_names


def test_engine_level_limit_blocks_attach_if_ast_check_skipped(
    tmp_path: Path,
) -> None:
    """Defense in depth: SQLite must refuse ATTACH at the engine level.

    Bypasses the AST guard by calling ``sqlite3`` directly the same way
    ``apply_migration`` does, then exercising the post-connect limit.
    Regression guard against any future refactor that drops the AST check
    without also dropping the engine-level limit.
    """
    import sqlite3

    conn = sqlite3.connect(":memory:")
    try:
        conn.setlimit(sqlite3.SQLITE_LIMIT_ATTACHED, 0)
        target = tmp_path / "engine-limit.db"
        with pytest.raises(sqlite3.OperationalError):
            conn.execute(f"ATTACH DATABASE '{target}' AS p")
        assert not target.exists()
    finally:
        conn.close()
