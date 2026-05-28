# Story: data_check_migration_drift

## Metadata

- **Surface kind:** mcp_tool
- **Package:** pickled-data
- **Surface id:** data_check_migration_drift

## Context

This tool is used by teams that want to validate that a SQL migration script produces a database schema that matches an expected schema definition written in YAML. It is likely invoked during CI/CD pipelines or local development workflows to catch schema drift before migrations are applied to production databases. The caller provides the SQL migration script, the expected schema in YAML format, and optionally a SQL dialect to ensure the migration produces the correct schema structure.

## What the target does today

The tool compares the schema resulting from a migration script against an expected schema defined in YAML format. It accepts a required `sql` parameter containing the migration SQL, a required `expected_schema_yaml` parameter with the schema specification, and an optional `dialect` parameter to specify the SQL dialect for execution or parsing.

## What we want to verify

- Accept a `sql` parameter containing migration SQL script
- Accept an `expected_schema_yaml` parameter containing the expected schema definition
- Accept an optional `dialect` parameter for SQL dialect specification
- Perform comparison between the migration result schema and the expected YAML schema
- Report whether the migration result matches the expected schema or indicate drift
- Return results that can be consumed by the caller to determine migration validity

## Inventory references

- Arguments:
- `sql` (required): 
- `expected_schema_yaml` (required): 
- `dialect` (optional): 
- Related gates: DataContractGate.run, MigrationDriftGate.run, run_all
- Related ADRs:
- ADR 0007: Code-aware stories and docstring drift detection — Accepted

## Open questions

(none)

## Status

draft
