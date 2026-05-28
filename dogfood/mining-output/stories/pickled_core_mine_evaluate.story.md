# Story: mine evaluate

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-core
- **Surface id:** pickled_core_mine_evaluate

## Context

Engineers and CI pipelines use `mine evaluate` after earlier mining stages have run. It is stage 6 of the pickled-core mining pipeline (per ADR 0005), invoked to check whether mined surfaces meet coverage and ambiguity quality gates before finalizing the mining output. The command is typically run against a target codebase after surfaces have been extracted, and its pass/fail result determines whether the mined inventory is acceptable for downstream use.

## What the target does today

Stage 6: evaluate coverage and ambiguity gates.

The command accepts a required `target` argument (the codebase being mined), an optional `output_dir` for mining artifacts, optional `verbose` flag for stderr logging, an optional `surfaces` filter to restrict evaluation to specific packages or surface IDs, and optional `ruleset_dir` and `ruleset_config` parameters to configure gate behavior. It evaluates the mined surfaces against configured coverage and ambiguity gates and reports gate pass/fail status.

## What we want to verify

- Invoking `mine evaluate <target>` without prior mining stages fails or reports missing prerequisite data.
- When all configured gates pass, the command exits with status 0.
- When any gate fails, the command exits with a non-zero status.
- The `--surfaces` filter restricts gate evaluation to only matching package names or surface IDs.
- The `--verbose` flag produces additional diagnostic output to stderr during evaluation.
- The `--output_dir` argument changes where the command reads mined artifacts and writes evaluation results.
- Coverage gate evaluation measures the percentage or count of surfaces meeting documentation or verification thresholds.
- Ambiguity gate evaluation detects conflicting or overlapping surface definitions.
- Gate results are written to the output directory in a structured format (JSON or similar).
- Running `mine evaluate` multiple times with the same inputs produces the same gate results (idempotent).

## Inventory references

- Arguments:
- `target` (required): 
- `output_dir` (optional): Mining output directory.
- `verbose` (optional): Extra logging to stderr.
- `surfaces` (optional): Comma-separated filter on package name or surface-id substring.
- `ruleset_dir` (optional): 
- `ruleset_config` (optional): 
- Related gates: (none)
- Related ADRs:
- ADR 0005: `pickled-spec mine` staged mining pipeline — Accepted

## Open questions

(none)

## Status

draft
