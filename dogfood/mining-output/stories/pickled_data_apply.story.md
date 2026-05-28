# Story: apply

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-data
- **Surface id:** pickled_data_apply
- **Code depth:** callgraph | **Units read:** 6 | **Unresolved:** 6

## Context

This CLI command is used by developers or automated tools to validate SQL migration files before applying them to a production database. It provides a safe sandbox environment (in-memory SQLite) to test whether a migration's DDL/DML statements will execute successfully and to preview the resulting database schema. The command accepts migration files written in various SQL dialects (e.g., PostgreSQL) and transpiles them to SQLite for validation. Related gates like `MigrationDriftGate.run` and `DataContractGate.run` likely consume this functionality to verify migrations as part of a validation pipeline.

## What the target does today

The command accepts two arguments: a file path to a migration script and a SQL dialect identifier (e.g., "postgres").

**Pre-execution validation:**
- Rejects files with a `.dbt` suffix, raising `NotImplementedError` with a message about dbt not being implemented
- Reads the migration file as UTF-8 text
- Parses the SQL using the specified dialect; raises `SQLParseError` if parsing fails or produces empty results
- Scans the parsed AST for `ATTACH` or `DETACH` statements (both top-level and nested); raises `UnsafeMigrationStatementError` if any are found, preventing filesystem access attempts

**Execution:**
- Transpiles all parsed SQL statements from the source dialect to SQLite dialect (delegated to unresolved `sqlglot.parse` and `stmt.sql` calls)
- Creates an in-memory SQLite database connection
- Attempts to set the SQLite attached database limit to 0 as defense-in-depth (catches `AttributeError` for Python <3.11 compatibility but does not fail)
- Executes each transpiled statement sequentially (delegated to unresolved `conn.execute`)
- Commits the transaction (delegated to unresolved `conn.commit`)
- Closes the connection regardless of success or failure

**Output:**
- On success, introspects the resulting schema and prints a JSON object to stdout with this structure:
  - `tables`: array of table objects, excluding SQLite system tables (names starting with `sqlite_`)
  - Each table object contains:
    - `name`: table name (string)
    - `columns`: array of column objects
  - Each column object contains:
    - `name`: column name (string)
    - `type`: column type uppercased (string), defaults to "TEXT" if null
    - `nullable`: boolean indicating whether the column accepts nulls
- JSON is formatted with 2-space indentation

**Error modes:**
- Raises `NotImplementedError` if the migration file has a `.dbt` extension
- Raises `SQLParseError` if SQL cannot be parsed or parsing produces no result
- Raises `UnsafeMigrationStatementError` if `ATTACH` or `DETACH` statements are detected
- Any errors during statement execution propagate from the unresolved `conn.execute` call
- File reading errors (missing file, encoding issues) propagate naturally

The command provides no return value (returns `None`) as it's a CLI endpoint that produces side effects (stdout output).

## What we want to verify

- Accepts a valid migration file path and dialect string, produces JSON output to stdout
- Rejects `.dbt` files with `NotImplementedError` before any SQL processing
- Rejects SQL containing top-level `ATTACH` statements with `UnsafeMigrationStatementError`
- Rejects SQL containing nested `ATTACH` or `DETACH` statements with `UnsafeMigrationStatementError`
- Raises `SQLParseError` when SQL cannot be parsed in the specified dialect
- Raises `SQLParseError` when SQL file is empty or produces no parse result
- Outputs JSON with `tables` array containing objects with `name` and `columns` fields
- Each column object in output contains `name`, `type`, and `nullable` fields
- Column types in output are uppercased
- Column types default to "TEXT" when database reports null type
- Output excludes SQLite system tables (names starting with `sqlite_`)
- JSON output is indented with 2 spaces
- Closes database connection even when statement execution fails
- Handles missing UTF-8 encoding in migration file by raising appropriate error
- Transpiles SQL from specified source dialect to SQLite dialect before execution
- Creates an in-memory SQLite database (not a file-based one)
- Attempts to set SQLite attached database limit to 0 (silently continues on AttributeError)
- Commits transaction after all statements execute successfully

## Inventory references

- Arguments:
- `migration` (required): 
- `dialect` (optional): 
- Related gates: DataContractGate.run, MigrationDriftGate.run, run_all
- Related ADRs:
- (none directly relevant)

## Open questions

- Docstring drift: Docstring claims "Apply migration to in-memory SQLite and print resulting schema" but omits several important behaviors: rejection of `.dbt` files, rejection of `ATTACH`/`DETACH` statements, SQL parsing and validation before execution, error conditions, and the specific JSON schema structure returned
- Docstring drift: Docstring does not mention the `dialect` parameter's purpose (transpilation from source dialect to SQLite)
- Docstring drift: Docstring does not indicate that the command performs security validation to prevent filesystem access attempts

## Status

draft
