# Story: draft

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-data
- **Surface id:** pickled_data_draft
- **Code depth:** callgraph | **Units read:** 8 | **Unresolved:** 3

## Context

CLI command used by developers and automation pipelines to generate SQL migration files from natural-language descriptions. Invoked when a schema change is needed but the exact DDL is not yet written. The command consults an LLM to produce a draft migration, optionally considering the current schema state, and outputs the SQL plus explanatory metadata. Related to other pickled-data commands that validate schemas (DataContractGate) and check for drift (MigrationDriftGate).

## What the target does today

**Inputs:**
- `intent`: A string representing either a file path to read intent text from, or the literal `"-"` to read from standard input. The content is treated as natural-language description of the desired migration.
- `dialect`: A string naming the SQL dialect (e.g., "postgres", "mysql"). Used both in the LLM prompt and for SQL parsing validation.
- `current_schema`: Optional Path to a YAML file describing the current schema. If provided, the file is read (UTF-8) and passed to the LLM as context. If None, no schema context is provided.
- `output`: Optional Path for writing the generated SQL migration. If None, SQL is written to standard output.

**Returns:**
The function signature is `-> None`; it never returns a value. Success or failure is communicated via exit codes and side effects.

**Success path:**
1. Reads the current schema YAML file (if `current_schema` is not None) using UTF-8 encoding.
2. Builds an LLM client by delegating to an internal function that reads configuration from environment variable `PICKLED_DATA_LLM_FACTORY`.
3. Constructs a prompt incorporating the intent text, SQL dialect, and optional schema YAML, instructing the LLM to emit DDL with a comment line `-- intent: <summary>`, followed by a sentinel string and rationale.
4. Delegates to the unresolved `self._llm.complete` call (temperature=0.0, max_tokens=4000) to generate completion text.
5. Splits the LLM output at a rationale sentinel to separate SQL text from rationale explanation.
6. Validates the SQL text by attempting to parse it with sqlglot using the specified dialect, and scans for destructive operations (case-insensitive "drop table" in any line).
7. If `output` is provided, writes the SQL text to that file (UTF-8). Otherwise, writes SQL text to standard output.
8. Writes rationale lines to standard error, each prefixed with `"rationale: "`.
9. Writes validation warnings to standard error, each prefixed with `"warning: "`.
10. If any validation warnings were produced, exits with code 1. Otherwise, exits normally (implicit 0).

**Error paths:**
- If LLM client configuration fails (ConfigError), raises `click.ClickException` with the configuration error message, which Click handles as a user-friendly error.
- If any other exception occurs during LLM client building, intent reading, drafting, or output emission (except `click.ClickException`), the exception message is written to standard error and the process exits with code 2.
- File read failures (e.g., `current_schema` or intent file not found, encoding errors) propagate as exceptions caught by the generic handler, resulting in error message to stderr and exit code 2.

**Observable side effects:**
- Reads from standard input if `intent` is `"-"`.
- Reads files from disk when `intent` is a file path or `current_schema` is provided.
- Writes SQL migration to the specified `output` file or to standard output.
- Writes rationale and warnings to standard error.
- Process exit code: 0 on success without warnings, 1 on success with validation warnings, 2 on error.

**Validation warnings produced:**
- If sqlglot parsing fails for the generated SQL in the specified dialect, a warning containing the parse exception message is emitted.
- For every line containing the substring "drop table" (case-insensitive), a warning is emitted noting the line number and advising confirmation before applying.

## What we want to verify

- Accept `intent` as `"-"` and read from standard input; verify prompt is built with stdin content.
- Accept `intent` as a file path; verify file content is read and used in prompt.
- When `current_schema` is None, verify no schema YAML is read and prompt indicates "none" for schema.
- When `current_schema` is a valid Path, verify file is read as UTF-8 and content is included in prompt.
- When `dialect` is specified, verify it is passed to both the LLM prompt and sqlglot parse validation.
- When `output` is None, verify SQL text is written to standard output.
- When `output` is a Path, verify SQL text is written to that file as UTF-8.
- When LLM output contains the rationale sentinel, verify SQL and rationale are separated and rationale lines are written to stderr with `"rationale: "` prefix.
- When LLM output lacks the rationale sentinel, verify all output is treated as SQL and no rationale is emitted.
- When sqlglot parse fails, verify a warning is written to stderr with `"warning: "` prefix containing the exception message.
- When generated SQL contains "drop table" (any case), verify a warning is emitted to stderr identifying the line number and operation.
- When validation warnings exist, verify process exits with code 1 after emitting SQL and warnings.
- When no validation warnings exist, verify process exits with code 0.
- When LLM client configuration fails with ConfigError, verify a ClickException is raised with the error message.
- When any non-ClickException occurs, verify the exception message is written to stderr and process exits with code 2.
- When `current_schema` file does not exist, verify exception is caught, message written to stderr, exit code 2.
- When intent file does not exist, verify exception is caught, message written to stderr, exit code 2.

## Inventory references

- Arguments:
- `intent` (required): Intent file path or '-' for stdin.
- `dialect` (required): SQL dialect for the migration.
- `current_schema` (optional): Optional existing schema YAML file.
- `output` (optional): Write SQL to this path. Default: stdout.
- Related gates: DataContractGate.run, MigrationDriftGate.run, run_all
- Related ADRs:
- (none directly relevant)

## Open questions

- Docstring drift: The docstring states the function "drafts a SQL migration from a natural-language intent" but omits key observable behaviors: the function reads optional schema context from a file, validates the generated SQL for parse errors and destructive operations, writes rationale and warnings to stderr, exits with different codes based on validation results (0 for clean, 1 for warnings, 2 for errors), and supports reading intent from stdin via `"-"`.
- Docstring drift: The docstring does not mention the `output` parameter's effect of controlling whether SQL is written to a file or stdout.
- Docstring drift: The docstring does not describe any error handling or exit code behavior, which is a significant part of the observable contract.

## Status

draft
