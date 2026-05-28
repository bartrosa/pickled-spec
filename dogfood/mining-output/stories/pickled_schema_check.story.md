# Story: check

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-schema
- **Surface id:** pickled_schema_check
- **Code depth:** callgraph | **Units read:** 7 | **Unresolved:** 0

## Context

This CLI command is used to verify that all `@schema:endpoint` tags found in Gherkin .feature files correspond to actual endpoints defined in an OpenAPI specification document. It is typically run as part of a CI/CD pipeline or pre-commit check to ensure feature files reference only documented API endpoints, preventing drift between acceptance tests and the actual API contract.

## What the target does today

**Inputs:**
- `spec`: A required Path to an OpenAPI specification file (YAML or JSON). The file must contain a valid OpenAPI 3.0, 3.1, or 3.2 document with an `openapi` version field at the root. OpenAPI 2.0 (Swagger) is rejected.
- `feature_dir`: An optional Path to a directory. When provided, the command recursively searches for all `**/*.feature` files within that directory tree.
- `feature_glob`: An optional string glob pattern. When provided, the command expands the glob recursively to find matching .feature files.

**Mutual exclusivity:** Exactly one of `feature_dir` or `feature_glob` must be provided. If both are provided, or if neither is provided, the command raises a ClickException and exits.

**Processing:**
1. Loads and parses the OpenAPI specification file. If the file cannot be parsed as YAML or JSON, or if the schema version is unsupported or missing, a SchemaParseError is raised.
2. Resolves the list of .feature files from the provided directory or glob pattern. Files are sorted. If no files match the pattern, a ClickException is raised with message "No feature files matched".
3. Instantiates a SchemaCoverageGate and runs it with the parsed spec and the list of feature file paths in the context.
4. The gate scans each .feature file for `@schema:endpoint` tags (format appears to be method and path pairs) and checks whether the OpenAPI spec defines each referenced endpoint.

**Output:**
Always writes a JSON object to stdout with the following structure:
- `gate`: string name of the gate (from result.gate_name)
- `verdict`: string value of the verdict enum ("PASS", "FAIL", or "WARN")
- `notes`: string describing the result
- `findings`: array of objects, each with `tag` and `source` fields, representing only SchemaCoverageFinding instances

**Exit behavior:**
- If the verdict is `FAIL`, exits with status code 2
- If the verdict is `WARN`, exits with status code 1
- If the verdict is `PASS`, exits with status code 0 (normal termination)

**Error modes:**
- Both `feature_dir` and `feature_glob` provided → ClickException "Use only one of --feature-dir or --feature-glob"
- Neither `feature_dir` nor `feature_glob` provided → ClickException "Provide --feature-dir or --feature-glob"
- No .feature files found → ClickException "No feature files matched"
- Spec file cannot be parsed or has wrong format → SchemaParseError
- OpenAPI version is 2.0 or unsupported → SchemaParseError

## What we want to verify

- When neither `feature_dir` nor `feature_glob` is provided, command raises ClickException
- When both `feature_dir` and `feature_glob` are provided, command raises ClickException
- When `feature_dir` points to a directory with no .feature files, command raises ClickException with message "No feature files matched"
- When `spec` points to a valid OpenAPI 3.x file and all `@schema:endpoint` tags in .feature files match spec endpoints, command writes JSON with verdict "PASS" and exits 0
- When `spec` points to a valid OpenAPI 3.x file and at least one `@schema:endpoint` tag in .feature files does not match any spec endpoint, command writes JSON with verdict "FAIL", includes findings array with tag and source for each missing endpoint, and exits 2
- When `spec` points to an OpenAPI 2.0 file (contains "swagger" field), command raises SchemaParseError
- When `spec` file is not valid YAML or JSON, command raises SchemaParseError
- When `spec` file is valid YAML/JSON but lacks "openapi" version field, command raises SchemaParseError
- JSON output always contains exactly four keys: "gate", "verdict", "notes", and "findings"
- Findings array only includes objects with "tag" and "source" fields
- When verdict is "WARN", command exits with status code 1
- `feature_glob` pattern is expanded recursively and only includes actual files (not directories)
- Feature files discovered via `feature_dir` are sorted by path
- Feature files discovered via `feature_glob` are sorted by path

## Inventory references

- Arguments:
- `spec` (required): 
- `feature_dir` (optional): Directory tree containing .feature files.
- `feature_glob` (optional): Glob of .feature files (alternative to --feature-dir).
- Related gates: SchemaAmbiguityGate.run, SchemaCoverageGate.run, run_all
- Related ADRs:
- (none directly relevant)

## Open questions

- Docstring drift: The docstring states "Run SchemaCoverageGate on @schema:endpoint tags in .feature files" but does not mention that the command requires exactly one of `feature_dir` or `feature_glob` to be provided, that it validates the OpenAPI version, that it produces structured JSON output to stdout, or that it uses specific exit codes (0, 1, 2) based on verdict.

## Status

draft
