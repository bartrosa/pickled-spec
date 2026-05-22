"""In-memory SQLite sandbox for migration application.

The sandbox is reachable from untrusted callers via the
``apply_sql_to_sandbox`` and ``check_migration_drift`` MCP tools (per the
threat model documented in PR #18 / #19: any pickled-* MCP client should
be assumed hostile). SQL goes through sqlglot, which transpiles to the
SQLite dialect for execution. SQLite's ``ATTACH DATABASE`` statement
creates a new database file at an attacker-chosen path, giving any MCP
client an arbitrary-file-write primitive against the server process
(e.g. planting files in world-readable directories or filling disk).
We defend in two layers:

1. Reject parsed SQL that contains ``Attach`` or ``Detach`` nodes
   before any statement is executed — this gives callers a clear error.
2. Set ``SQLITE_LIMIT_ATTACHED = 0`` on the connection so even if the
   first layer were bypassed (e.g. by a transpilation quirk), the SQLite
   engine refuses to attach any database.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import sqlglot
from sqlglot import expressions as exp

from pickled_data.parser import parse_sql


class UnsafeMigrationStatementError(ValueError):
    """Raised when migration SQL contains statements that escape the sandbox.

    Currently triggered by ``ATTACH DATABASE`` / ``DETACH DATABASE``: those
    operate on filesystem paths and would let an MCP client create or
    interact with database files outside the in-memory sandbox.
    """


def _reject_filesystem_escapes(statements: list[exp.Expression | None]) -> None:
    """Refuse ATTACH/DETACH statements before any SQL is executed."""
    for stmt in statements:
        if stmt is None:
            continue
        if isinstance(stmt, exp.Attach | exp.Detach):
            raise UnsafeMigrationStatementError(
                f"ATTACH/DETACH statements are not allowed in the sandbox: "
                f"{stmt.sql(dialect='sqlite')!r}"
            )
        for node in stmt.find_all(exp.Attach, exp.Detach):
            raise UnsafeMigrationStatementError(
                f"ATTACH/DETACH statements are not allowed in the sandbox: "
                f"{node.sql(dialect='sqlite')!r}"
            )


def _introspect(conn: sqlite3.Connection) -> dict[str, Any]:
    tables: list[dict[str, Any]] = []
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    for (name,) in cur.fetchall():
        cols: list[dict[str, Any]] = []
        info = conn.execute(f"PRAGMA table_info({name})").fetchall()
        for _cid, col_name, col_type, notnull, _default, _pk in info:
            cols.append(
                {
                    "name": col_name,
                    "type": (col_type or "TEXT").upper(),
                    "nullable": not bool(notnull),
                }
            )
        tables.append({"name": name, "columns": cols})
    return {"tables": tables}


def apply_migration(
    sql: str,
    target_db: Path | None = None,
    *,
    dialect: str = "postgres",
) -> dict[str, Any]:
    """Apply DDL/DML and return resulting schema summary."""
    parse_sql(sql, dialect=dialect)
    statements = sqlglot.parse(sql, dialect=dialect)
    _reject_filesystem_escapes(statements)
    sqlite_sqls: list[str] = []
    for stmt in statements:
        if stmt is None:
            continue
        transpiled = stmt.sql(dialect="sqlite")
        if transpiled.strip():
            sqlite_sqls.append(transpiled)

    conn = (
        sqlite3.connect(str(target_db))
        if target_db is not None
        else sqlite3.connect(":memory:")
    )

    try:
        # Defense in depth: even if a future transpilation quirk reintroduces
        # an ATTACH statement past the AST check, SQLite refuses to attach
        # anything when SQLITE_LIMIT_ATTACHED == 0.
        try:
            conn.setlimit(sqlite3.SQLITE_LIMIT_ATTACHED, 0)
        except AttributeError:  # pragma: no cover — only Python <3.11
            pass
        for statement in sqlite_sqls:
            conn.execute(statement)
        conn.commit()
        return _introspect(conn)
    finally:
        conn.close()


__all__ = ["UnsafeMigrationStatementError", "apply_migration"]
