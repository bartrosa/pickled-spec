# Story: schema_check_schema_coverage

## Metadata

- **Surface kind:** mcp_tool
- **Package:** pickled-schema
- **Surface id:** schema_check_schema_coverage

## Context

QA engineers and CI pipeline scripts use this tool to validate that all `@schema:endpoint` tags referenced in Cucumber feature files correspond to actual endpoints defined in an OpenAPI specification. This prevents runtime failures where tests reference non-existent API endpoints and ensures test coverage stays synchronized with the API schema.

## What the target does today

The tool verifies that every `@schema:endpoint` tag found in the provided feature files exists as a defined endpoint in the given OpenAPI specification YAML. It checks for coverage by matching endpoint identifiers from feature annotations against the spec's endpoint definitions.

## What we want to verify

- Returns success when all `@schema:endpoint` tags in feature_texts reference endpoints that exist in spec_yaml
- Returns failure or error indication when one or more `@schema:endpoint` tags reference endpoints not found in spec_yaml
- Parses spec_yaml as an OpenAPI specification document to extract valid endpoint definitions
- Scans feature_texts to extract all `@schema:endpoint` tag values
- Reports which `@schema:endpoint` tags are missing from the specification when coverage is incomplete
- Handles empty or malformed spec_yaml gracefully with appropriate error messaging
- Handles empty feature_texts without error (zero tags means full coverage)
- Does not validate endpoint implementation or test correctness, only tag-to-spec correspondence

## Inventory references

- Arguments:
- `spec_yaml` (required): 
- `feature_texts` (required): 
- Related gates: SchemaAmbiguityGate.run, SchemaCoverageGate.run, run_all
- Related ADRs:
- ADR 0004: Multi-ruleset workspace configuration — Accepted

## Open questions

(none)

## Status

draft
