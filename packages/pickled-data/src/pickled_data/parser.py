"""SQL parsing via sqlglot."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import sqlglot
from sqlglot import expressions as exp

from pickled_data.types import DBT_NOT_IMPLEMENTED_MSG, SQLArtifact, SQLParseError


def _reject_dbt(path: Path | None) -> None:
    if path is not None and path.suffix == ".dbt":
        raise NotImplementedError(DBT_NOT_IMPLEMENTED_MSG)


def parse_sql(sql: str, dialect: str = "postgres") -> exp.Expr:
    """Parse SQL into a sqlglot AST."""
    try:
        parsed = sqlglot.parse_one(sql, dialect=dialect)
    except sqlglot.errors.ParseError as exc:
        raise SQLParseError(str(exc)) from exc
    if parsed is None:
        msg = "empty parse result"
        raise SQLParseError(msg)
    return parsed


def load_sql_file(path: Path, dialect: str = "postgres") -> SQLArtifact:
    _reject_dbt(path)
    content = path.read_text(encoding="utf-8")
    ast = parse_sql(content, dialect=dialect)
    return SQLArtifact(content=content, dialect=dialect, ast=ast)


def ast_summary(ast: Any) -> dict[str, str]:
    """Short summary for CLI / MCP."""
    return {"kind": type(ast).__name__, "sql": ast.sql(dialect="postgres")}


__all__ = ["ast_summary", "load_sql_file", "parse_sql"]
