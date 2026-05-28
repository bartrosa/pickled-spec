# Story: rules_check_ruleset_coverage

## Metadata

- **Surface kind:** mcp_tool
- **Package:** pickled-rules
- **Surface id:** rules_check_ruleset_coverage

## Context

Used by MCP clients that need to verify Gherkin feature files comply with a YAML-defined rule set as part of a coverage gate. This tool replaced a previous version that accepted filesystem paths, which created a security vulnerability by allowing arbitrary file reads through parser error messages. Clients now pass feature file contents directly rather than paths.

## What the target does today

Accepts the text content of YAML rule set definitions and one or more Gherkin feature file contents, along with a short name identifier for the ruleset. Evaluates whether the provided features meet the coverage requirements defined in the YAML ruleset. This is a coverage gate check—it verifies that feature files adequately cover the rules specified in the ruleset.

The tool explicitly does NOT accept filesystem paths for security reasons (preventing arbitrary-file-read attacks via parser error messages). Feature texts must be passed as content strings.

## What we want to verify

- Accepts `ruleset_yaml_text` parameter containing YAML rule set definition content
- Accepts `feature_texts` parameter containing the text contents of one or more `.feature` files
- Accepts `ruleset_short_name` parameter as an identifier for the ruleset being checked
- Rejects or fails safely when given filesystem paths instead of file contents
- Returns coverage analysis results indicating whether features meet ruleset requirements
- Does not perform filesystem reads based on user-supplied paths
- Parses YAML ruleset definitions to extract coverage requirements
- Parses Gherkin feature file contents to extract coverage information
- Compares parsed features against ruleset requirements to determine coverage status

## Inventory references

- Arguments:
- `ruleset_yaml_text` (required): 
- `feature_texts` (required): 
- `ruleset_short_name` (required): 
- Related gates: coverage_gate, coverage_gate_features, run_all
- Related ADRs:
- ADR 0004: Multi-ruleset workspace configuration — Accepted

## Open questions

(none)

## Status

draft
