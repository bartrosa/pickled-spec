# Story: run_all

## Metadata

- **Surface kind:** gate
- **Package:** pickled-data
- **Surface id:** pickled_data_run_all
- **Code depth:** callgraph | **Units read:** 4 | **Unresolved:** 0

## Context

This gate function is used by clients running quality checks on a data project's migration files. It orchestrates parsing of SQL migration files and validates whether applying those migrations produces a schema that matches an expected YAML specification. The function is designed to be called with a project working directory, returning a list of pass/warn/fail gate results that can be aggregated into a quality report.

## What the target does today

**Accepts**: A working directory path (Path or str) containing a `migrations/` subdirectory and optionally an `expected_schema.yaml` file at the root.

**Returns**: A list of GateResult objects, each representing a specific check. The function never returns an empty list.

**Basic flow**:
- Resolves the working directory to an absolute path
- Globs for `migrations/*.sql` files and sorts them by filename
- If no migration files exist, returns a single WARN result with gate_name "data.migrations" and notes "no migrations/*.sql"
- For each migration file found, attempts to parse it as SQLite-dialect SQL:
  - On successful parse: emits a PASS result with gate_name "data.parse.{filename}"
  - On parse failure (SQLParseError): emits a FAIL result with gate_name "data.parse.{filename}" and the exception message as notes
- If more than one migration file exists, emits an additional WARN result with gate_name "data.migrations.note" explaining that multiple migrations will be applied in filename order
- If `expected_schema.yaml` exists and is a file, and at least one migration exists:
  - Concatenates all migration file contents with double-newline separators
  - Loads the YAML file as a dict using yaml.safe_load
  - If the loaded YAML is a dict, delegates to MigrationDriftGate().run() with the combined SQL, passing expected schema and dialect "sqlite" in context
  - Appends the drift gate result with gate_name "data.migration_drift"

**Error modes**:
- SQL parse errors are caught and converted to FAIL gate results (not raised)
- .dbt file extensions in migration paths trigger NotImplementedError
- YAML parsing errors or file read errors are not caught and will propagate to the caller
- Type mismatches or other exceptions from MigrationDriftGate().run() are not caught

**Side effects**:
- Reads files from disk (migration SQL files and expected_schema.yaml)
- No writes or persistent state changes

**Constraints**:
- Hard-coded to SQLite dialect for all parsing and drift checking
- Migration files must have .sql extension to be discovered by glob
- Expected schema must deserialize to a dict, otherwise drift gate is skipped silently
- Filename-based lexicographic sorting determines migration application order

## What we want to verify

- When workdir contains no migrations/*.sql files, returns exactly one GateResult with verdict WARN and gate_name "data.migrations"
- When migrations exist but expected_schema.yaml does not exist or is not a file, drift gate result is not included in output
- When a migration file cannot be parsed, returns a FAIL result for that file with gate_name "data.parse.{filename}" and includes the parse error message
- When a migration file parses successfully, returns a PASS result with gate_name "data.parse.{filename}"
- When exactly one migration exists, no WARN result about multiple migrations is emitted
- When more than one migration exists, emits a WARN result with gate_name "data.migrations.note"
- When expected_schema.yaml exists and contains a dict, and migrations exist, includes a gate result with gate_name "data.migration_drift"
- All SQL parsing uses "sqlite" dialect regardless of file content or project configuration
- Migration files are sorted lexicographically by filename before processing
- Combined SQL passed to drift gate concatenates migrations with "\n\n" separator
- YAML file that does not deserialize to a dict causes drift gate to be skipped (no error raised)

## Inventory references

- Arguments:
- (gate class)
- Related gates: run_all
- Related ADRs:
- (none directly relevant)

## Open questions

- Docstring drift: Docstring does not specify the return value is a list of GateResult objects
- Docstring drift: Docstring does not mention the WARN result returned when no migrations exist
- Docstring drift: Docstring does not mention the per-file parse gate results
- Docstring drift: Docstring does not mention the WARN result for multiple migrations
- Docstring drift: Docstring claims general parsing behavior but code hard-codes SQLite dialect, not configurable
- Docstring drift: Docstring does not specify that drift checking is conditional on expected_schema.yaml existing and being a valid dict-containing YAML file

## Status

draft
