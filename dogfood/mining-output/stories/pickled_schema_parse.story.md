# Story: parse

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-schema
- **Surface id:** pickled_schema_parse
- **Code depth:** callgraph | **Units read:** 6 | **Unresolved:** 0

## Context

This CLI command is used by operators and developers to quickly inspect a schema file's metadata without fully validating or processing it. It provides a lightweight way to verify that a schema file can be loaded, determine its format (either explicitly specified or auto-detected), and see basic statistics about the content. The command outputs structured JSON to stdout, making it suitable for both human inspection and scripting/pipeline integration.

## What the target does today

Accepts a file path and optional format specifier. When format is not provided, infers it from file extension: `.yaml`/`.yml` → OpenAPI 3.1, `.json` → JSON Schema 2020-12, `.proto` → Proto3. Raises an error for unrecognized extensions when format is not explicitly specified.

Loads the schema file according to the determined format:
- **OpenAPI files** (.yaml, .yml, or explicit OpenAPI 3.0/3.1/3.2 format): Reads file as text, detects the actual OpenAPI version from content (may differ from inferred/specified format), returns the detected version in output
- **JSON Schema files** (.json or explicit json_schema_2020_12): Reads file as UTF-8 text, parses as JSON, validates root is an object (raises SchemaParseError if not)
- **Proto3 files** (.proto or explicit proto3): Invokes `protoc` via `grpc_tools.protoc` Python module with the file's parent directory as proto_path, generates a descriptor set with imports included, base64-encodes the binary descriptor, stores encoded string as content

Prints to stdout a JSON object with four fields:
- `format`: the schema format as a string (detected version for OpenAPI, specified format otherwise)
- `endpoint_id`: always null for file-based schemas
- `source`: always the string "file"
- `content_bytes`: byte length of the UTF-8 encoded content string (raw text for OpenAPI/JSON Schema, base64-encoded descriptor for Proto3)

Raises ClickException if:
- Format cannot be inferred from file extension and no explicit format provided
- Explicit format is not one of the supported values
- For Proto3, if `protoc` subprocess returns non-zero exit code

Raises SchemaParseError if JSON Schema root is not a JSON object.

File reading errors (missing file, permission denied, encoding errors) propagate as standard Python exceptions.

The command produces side effects only to stdout (via click.echo) and does not modify any files.

## What we want to verify

- Given a .yaml file with valid OpenAPI 3.1 content and no format argument, outputs JSON with format field matching detected OpenAPI version
- Given a .json file with valid JSON Schema and no format argument, outputs JSON with format="json_schema_2020_12"
- Given a .proto file with valid Proto3 syntax and no format argument, outputs JSON with format="proto3" and content_bytes representing base64-encoded descriptor length
- Given explicit --format argument, uses that format instead of inferring from extension
- Given a file with .txt extension and no format argument, raises ClickException mentioning inability to infer format
- Given a .json file containing a JSON array as root, raises SchemaParseError
- Given a nonexistent file path, raises file-not-found exception before format processing
- Output JSON always contains endpoint_id=null and source="file" for any valid file input
- For Proto3 files, if protoc compilation fails (syntax error, missing import), raises RuntimeError with protoc error message
- content_bytes field equals len(content.encode("utf-8")) where content is the artifact's content string
- OpenAPI format detection may return different version than inferred (e.g., .yaml file could be detected as OpenAPI 3.0 if content specifies that version)

## Inventory references

- Arguments:
- `file` (required): 
- `fmt` (optional): Schema format (auto-detected from extension when omitted).
- Related gates: SchemaAmbiguityGate.run, SchemaCoverageGate.run, run_all
- Related ADRs:
- (none directly relevant)

## Open questions

- Docstring drift: Docstring claims "print a short summary" but does not specify the output is JSON format with four specific fields (format, endpoint_id, source, content_bytes)
- Docstring drift: Docstring does not mention format auto-detection behavior or the mapping of file extensions to schema formats
- Docstring drift: Docstring does not mention any error conditions (unsupported extensions, invalid JSON Schema structure, protoc failures)
- Docstring drift: Docstring does not clarify that endpoint_id is always null and source is always "file" for this command

## Status

draft
