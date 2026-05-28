# Story: rules_list_rules

## Metadata

- **Surface kind:** mcp_tool
- **Package:** pickled-rules
- **Surface id:** rules_list_rules

## Context

Test automation and CI/CD pipelines that need to inspect or validate the structure and content of YAML-based rule sets before executing them. Used by developers and quality gates to understand what rules are defined in a rule set without running the full rule execution logic.

## What the target does today

The inventory provides no docstring for this surface; behavior must be confirmed from source before specifying.

## What we want to verify

- Accept a `ruleset_yaml_text` parameter containing YAML rule set content
- Parse the YAML content to extract rule definitions
- Return a list or collection of rule summaries
- Handle invalid or malformed YAML input without crashing
- Return an empty or null result when the YAML contains no rules
- Extract identifying information from each rule (minimally rule names/identifiers)
- Preserve the order of rules as they appear in the YAML if order is meaningful
- Support the YAML schema expected by the pickled-rules package
- Function as an MCP tool interface, returning results in MCP-compatible format

## Inventory references

- Arguments:
- `ruleset_yaml_text` (required): 
- Related gates: coverage_gate, coverage_gate_features, run_all
- Related ADRs:
- (none directly relevant)

## Open questions

(none)

## Status

draft
