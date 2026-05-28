# Story: mine tag

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-core
- **Surface id:** pickled_core_mine_tag

## Context

Developers and automation pipelines use this command during the fifth stage of the pickled-core workflow to tag scenarios within generated feature files. This follows earlier mining stages and prepares features for downstream processing. The command is part of a multi-stage feature generation pipeline where tagging scenarios helps organize, categorize, or filter test cases.

## What the target does today

Stage 5: tag scenarios in generated features.

The command processes previously generated feature files and applies tags to scenarios. It operates on a specified target and can filter which surfaces are processed. It supports both quick (non-interactive) and interactive modes for tagging operations. Output is written to a configured mining directory, and verbosity can be increased for debugging. Multiple rulesets can be configured via ruleset directory and config parameters, consistent with ADR 0004's multi-ruleset workspace configuration support.

## What we want to verify

- `mine tag` with a valid target processes feature files and tags scenarios within them
- The `--output-dir` parameter, when provided, determines where tagged features are written
- The `--quick` flag (default true) runs without interactive prompts; when false, enables interactive mode
- The `--verbose` flag increases logging output to stderr when enabled
- The `--surfaces` parameter filters processing to only surfaces matching the comma-separated package name or surface-id substrings
- The `--ruleset-dir` parameter specifies the directory containing ruleset definitions
- The `--ruleset-config` parameter specifies ruleset configuration consistent with ADR 0004
- The command fails with an appropriate error when the target parameter is missing
- The command operates as stage 5 in a sequential mining pipeline, expecting prior stages to have generated features

## Inventory references

- Arguments:
- `target` (required): 
- `output_dir` (optional): Mining output directory.
- `quick` (optional): Quick mode (default) or interactive prompts.
- `verbose` (optional): Extra logging to stderr.
- `surfaces` (optional): Comma-separated filter on package name or surface-id substring.
- `ruleset_dir` (optional): 
- `ruleset_config` (optional): 
- Related gates: (none)
- Related ADRs:
- ADR 0004: Multi-ruleset workspace configuration (general) — Accepted

## Open questions

(none)

## Status

draft
