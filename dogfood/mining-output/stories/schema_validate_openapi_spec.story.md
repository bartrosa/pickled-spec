# Story: schema_validate_openapi_spec

## Metadata

- **Surface kind:** mcp_tool
- **Package:** pickled-schema
- **Surface id:** schema_validate_openapi_spec

## Context

This tool is used by MCP clients (Model Context Protocol clients) to validate OpenAPI specification documents provided in YAML format. It is part of the pickled-schema package's validation capabilities, likely called when teams need to ensure their API specifications conform to OpenAPI standards before using them in schema-based testing or documentation workflows.

## What the target does today

The surface validates an OpenAPI YAML document. It accepts a required `spec_yaml` parameter containing the YAML content to be validated.

## What we want to verify

- Given a valid OpenAPI 3.x YAML document in `spec_yaml`, the tool completes without raising validation errors
- Given an invalid OpenAPI YAML document in `spec_yaml`, the tool reports specific validation failures
- Given malformed YAML in `spec_yaml`, the tool reports a parsing error
- Given an empty string in `spec_yaml`, the tool reports a validation error
- The tool accepts `spec_yaml` as a required parameter and fails when it is omitted
- The validation output indicates whether the specification conforms to OpenAPI standards

## Inventory references

- Arguments:
- `spec_yaml` (required): 
- Related gates: SchemaAmbiguityGate.run, SchemaCoverageGate.run, run_all
- Related ADRs:
- ADR 0007: Code-aware stories and docstring drift detection — Accepted

## Open questions

(none)

## Status

draft
