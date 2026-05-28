# Story: mine code

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-core
- **Surface id:** pickled_core_mine_code

## Context

The `mine code` CLI command is used by developers and automation systems to extract source code context from software projects for documentation, analysis, or AI-assisted development workflows. It operates on a target codebase to collect surface definitions (functions, classes, CLI commands) along with their implementation details and call graphs. Users invoke this command to build an inventory of code surfaces with configurable depth and scope, which can then be consumed by downstream tools or LLM-based verification systems.

## What the target does today

The inventory provides no docstring for this surface; behavior must be confirmed from source before specifying.

## What we want to verify

- **Required target argument**: Command fails gracefully when invoked without the `target` argument.
- **Output directory handling**: When `output_dir` is specified, mining results are written to that directory; when omitted, a default output location is used.
- **Verbose logging**: When `verbose` flag is enabled, additional diagnostic information is written to stderr during mining operations.
- **Surface filtering**: When `surfaces` is provided with package name or surface-id substrings, only matching surfaces are included in the output.
- **Depth control**: The `depth` parameter controls how much source code context is collected for each surface (e.g., imports, dependencies, implementation).
- **Callee scope**: The `callee_scope` parameter determines which intra-project function/method calls are followed during analysis.
- **Hop limiting**: The `max_hops` parameter caps the depth of callee expansion in the call graph traversal.
- **Callee count limiting**: The `max_callees` parameter enforces a hard limit on the number of callee units collected per surface.
- **Line count limiting**: The `max_code_lines` parameter enforces a hard limit on total source lines collected per surface.
- **Cycle detection**: When `detect_cycles` is enabled, a `code-context/_cycles.json` file is written containing detected circular dependencies from call graph edges.
- **Exit code**: Command exits with 0 on successful mining, non-zero on errors.
- **File output**: Mining produces structured output files (likely JSON) containing surface metadata, source code, and call graph information.

## Inventory references

- Arguments:
- `target` (required): 
- `output_dir` (optional): Mining output directory.
- `verbose` (optional): Extra logging to stderr.
- `surfaces` (optional): Comma-separated filter on package name or surface-id substring.
- `depth` (optional): How much source to collect per surface.
- `callee_scope` (optional): Which intra-project callees to follow.
- `max_hops` (optional): Callee expansion depth (callgraph only).
- `max_callees` (optional): Hard cap on collected callee units per surface.
- `max_code_lines` (optional): Hard cap on total source lines per surface.
- `detect_cycles` (optional): Write code-context/_cycles.json from observed edges.
- Related gates: (none)
- Related ADRs:
- ADR 0004: Multi-ruleset workspace configuration (general) — Accepted

## Open questions

(none)

## Status

draft
