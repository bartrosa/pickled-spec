# Story: data_parse_sql_migration

## Metadata

- **Surface kind:** mcp_tool
- **Package:** pickled-data
- **Surface id:** data_parse_sql_migration

## Context

This tool is used by data engineers and migration authors who need to parse SQL migration files and extract structural information about the schema changes. It supports the migration drift detection workflow by converting SQL text into a structured AST (Abstract Syntax Tree) that can be analyzed programmatically. Related gates like MigrationDriftGate.run likely consume this parsed output to detect drift between expected and actual migration state.

## What the target does today

Parse SQL and return AST summary.

The tool accepts SQL text as input and an optional dialect parameter. It parses the SQL into an abstract syntax tree representation and returns a summary of that structure, enabling programmatic analysis of schema migration commands.

## What we want to verify

- Accepts a required `sql` parameter containing SQL text
- Accepts an optional `dialect` parameter to specify SQL dialect for parsing
- Returns an AST summary structure representing the parsed SQL
- Successfully parses valid SQL migration statements (CREATE TABLE, ALTER TABLE, etc.)
- Handles SQL syntax appropriate to the specified dialect when provided
- Returns structured output that can be consumed by drift detection gates
- Handles empty or whitespace-only SQL input gracefully
- Reports parse errors for malformed SQL syntax

## Inventory references

- Arguments:
- `sql` (required): 
- `dialect` (optional): 
- Related gates: DataContractGate.run, MigrationDriftGate.run, run_all
- Related ADRs:
- (none directly relevant)

## Open questions

(none)

## Status

draft
