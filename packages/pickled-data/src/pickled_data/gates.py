"""Gates for pickled-data."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import yaml
from pickled_core import GateResult, Verdict
from sqlglot import expressions as exp

from pickled_data.oracle import apply_migration
from pickled_data.parser import parse_sql

if TYPE_CHECKING:
    from pickled_schema.api import SchemaRegistry


def _normalize_columns(schema: dict[str, Any]) -> dict[str, set[tuple[str, str, bool]]]:
    """Map table name -> set of (name, type, nullable)."""
    out: dict[str, set[tuple[str, str, bool]]] = {}
    for table in schema.get("tables", []):
        if not isinstance(table, dict):
            continue
        name = str(table.get("name", ""))
        cols: set[tuple[str, str, bool]] = set()
        for col in table.get("columns", []):
            if isinstance(col, dict):
                cols.add(
                    (
                        str(col.get("name", "")),
                        str(col.get("type", "TEXT")).upper(),
                        bool(col.get("nullable", True)),
                    )
                )
        out[name] = cols
    return out


def _column_keys(cols: set[tuple[str, str, bool]]) -> set[tuple[str, str]]:
    return {(name, col_type) for name, col_type, _nullable in cols}


def _compare_schemas(
    expected: dict[str, set[tuple[str, str, bool]]],
    actual: dict[str, set[tuple[str, str, bool]]],
) -> tuple[bool, str]:
    """Compare schemas; ignore nullable-only drift (e.g. SQLite DEFAULT → NOT NULL)."""
    if set(expected) != set(actual):
        return (
            False,
            f"drift: expected tables {sorted(expected)} vs actual {sorted(actual)}",
        )
    nullable_notes: list[str] = []
    for table in sorted(expected):
        exp_cols = expected[table]
        act_cols = actual[table]
        if _column_keys(exp_cols) != _column_keys(act_cols):
            return (
                False,
                f"drift: table {table!r} expected {_column_keys(exp_cols)} "
                f"vs actual {_column_keys(act_cols)}",
            )
        exp_null = {(n, t): nullable for n, t, nullable in exp_cols}
        act_null = {(n, t): nullable for n, t, nullable in act_cols}
        for key, exp_n in exp_null.items():
            act_n = act_null.get(key)
            if act_n is not None and exp_n != act_n:
                nullable_notes.append(f"{table}.{key[0]} expected nullable={exp_n} got {act_n}")
    if nullable_notes:
        detail = "; ".join(nullable_notes)
        return True, f"Schema matches expected (nullable differs: {detail})."
    return True, "Schema matches expected."


class MigrationDriftGate:
    """Compare oracle schema output vs expected schema YAML."""

    name = "data_migration_drift"

    def run(
        self,
        target: object,
        *,
        context: dict[str, Any] | None = None,
    ) -> GateResult:
        ctx = context or {}
        if not isinstance(target, str):
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes=f"Expected migration SQL string, got {type(target).__name__}",
            )
        expected = ctx.get("expected_schema")
        if not isinstance(expected, dict):
            raw = ctx.get("expected_schema_yaml")
            if isinstance(raw, str):
                loaded = yaml.safe_load(raw)
                expected = loaded if isinstance(loaded, dict) else None
        if not isinstance(expected, dict):
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes='context needs "expected_schema" or "expected_schema_yaml"',
            )
        dialect = str(ctx.get("dialect", "postgres"))
        actual = apply_migration(target, dialect=dialect)
        exp_tables = _normalize_columns(expected)
        act_tables = _normalize_columns(actual)
        ok, notes = _compare_schemas(exp_tables, act_tables)
        return GateResult(
            gate_name=self.name,
            verdict=Verdict.PASS if ok else Verdict.FAIL,
            notes=notes,
        )


class DataContractGate:
    """v0.1 PARTIAL: column name matching against OpenAPI response properties."""

    name = "data_contract"

    def __init__(self, schema_registry: SchemaRegistry | None = None) -> None:
        self._registry = schema_registry

    def run(
        self,
        target: object,
        *,
        context: dict[str, Any] | None = None,
    ) -> GateResult:
        ctx = context or {}
        if not isinstance(target, str):
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes=f"Expected SQL string, got {type(target).__name__}",
            )
        endpoint_tag = ctx.get("endpoint_tag")
        if not isinstance(endpoint_tag, str):
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes='context must contain "endpoint_tag"',
            )
        if self._registry is None:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.WARN,
                notes="no SchemaRegistry configured",
            )
        artifact = self._registry.find_schema_by_tag(endpoint_tag)
        if artifact is None:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.WARN,
                notes=f"no schema for tag {endpoint_tag!r}",
            )
        sql_columns = _select_column_names(target)
        api_columns = _openapi_response_property_names(artifact.content)
        if not api_columns:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.WARN,
                notes="could not extract OpenAPI response properties",
            )
        api_set = set(api_columns)
        sql_set = set(sql_columns)
        missing = sorted(sql_set - api_set)
        extra = sorted(api_set - sql_set)
        if missing or extra:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes=f"column mismatch missing={missing} extra={extra}",
            )
        return GateResult(
            gate_name=self.name,
            verdict=Verdict.PASS,
            notes="column names match OpenAPI properties (types not checked in v0.1)",
        )


def _select_column_names(sql: str) -> list[str]:
    """Extract output column names from a SELECT (best-effort)."""
    try:
        ast = parse_sql(sql, dialect="postgres")
    except Exception:
        return []
    cols: list[str] = []
    for node in ast.find_all(exp.Select):
        for expr in node.expressions:
            alias = getattr(expr, "alias", None)
            if alias:
                cols.append(str(alias))
            elif hasattr(expr, "name") and expr.name:
                cols.append(str(expr.name))
    return cols


def _openapi_response_property_names(spec_yaml: str) -> list[str]:
    import yaml

    try:
        spec = yaml.safe_load(spec_yaml)
    except yaml.YAMLError:
        return []
    if not isinstance(spec, dict):
        return []
    paths = spec.get("paths")
    if not isinstance(paths, dict):
        return []
    for _path, item in paths.items():
        if not isinstance(item, dict):
            continue
        for _method, op in item.items():
            if not isinstance(op, dict):
                continue
            responses = op.get("responses") or {}
            ok = responses.get("200") or responses.get("201")
            if not isinstance(ok, dict):
                continue
            content = ok.get("content") or {}
            app_json = content.get("application/json") or {}
            schema = app_json.get("schema") or {}
            props = schema.get("properties") or {}
            if isinstance(props, dict):
                return sorted(str(k) for k in props)
    return []


__all__ = ["DataContractGate", "MigrationDriftGate"]
