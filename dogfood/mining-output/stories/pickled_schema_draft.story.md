# Story: draft

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-schema
- **Surface id:** pickled_schema_draft
- **Code depth:** callgraph | **Units read:** 5 | **Unresolved:** 4

## Context

This CLI command is used by developers who want to generate an OpenAPI 3.1 path item specification from a Gherkin scenario file. It automates the creation of API documentation by reading behavior-driven development (BDD) scenarios and producing corresponding OpenAPI schema fragments. The command supports both writing to a file or printing to stdout, making it suitable for both automated pipelines and interactive use.

## What the target does today

**Inputs:**
- Accepts four parameters: `method` (string), `endpoint_path` (string), `gherkin_file` (Path object), and optional `output` (Path object or None)
- Reads the Gherkin file content as UTF-8 encoded text
- Does not validate the method string format or endpoint_path structure before passing to the drafter

**LLM Client Configuration:**
- Attempts to build an LLM client first by checking the `PICKLED_SCHEMA_LLM_FACTORY` environment variable
- If `PICKLED_SCHEMA_LLM_FACTORY` is set, expects format "module:callable" and dynamically imports and invokes it; raises `ClickException` if the format lacks a colon separator
- If `PICKLED_SCHEMA_LLM_FACTORY` is not set, falls back to `PICKLED_LLM_PROVIDER` environment variable (defaults to "anthropic") and uses pickled_core's build_client with loaded configuration
- Converts any `ConfigError` from the fallback client builder into a `ClickException`

**Drafting Process:**
- Delegates to `OpenAPIDrafter.draft_endpoint()` which attempts up to 3 times to generate valid OpenAPI YAML
- For each attempt, renders a prompt template (unresolved call) with the method (uppercased), path, gherkin context, and existing component names
- Invokes an LLM with the prompt and system instruction to output only YAML
- Parses the LLM output as YAML and expects a dictionary
- Unwraps the path item if the LLM returns either a bare operation object or a single-key wrapper with an HTTP method
- Validates the path item by embedding it in a minimal OpenAPI 3.1.0 envelope with the specified path and method (lowercased)
- Uses openapi-spec-validator for validation; requires the pickled-schema[openapi] extra to be installed
- If validation fails, includes previous validation errors in the next prompt attempt
- After 3 failed attempts, raises `SchemaValidationError` with the last error message

**Outputs:**
- If `output` parameter is provided: writes the generated YAML content to the specified file as UTF-8 text and prints a confirmation message to stderr
- If `output` is None: prints the generated YAML content to stdout
- The generated content is a YAML-formatted path item (not a complete OpenAPI document), using safe_dump with sort_keys=False and default_flow_style=False

**Error Conditions:**
- Raises `ClickException` if `PICKLED_SCHEMA_LLM_FACTORY` is malformed (missing colon)
- Raises `ClickException` if LLM client configuration fails (ConfigError from pickled_core)
- Raises `SchemaValidationError` if the LLM output is not a YAML mapping
- Raises `SchemaValidationError` if openapi-spec-validator extra is not installed
- Raises `SchemaValidationError` if unable to produce valid OpenAPI after 3 attempts, including the last validation error
- May raise file I/O errors if gherkin_file cannot be read or output cannot be written

## What we want to verify

- When gherkin_file contains valid text and output is None, the command prints valid OpenAPI path item YAML to stdout
- When gherkin_file contains valid text and output is a Path, the command writes the YAML to that file and prints "Wrote {output}" to stderr
- When PICKLED_SCHEMA_LLM_FACTORY is set to "module:callable" format, the command attempts to import and invoke the specified factory
- When PICKLED_SCHEMA_LLM_FACTORY is set without a colon, the command raises ClickException with message about required format
- When PICKLED_SCHEMA_LLM_FACTORY is not set, the command uses PICKLED_LLM_PROVIDER (defaulting to "anthropic")
- When the LLM produces invalid YAML mapping output, the command retries up to 3 times
- When the LLM produces output that fails OpenAPI validation, the command includes previous errors in subsequent prompts
- When 3 validation attempts all fail, the command raises SchemaValidationError with details about the last failure
- When openapi-spec-validator is not installed, the command raises SchemaValidationError requesting pickled-schema[openapi]
- The method parameter is uppercased for endpoint_id and prompt rendering but lowercased when constructing the validation envelope
- The output YAML is formatted with sort_keys=False and default_flow_style=False

## Inventory references

- Arguments:
- `method` (required): 
- `endpoint_path` (required): 
- `gherkin_file` (required): 
- `output` (optional): 
- Related gates: SchemaAmbiguityGate.run, SchemaCoverageGate.run, run_all
- Related ADRs:
- (none directly relevant)

## Open questions

- Docstring drift: The docstring states the function drafts "an OpenAPI 3.1 path item from a Gherkin scenario" but omits that it may perform up to 3 retry attempts with validation feedback
- Docstring drift: The docstring does not mention the LLM client configuration mechanism via environment variables (PICKLED_SCHEMA_LLM_FACTORY and PICKLED_LLM_PROVIDER)
- Docstring drift: The docstring does not mention that openapi-spec-validator must be installed (via pickled-schema[openapi] extra) for the function to work
- Docstring drift: The docstring does not mention the two output modes (file vs stdout) or the stderr confirmation message behavior
- Docstring drift: The docstring does not mention any error conditions or exceptions that may be raised

## Status

draft
