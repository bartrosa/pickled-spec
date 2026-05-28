# Story: rules_draft_ruleset_from_brief

## Metadata

- **Surface kind:** mcp_tool
- **Package:** pickled-rules
- **Surface id:** rules_draft_ruleset_from_brief

## Context

This tool is used by agents or clients within the pickled-rules package to generate a complete ruleset from a brief text description. It accepts metadata about the ruleset (short name, source identifier, what it applies to, and when it becomes active) along with the brief text, and constructs a draft ruleset structure. The tool appears in a workflow alongside coverage_gate, coverage_gate_features, and run_all gates, suggesting it participates in ruleset authoring and validation pipelines. ADR 0004 indicates this operates within a multi-ruleset workspace environment where multiple rulesets may coexist with different activation criteria.

## What the target does today

The inventory provides no docstring for this surface; behavior must be confirmed from source before specifying.

## What we want to verify

- The tool accepts exactly five required parameters: brief_text, ruleset_short_name, source_id, applies_to, and active_from
- Calling the tool with all five parameters produces a response without parameter validation errors
- The tool generates output that represents a ruleset structure (format to be confirmed from source)
- The generated ruleset incorporates the provided ruleset_short_name in its structure
- The generated ruleset incorporates the provided source_id in its structure
- The generated ruleset incorporates the provided applies_to scope in its structure
- The generated ruleset incorporates the provided active_from temporal constraint in its structure
- The generated ruleset content relates to the provided brief_text description
- Missing any required parameter results in an appropriate error
- The tool can be invoked within a multi-ruleset workspace context (per ADR 0004)

## Inventory references

- Arguments:
- `brief_text` (required): 
- `ruleset_short_name` (required): 
- `source_id` (required): 
- `applies_to` (required): 
- `active_from` (required): 
- Related gates: coverage_gate, coverage_gate_features, run_all
- Related ADRs:
- ADR 0004: Multi-ruleset workspace configuration — Accepted

## Open questions

(none)

## Status

draft
