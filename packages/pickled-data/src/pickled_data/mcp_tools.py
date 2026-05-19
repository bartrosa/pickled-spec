"""MCP tool registration for pickled-data."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import yaml

if TYPE_CHECKING:
    from fastmcp import FastMCP

from pickled_data.gates import MigrationDriftGate
from pickled_data.oracle import apply_migration
from pickled_data.parser import ast_summary, parse_sql


def register_with_fastmcp(app: FastMCP) -> None:
    @app.tool(name="parse_sql_migration")
    def parse_sql_migration(*, sql: str, dialect: str = "postgres") -> dict[str, Any]:
        """Parse SQL and return AST summary."""
        ast = parse_sql(sql, dialect=dialect)
        return {"dialect": dialect, **ast_summary(ast)}

    @app.tool(name="apply_sql_to_sandbox")
    def apply_sql_to_sandbox(*, sql: str, dialect: str = "postgres") -> dict[str, Any]:
        """Apply SQL to in-memory SQLite and return schema."""
        return apply_migration(sql, dialect=dialect)

    @app.tool(name="check_migration_drift")
    def check_migration_drift(
        *,
        sql: str,
        expected_schema_yaml: str,
        dialect: str = "postgres",
    ) -> dict[str, Any]:
        """Compare migration result schema to expected YAML."""
        loaded = yaml.safe_load(expected_schema_yaml)
        if not isinstance(loaded, dict):
            return {
                "verdict": "fail",
                "notes": "expected_schema_yaml root must be a mapping",
                "findings": [],
            }
        result = MigrationDriftGate().run(
            sql,
            context={
                "expected_schema": loaded,
                "dialect": dialect,
            },
        )
        return {
            "verdict": result.verdict.value,
            "notes": result.notes,
            "findings": list(result.findings),
        }


__all__ = ["register_with_fastmcp"]
