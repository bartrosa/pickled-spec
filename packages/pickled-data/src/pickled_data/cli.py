"""CLI for pickled-data."""

from __future__ import annotations

import json
from pathlib import Path

import click
import yaml
from pickled_core import Verdict

from pickled_data.gates import MigrationDriftGate
from pickled_data.oracle import apply_migration
from pickled_data.parser import ast_summary, load_sql_file
from pickled_data.types import DBT_NOT_IMPLEMENTED_MSG


def _check_dbt(path: Path) -> None:
    if path.suffix == ".dbt":
        raise NotImplementedError(DBT_NOT_IMPLEMENTED_MSG)


@click.group()
@click.version_option(package_name="pickled-data")
def main() -> None:
    """pickled-data — SQL migration parsing and drift checks."""


@main.command()
@click.argument("migration", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--dialect", default="postgres", show_default=True)
def parse(migration: Path, dialect: str) -> None:
    """Parse a migration SQL file and print AST summary."""
    _check_dbt(migration)
    artifact = load_sql_file(migration, dialect=dialect)
    summary = ast_summary(artifact.ast)
    click.echo(json.dumps({"dialect": artifact.dialect, **summary}, indent=2))


@main.command()
@click.argument("migration", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--dialect", default="postgres", show_default=True)
def apply(migration: Path, dialect: str) -> None:
    """Apply migration to in-memory SQLite and print resulting schema."""
    _check_dbt(migration)
    sql = migration.read_text(encoding="utf-8")
    schema = apply_migration(sql, dialect=dialect)
    click.echo(json.dumps(schema, indent=2))


@main.command("check-drift")
@click.option("--migration", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--expected", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--dialect", default="postgres", show_default=True)
def check_drift(migration: Path, expected: Path, dialect: str) -> None:
    """Run MigrationDriftGate against expected schema YAML."""
    _check_dbt(migration)
    sql = migration.read_text(encoding="utf-8")
    expected_schema = yaml.safe_load(expected.read_text(encoding="utf-8"))
    if not isinstance(expected_schema, dict):
        raise click.ClickException("expected schema YAML root must be a mapping")
    result = MigrationDriftGate().run(
        sql,
        context={"expected_schema": expected_schema, "dialect": dialect},
    )
    click.echo(
        json.dumps(
            {"verdict": result.verdict.value, "notes": result.notes},
            indent=2,
        )
    )
    if result.verdict is Verdict.FAIL:
        raise SystemExit(2)


@main.group()
def mcp() -> None:
    """MCP server commands."""


@mcp.command("serve")
@click.option("--transport", type=click.Choice(["stdio", "http"]), default="stdio")
@click.option("--host", default=None)
@click.option("--port", type=int, default=None)
@click.option("--allow-public", is_flag=True, default=False)
def mcp_serve(
    transport: str,
    host: str | None,
    port: int | None,
    allow_public: bool,
) -> None:
    from pickled_data.mcp_cli import cli as mcp_cli_main

    mcp_cli_main.main(
        args=[
            "--transport",
            transport,
            *(["--host", host] if host else []),
            *(["--port", str(port)] if port is not None else []),
            *(["--allow-public"] if allow_public else []),
        ],
        standalone_mode=False,
    )


__all__ = ["main"]
