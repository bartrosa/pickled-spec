"""In-memory SQLite sandbox for migration application."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import sqlglot

from pickled_data.parser import parse_sql


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
        for statement in sqlite_sqls:
            conn.execute(statement)
        conn.commit()
        return _introspect(conn)
    finally:
        conn.close()


__all__ = ["apply_migration"]
