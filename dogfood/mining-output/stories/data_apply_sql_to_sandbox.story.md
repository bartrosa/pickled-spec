# Story: data_apply_sql_to_sandbox

## Metadata

- **Surface kind:** mcp_tool
- **Package:** pickled-data
- **Surface id:** data_apply_sql_to_sandbox

## Context

This surface is an MCP tool in the pickled-data package that allows users to execute SQL statements against an in-memory SQLite database sandbox and receive back the resulting schema. It is used by callers who need to validate SQL queries, explore database structure changes, or test SQL transformations in isolation without affecting persistent data stores. The tool accepts SQL commands and optionally a dialect parameter, then returns schema information describing the resulting database state.

## What the target does today

Apply SQL to in-memory SQLite and return schema.

The surface accepts SQL statements via the `sql` parameter (required) and executes them against an ephemeral SQLite database instance. An optional `dialect` parameter may be provided to influence SQL interpretation or formatting. After applying the SQL, the tool returns schema information describing the database structure that resulted from the SQL execution.

## What we want to verify

- Executing valid CREATE TABLE SQL returns schema information describing the created table
- Executing multiple SQL statements (e.g., CREATE TABLE followed by ALTER TABLE) returns the final schema state
- The returned schema includes table names present after SQL execution
- The returned schema includes column definitions for created tables
- Providing invalid SQL produces an error response rather than schema output
- Executing SQL that creates no tables returns an empty or minimal schema representation
- The in-memory database is isolated and does not persist between invocations
- The optional `dialect` parameter, when provided, is accepted without error
- Executing DROP TABLE SQL removes the table from the returned schema
- The schema output format is consistent and parseable across different SQL inputs

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
