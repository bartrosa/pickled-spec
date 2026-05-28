# Story: mine all

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-core
- **Surface id:** pickled_core_mine_all

## Context

The "mine all" CLI command is the top-level orchestrator for the pickled-core mining pipeline. It is invoked by users (developers, QA engineers, or automated CI/CD processes) who want to extract software surfaces from a target codebase, generate human-readable stories and Gherkin features, apply tagging rules, evaluate quality, and produce a final report—all in a single command. This is the primary entry point for a complete end-to-end mining workflow, as opposed to running individual pipeline stages separately.

## What the target does today

Run inventory → code → stories → features → tag → evaluate → report.

The command accepts a required `target` parameter (presumably a path or identifier for the codebase to mine) and an optional `output_dir` for where mining artifacts are written. It operates in `quick` mode by default (non-interactive) but can prompt interactively if disabled. Verbosity, surface filtering by package or surface-id substring, and parallelism control for LLM calls during story and feature generation are configurable. Advanced code-collection parameters include `depth`, `callee_scope`, `max_hops`, `max_callees`, and `max_code_lines` to control how much source context is gathered per surface. Optional flags control MCP behavior (`no_mcp`, `mcp_timeout`), ruleset location (`ruleset_dir`, `ruleset_config`), story/feature overwrite policy, and cycle detection in the call graph (`detect_cycles`). The command chains the seven named stages in sequence, passing intermediate artifacts between them.

## What we want to verify

- Invoking "mine all" with a valid `target` runs all seven stages (inventory, code, stories, features, tag, evaluate, report) in the documented order.
- Omitting `target` raises an error indicating the parameter is required.
- Specifying `--output_dir <path>` writes all mining artifacts to `<path>`.
- Passing `--verbose` increases logging detail to stderr.
- Using `--surfaces <filter>` restricts processing to surfaces whose package name or surface-id contains the specified substring.
- Setting `--max_parallel <N>` limits concurrent LLM calls during story and feature generation to N.
- Providing `--ruleset_dir <path>` and/or `--ruleset_config <file>` configures which tagging rulesets are applied.
- Flags `--overwrite_stories` and `--overwrite_features` control whether existing story or feature files are replaced on re-run.
- Code-collection parameters (`--depth`, `--callee_scope`, `--max_hops`, `--max_callees`, `--max_code_lines`) affect the volume and scope of source context extracted per surface.
- Setting `--detect_cycles` generates a `code-context/_cycles.json` file when call-graph cycles are detected.
- The command exits with a non-zero status if any stage fails.
- Running in non-quick mode (when `--quick` is false or omitted and defaults permit) prompts the user for confirmation at interactive decision points.

## Inventory references

- Arguments:
- `target` (required): 
- `output_dir` (optional): Mining output directory.
- `quick` (optional): Quick mode (default) or interactive prompts.
- `verbose` (optional): Extra logging to stderr.
- `surfaces` (optional): Comma-separated filter on package name or surface-id substring.
- `max_parallel` (optional): Max parallel LLM calls in quick mode (stories, features).
- `no_mcp` (optional): 
- `mcp_timeout` (optional): 
- `ruleset_dir` (optional): 
- `ruleset_config` (optional): 
- `overwrite_stories` (optional): 
- `overwrite_features` (optional): 
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
