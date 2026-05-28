# Story: parse

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-data
- **Surface id:** pickled_data_parse
- **Code depth:** callgraph | **Units read:** 6 | **Unresolved:** 0

## Context

This CLI command is used by developers and tooling to inspect migration SQL files. It parses a SQL file into an abstract syntax tree (AST) and outputs a JSON summary to standard output. The command is invoked as part of the pickled-data CLI tool to understand the structure of migration SQL before execution or analysis. Related gates (DataContractGate.run, MigrationDriftGate.run, run_all) likely consume or validate migration files, making this parse command useful for debugging and inspection during development or CI/CD workflows.

## What the target does today

The surface accepts a file path (`migration`) and an optional SQL dialect string (`dialect`). It performs the following observable behaviors:

**Input validation:**
- Rejects files with a `.dbt` suffix by raising `NotImplementedError` with a message indicating DBT files are not supported
- This rejection occurs twice in the call chain (once in `_check_dbt` at the root level, once in `_reject_dbt` within `load_sql_file`)

**File processing:**
- Reads the file at the given path using UTF-8 encoding
- Parses the file content as SQL using the specified dialect (defaults to "postgres" if not provided)
- Parsing delegates to `sqlglot.parse_one` (external library call)

**Error handling:**
- If the external parser raises `sqlglot.errors.ParseError`, wraps it as `SQLParseError` with the original error message
- If parsing returns `None`, raises `SQLParseError` with message "empty parse result"
- File I/O errors (e.g., file not found, permission denied) propagate as standard Python exceptions

**Output:**
- Prints a JSON object to standard output (via `click.echo`) containing:
  - `"dialect"`: the dialect string used for parsing
  - `"kind"`: the AST node type name (Python class name of the root AST node)
  - `"sql"`: the SQL representation of the AST, rendered in "postgres" dialect regardless of input dialect
- The JSON is formatted with 2-space indentation

**Side effects:**
- Writes formatted JSON to standard output
- No modifications to the filesystem or other persistent state

**Return value:**
- The function signature indicates it returns `None`; output is via side effect (printing to stdout)

## What we want to verify

- Accepts a Path object and optional dialect string as parameters
- Rejects files with `.dbt` extension by raising NotImplementedError before attempting to read
- Reads the migration file content using UTF-8 encoding
- Parses SQL content using the specified dialect (or "postgres" if not specified)
- Raises SQLParseError when the SQL cannot be parsed by sqlglot
- Raises SQLParseError with message "empty parse result" when parser returns None
- Outputs valid JSON to stdout containing "dialect", "kind", and "sql" keys
- The "dialect" field in output matches the dialect parameter used for parsing
- The "kind" field contains the Python class name of the AST root node
- The "sql" field contains the AST rendered in "postgres" dialect regardless of input dialect
- JSON output is indented with 2 spaces
- Returns None (no return value, output is side effect only)
- Propagates file I/O exceptions (FileNotFoundError, PermissionError, etc.) without wrapping

## Inventory references

- Arguments:
- `migration` (required): 
- `dialect` (optional): 
- Related gates: DataContractGate.run, MigrationDriftGate.run, run_all
- Related ADRs:
- (none directly relevant)

## Open questions

- Docstring drift: The docstring states "print AST summary" but does not mention that the output is formatted as JSON, which is a specific and important detail for callers who need to parse the output
- Docstring drift: The docstring does not mention the `.dbt` file rejection behavior, which is a prominent input validation constraint
- Docstring drift: The docstring does not describe the structure of the output (the three fields: dialect, kind, sql) or that the SQL output is always rendered in postgres dialect
- Docstring drift: The docstring does not mention any error conditions (SQLParseError, NotImplementedError for .dbt files)

## Status

draft
