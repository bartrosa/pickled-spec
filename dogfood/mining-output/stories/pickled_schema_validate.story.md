# Story: validate

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-schema
- **Surface id:** pickled_schema_validate
- **Code depth:** callgraph | **Units read:** 4 | **Unresolved:** 0

## Context

This CLI command surface is used to validate schema files (OpenAPI, JSON Schema, or Protocol Buffers) against their respective format specifications. Callers invoke this command by providing a file path, and the command determines the schema format, performs validation, and outputs a JSON result indicating whether the file is valid.

## What the target does today

**Input acceptance:**
- Accepts a single required parameter `file` of type `Path` representing the schema file to validate.
- Infers the schema format from the file extension:
  - `.yaml` or `.yml` → treats as OpenAPI 3.1
  - `.json` → treats as JSON Schema 2020-12
  - `.proto` → treats as Protocol Buffers 3
- Raises a `click.ClickException` with message "cannot infer format from extension {suffix!r}; use --format" if the file extension does not match the expected patterns (case-insensitive comparison).

**Validation behavior by format:**
- For OpenAPI formats (3.0, 3.1, 3.2):
  - Loads the file content into a dictionary
  - Delegates validation to `openapi-spec-validator` library
  - Requires the optional dependency `pickled-schema[openapi]` to be installed; raises `SchemaValidationError` with message "install pickled-schema[openapi] for OpenAPI validation" if not available
  - Raises `SchemaValidationError` with message "OpenAPI validation failed" and error details if validation fails
- For JSON Schema 2020-12:
  - Loads the file into a dictionary
  - Delegates validation to `validate_json_schema_document` (unresolved callee)
- For Protocol Buffers 3:
  - Delegates parsing and implicit validation to `parse_proto_file` (unresolved callee)

**Output:**
- On successful validation, writes a JSON object to standard output via `click.echo` with structure:
  ```json
  {"valid": true, "format": "<format-value>"}
  ```
  where `<format-value>` is the string representation of the inferred SchemaFormat enum value.

**Error modes:**
- Unrecognized file extension → `click.ClickException`
- Missing OpenAPI validation dependencies → `SchemaValidationError`
- OpenAPI validation failure → `SchemaValidationError` with error details
- JSON Schema or Proto3 validation failures depend on behavior of unresolved callees

**Side effects:**
- Outputs JSON to standard output (via `click.echo`)
- File I/O occurs when loading the schema file

## What we want to verify

- Accept `.yaml`, `.yml`, `.json`, and `.proto` file extensions (case-insensitive)
- Reject files with unrecognized extensions by raising `click.ClickException` with appropriate message
- Infer OpenAPI 3.1 format from `.yaml` or `.yml` extensions
- Infer JSON Schema 2020-12 format from `.json` extension
- Infer Proto3 format from `.proto` extension
- Output JSON with `{"valid": true, "format": "<format>"}` structure on successful validation
- Raise `SchemaValidationError` with installation message when `openapi-spec-validator` is not available for OpenAPI files
- Raise `SchemaValidationError` with "OpenAPI validation failed" message when OpenAPI validation detects errors
- Include nested schema errors in the raised exception when OpenAPI validator provides them
- Load OpenAPI files and pass dictionary to `openapi-spec-validator.validate`
- Call `validate_json_schema_document` for JSON files
- Call `parse_proto_file` for Proto files
- Write output to standard output using `click.echo`

## Inventory references

- Arguments:
- `file` (required): 
- Related gates: SchemaAmbiguityGate.run, SchemaCoverageGate.run, run_all
- Related ADRs:
- ADR 0007: Code-aware stories and docstring drift detection — Accepted

## Open questions

- Docstring drift: The docstring states "Validate a schema file against its format specification" but does not mention that the format is inferred from the file extension rather than being explicitly specified or detected from content.
- Docstring drift: The docstring does not document the specific output format (JSON with "valid" and "format" fields written to standard output).
- Docstring drift: The docstring does not mention the file extension requirements or the error raised for unrecognized extensions.
- Docstring drift: The docstring does not mention the optional dependency requirement for OpenAPI validation or the resulting error when missing.

## Status

draft
