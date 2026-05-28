# Story: data_draft_sql_migration_from_intent

## Metadata

- **Surface kind:** mcp_tool
- **Package:** pickled-data
- **Surface id:** data_draft_sql_migration_from_intent

## Context

This tool is used by developers or automated workflows within the pickled-data package to generate SQL migration scripts from natural language intent descriptions. Callers provide a description of desired schema changes along with the target SQL dialect, and optionally the current schema state in YAML format. This surface bridges human intent with executable database migrations, typically invoked when evolving data contracts or schemas based on requirements expressed in plain text rather than directly writing SQL DDL.

## What the target does today

The inventory provides no docstring for this surface; behavior must be confirmed from source before specifying.

## What we want to verify

- Tool accepts `intent_text` parameter containing natural language description of schema changes
- Tool accepts `dialect` parameter specifying target SQL dialect (e.g., PostgreSQL, MySQL, SQLite)
- Tool accepts optional `current_schema_yaml` parameter containing existing schema definition
- Tool returns valid SQL migration statements appropriate for the specified dialect
- When `current_schema_yaml` is provided, generated migration reflects transition from current to intended state
- When `current_schema_yaml` is omitted, tool behavior regarding baseline assumptions must be verified from implementation
- Tool execution triggers or respects DataContractGate.run validation
- Tool execution triggers or respects MigrationDriftGate.run checks
- Generated SQL is syntactically valid for the specified dialect
- Tool handles ambiguous or conflicting intent descriptions (error or best-effort behavior to be confirmed)

## Inventory references

- Arguments:
- `intent_text` (required): 
- `dialect` (required): 
- `current_schema_yaml` (optional): 
- Related gates: DataContractGate.run, MigrationDriftGate.run, run_all
- Related ADRs:
- (none directly relevant)

## Open questions

(none)

## Status

draft
