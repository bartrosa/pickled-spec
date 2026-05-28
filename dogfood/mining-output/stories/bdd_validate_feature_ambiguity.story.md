# Story: bdd_validate_feature_ambiguity

## Metadata

- **Surface kind:** mcp_tool
- **Package:** pickled-bdd
- **Surface id:** bdd_validate_feature_ambiguity

## Context

This tool is used by BDD practitioners and test automation engineers who need to validate Gherkin feature files for ambiguous step definitions before running tests. It serves as a quality gate in the BDD workflow to catch ambiguity issues early—particularly valuable when integrating feature files into CI/CD pipelines or when reviewing feature specifications. The tool connects to the `pickled-bdd` package's ambiguity detection capabilities, specifically wrapping `AmbiguityGate.run` for use as an MCP tool.

## What the target does today

Run the ambiguity gate against a Gherkin .feature file.

The tool accepts feature file text as input via the `feature_text` parameter (required) and executes ambiguity validation through the underlying `AmbiguityGate.run` gate. The gate is one of several available validation gates (alongside `run_all`), suggesting a modular validation architecture where different quality checks can be run independently or together.

## What we want to verify

- Accepts `feature_text` parameter containing Gherkin feature file content
- Invokes `AmbiguityGate.run` with the provided feature text
- Returns validation results indicating whether ambiguities were detected
- Handles malformed or invalid Gherkin syntax appropriately
- Can be invoked as an MCP tool within the pickled-bdd toolchain
- Functions independently of other gates (does not require `run_all` to operate)

## Inventory references

- Arguments:
- `feature_text` (required): 
- Related gates: AmbiguityGate.run, run_all
- Related ADRs:
- ADR 0005: `pickled-spec mine` staged mining pipeline — Accepted
- ADR 0007: Code-aware stories and docstring drift detection — Accepted

## Open questions

(none)

## Status

draft
