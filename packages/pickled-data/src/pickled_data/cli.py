"""CLI for pickled-data."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click
import yaml
from pickled_core import Verdict
from pickled_core.llm import LLMClient

from pickled_data.drafter import MigrationDrafter
from pickled_data.gates import MigrationDriftGate
from pickled_data.oracle import apply_migration
from pickled_data.parser import ast_summary, load_sql_file
from pickled_data.types import DBT_NOT_IMPLEMENTED_MSG


def _build_llm_client() -> LLMClient:
    from pickled_core.llm.bootstrap import build_default_client
    from pickled_core.llm.config import ConfigError

    try:
        return build_default_client(factory_env="PICKLED_DATA_LLM_FACTORY")
    except ConfigError as exc:
        raise click.ClickException(str(exc)) from exc


def _read_text_arg(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def _emit_draft_output(
    *,
    text: str,
    rationale: str,
    warnings: tuple[str, ...],
    output: Path | None,
) -> None:
    if output is not None:
        output.write_text(text, encoding="utf-8")
    else:
        click.echo(text)
    if rationale:
        for line in rationale.splitlines():
            click.echo(f"rationale: {line}", err=True)
    for warning in warnings:
        click.echo(f"warning: {warning}", err=True)
    if warnings:
        raise SystemExit(1)


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


@main.command("draft")
@click.option("--intent", required=True, help="Intent file path or '-' for stdin.")
@click.option(
    "--dialect",
    required=True,
    type=click.Choice(["sqlite", "postgres", "mysql"], case_sensitive=False),
    help="SQL dialect for the migration.",
)
@click.option(
    "--current-schema",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=None,
    help="Optional existing schema YAML file.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(dir_okay=False, path_type=Path),
    default=None,
    help="Write SQL to this path. Default: stdout.",
)
def draft(
    intent: str,
    dialect: str,
    current_schema: Path | None,
    output: Path | None,
) -> None:
    """Draft a SQL migration from a natural-language intent."""
    schema_yaml: str | None = None
    if current_schema is not None:
        schema_yaml = current_schema.read_text(encoding="utf-8")
    try:
        llm = _build_llm_client()
        result = MigrationDrafter(llm).draft_from_intent(
            intent_text=_read_text_arg(intent),
            dialect=dialect,
            current_schema_yaml=schema_yaml,
        )
    except click.ClickException:
        raise
    except Exception as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(2) from exc
    _emit_draft_output(
        text=result.text,
        rationale=result.rationale,
        warnings=result.warnings,
        output=output,
    )


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
