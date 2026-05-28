# Story: schema_draft_openapi_endpoint

## Metadata

- **Surface kind:** mcp_tool
- **Package:** pickled-schema
- **Surface id:** schema_draft_openapi_endpoint

## Context

This surface is used by clients that need to generate OpenAPI 3.1 path item specifications from Gherkin scenario text. The caller provides an HTTP method, a path, and Gherkin-formatted text describing the endpoint behavior, and receives a drafted OpenAPI path item structure in return. This is typically used in documentation generation workflows or schema-driven API development where behavioral specifications written in Gherkin need to be converted into machine-readable OpenAPI format.

## What the target does today

The tool drafts an OpenAPI 3.1 path item from the provided Gherkin text for the specified HTTP method and path. The caller must supply three required parameters: `method` (the HTTP verb), `path` (the endpoint path), and `gherkin_text` (the Gherkin-formatted scenario text describing the endpoint). The output is an OpenAPI 3.1-compliant path item representation derived from parsing and transforming the Gherkin input.

## What we want to verify

- Calling the tool with all three required parameters (`method`, `path`, `gherkin_text`) returns a response containing an OpenAPI path item structure
- The response conforms to OpenAPI 3.1 path item schema specifications
- The returned path item corresponds to the specified HTTP method
- The returned path item corresponds to the specified path
- The tool requires all three parameters; omitting any required parameter results in an error
- The Gherkin text is parsed and its content influences the structure of the drafted path item
- The tool integrates with SchemaAmbiguityGate and SchemaCoverageGate as related quality gates for the schema drafting process

## Inventory references

- Arguments:
- `method` (required): 
- `path` (required): 
- `gherkin_text` (required): 
- Related gates: SchemaAmbiguityGate.run, SchemaCoverageGate.run, run_all
- Related ADRs:
- (none directly relevant)

## Open questions

(none)

## Status

draft
