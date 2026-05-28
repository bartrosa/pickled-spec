# Story: run_all

## Metadata

- **Surface kind:** gate
- **Package:** pickled-schema
- **Surface id:** pickled_schema_run_all
- **Code depth:** callgraph | **Units read:** 5 | **Unresolved:** 3

## Context

This gate function is used by a build or CI/CD pipeline to validate OpenAPI specification files and measure schema coverage against Gherkin feature files. It is the entry point for schema validation checks in a project that follows a convention of storing OpenAPI specs under `specs/` and feature files under `features/`.

## What the target does today

**Input:**
- Accepts a `workdir` parameter that can be either a `Path` object or a string representing a directory path.
- Converts the workdir to an absolute Path via `.resolve()`.

**Discovery phase:**
- Searches for OpenAPI specification files matching `specs/*.yaml` and `specs/*.yml` patterns under the resolved workdir, sorted lexicographically.
- If no spec files are found, returns a single-element list containing a `GateResult` with gate_name "schema.openapi", verdict WARN, and notes "no specs/*.yaml".

**Validation phase:**
For each discovered spec file:
- Loads the file as UTF-8 text and parses it as YAML or JSON based on file extension (`.yaml`, `.yml`, `.json`).
- Falls back to YAML parsing if the extension is unrecognized.
- Rejects files that don't parse to a dict at the root level.
- Rejects OpenAPI 2.0 specs (those with a "swagger" field).
- Requires a string-valued "openapi" top-level field and recognizes versions starting with "3.0", "3.1", or "3.2".
- Validates the parsed spec using `openapi-spec-validator` (requires the `pickled-schema[openapi]` extra to be installed).
- If loading or validation fails due to OSError, ValueError, TypeError, or SchemaValidationError, appends a FAIL result with gate_name "schema.openapi.validate.<filename>" and the exception message as notes.
- If validation succeeds, appends a PASS result with the same gate_name pattern and the spec's relative path as notes, and retains the spec for coverage analysis.

**Coverage phase:**
- If no specs are valid, returns results immediately without coverage checks.
- If multiple valid specs exist, appends a WARN result with gate_name "schema.openapi.note" indicating how many specs were found and that the first (lexicographically) will be used for coverage.
- Uses only the first valid spec for coverage analysis.
- Searches for feature files matching `features/**/*.feature` under workdir, sorted.
- If feature files are found, delegates to `SchemaCoverageGate().run(spec_dict, context={"feature_paths": feature_paths})` (behavior unresolved).
- Appends a "schema.coverage" result using the verdict, findings, and notes from the delegated gate; defaults notes to the spec's relative path if none provided.

**Output:**
- Returns a list of `GateResult` objects representing all validation and coverage checks performed.
- The list may contain:
  - Zero or one discovery warning (if no specs found)
  - One validation result per spec file (PASS or FAIL)
  - Zero or one multi-spec warning (if multiple valid specs)
  - Zero or one coverage result (if features exist and at least one valid spec)

**Error conditions:**
- Raises SchemaValidationError if `openapi-spec-validator` is not installed.
- File I/O errors, parse errors, and validation errors are caught and converted to FAIL results rather than propagated.

## What we want to verify

- Given a directory with no `specs/` subdirectory or no `.yaml`/`.yml` files in it, returns a single WARN result with notes "no specs/*.yaml".
- Given a directory with `specs/example.yaml` containing valid OpenAPI 3.x, returns at least one PASS result with gate_name "schema.openapi.validate.example.yaml".
- Given a spec file that cannot be parsed as YAML/JSON, returns a FAIL result for that file.
- Given a spec with a root that is not a dict (e.g., a list), returns a FAIL result.
- Given a spec with "swagger" field instead of "openapi", returns a FAIL result mentioning OpenAPI 2.0 is unsupported.
- Given a spec without an "openapi" field, returns a FAIL result.
- Given a spec with "openapi" version not starting with "3.0", "3.1", or "3.2", returns a FAIL result.
- Given multiple valid specs in `specs/`, returns a WARN result indicating which spec is used for coverage.
- Given valid spec(s) but no `features/**/*.feature` files, does not append a coverage result.
- Given valid spec(s) and feature files, returns a "schema.coverage" result with verdict/findings/notes from the delegated gate.
- When `openapi-spec-validator` is not installed, raises SchemaValidationError during validation phase.
- The returned list of results is in deterministic order: discovery warnings, then validation results in lexicographic filename order, then multi-spec warnings, then coverage results.

## Inventory references

- Arguments:
- (gate class)
- Related gates: run_all
- Related ADRs:
- (none directly relevant)

## Open questions

- Docstring drift: The docstring states "Validate OpenAPI under `specs/`" but does not mention the function also performs schema coverage analysis against feature files, which is a major part of the observable behavior.
- Docstring drift: The docstring does not mention the function returns a list of `GateResult` objects, omitting the return type entirely.
- Docstring drift: The docstring does not mention any of the warning or failure conditions (no specs found, multiple specs found, validation failures, missing dependencies).

## Status

draft
