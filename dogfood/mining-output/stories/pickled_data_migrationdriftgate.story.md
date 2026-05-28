# Story: MigrationDriftGate.run

## Metadata

- **Surface kind:** gate
- **Package:** pickled-data
- **Surface id:** pickled_data_migrationdriftgate
- **Code depth:** callgraph | **Units read:** 5 | **Unresolved:** 7

## Context

This gate is used by the pickled-data migration validation pipeline to verify that a SQL migration script produces the expected database schema. Callers provide a migration SQL string as the target, along with context containing either a parsed expected schema dictionary or a YAML string describing the expected schema. The gate compares the schema produced by applying the migration against the expected schema and reports whether they match.

## What the target does today

**Inputs:**
- `target`: Must be a string containing SQL migration statements. Any other type results in immediate failure.
- `context`: Optional dictionary that must contain schema expectations via one of:
  - `"expected_schema"`: A dictionary directly describing the expected schema
  - `"expected_schema_yaml"`: A YAML string that parses to a dictionary
  - `"dialect"`: Optional SQL dialect string (defaults to "postgres")

**Validation and rejection:**
- Rejects non-string targets with verdict FAIL and a note identifying the received type.
- Rejects contexts lacking both `"expected_schema"` (as dict) and `"expected_schema_yaml"` (as parseable-to-dict string) with verdict FAIL.
- If `"expected_schema_yaml"` is provided but does not parse to a dictionary via `yaml.safe_load`, the context is considered invalid.

**Schema comparison:**
- Parses and applies the migration SQL to an in-memory SQLite database (or file-based if specified elsewhere in the call chain).
- The SQL is first parsed in the specified dialect, then transpiled to SQLite dialect for execution.
- Extracts the resulting schema from the SQLite database via introspection.
- Normalizes both expected and actual schemas into a format mapping table names to sets of `(column_name, type, nullable)` tuples.
- Column types are normalized to uppercase.
- Nullable defaults to `True` if not specified in the schema.

**Comparison rules:**
- Table name sets must match exactly between expected and actual schemas.
- For each table, the set of `(column_name, type)` pairs must match exactly.
- Nullable differences are NOT considered drift; the gate passes with a note if only nullable flags differ.
- If table sets differ, returns FAIL with a note listing both expected and actual table names.
- If column name/type sets differ for any table, returns FAIL with a note identifying the table and both column sets.

**Return value:**
Returns a `GateResult` with:
- `gate_name`: The name of this gate instance
- `verdict`: `Verdict.PASS` if schemas match (ignoring nullable), `Verdict.FAIL` otherwise
- `notes`: 
  - On success with no nullable drift: "Schema matches expected."
  - On success with nullable drift: "Schema matches expected (nullable differs: <details>)."
  - On failure: Description of the drift (table mismatch or column mismatch)
  - On input validation failure: Description of the validation error

**Side effects and safety:**
- Creates a temporary SQLite database connection to apply the migration.
- The connection is closed after introspection regardless of success or failure.
- Sets SQLite attachment limit to 0 to prevent ATTACH statements (defense-in-depth security measure).
- SQL statements are parsed and transpiled; filesystem escape attempts are rejected during parsing.

## What we want to verify

- When target is not a string, returns GateResult with verdict FAIL and notes containing the actual type name
- When context lacks both "expected_schema" dict and valid "expected_schema_yaml", returns FAIL with notes about missing context
- When "expected_schema_yaml" is provided as a string, it is parsed via yaml.safe_load
- When "expected_schema_yaml" parses to a non-dict value, the gate treats it as invalid context and returns FAIL
- When "expected_schema" is already a dict in context, it is used directly without YAML parsing
- The dialect from context["dialect"] is used for initial SQL parsing (defaults to "postgres")
- Migration SQL is transpiled to SQLite dialect for execution
- Schema comparison normalizes column types to uppercase
- Schema comparison treats nullable as True by default when not specified
- When table name sets differ between expected and actual, verdict is FAIL with notes listing both sets
- When column (name, type) pairs differ for any table, verdict is FAIL with notes identifying the table and both column sets
- When only nullable flags differ, verdict is PASS with notes describing the nullable differences
- When schemas match exactly including nullable, verdict is PASS with notes "Schema matches expected."
- The SQLite connection is closed in a finally block regardless of execution outcome
- Empty or None statements from SQL parsing are skipped during transpilation

## Inventory references

- Arguments:
- (gate class)
- Related gates: MigrationDriftGate.run
- Related ADRs:
- ADR 0007: Code-aware stories and docstring drift detection — Accepted

## Open questions

- Docstring drift: The docstring states "Compare oracle schema output vs expected schema YAML" but the code accepts the expected schema as either a dictionary via `"expected_schema"` key OR as YAML via `"expected_schema_yaml"` key, not exclusively from YAML.
- Docstring drift: The docstring mentions "oracle schema output" but the code actually applies the migration SQL to SQLite (after transpilation) and introspects the resulting SQLite schema, not an oracle database.

## Status

draft
