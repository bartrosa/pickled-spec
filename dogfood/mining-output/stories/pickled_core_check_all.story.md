# Story: check-all

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-core
- **Surface id:** pickled_core_check_all

## Context

Developers and CI pipelines use `check-all` as a single entry point to run all available workspace validation gates across every pickled-* package. This command provides comprehensive validation of a workspace directory structure (features/, specs/, infra/, migrations/) by executing all registered gates in one pass, supporting both strict and lenient exit-code behaviors depending on whether warnings should fail the build.

## What the target does today

Run workspace gates from every pickled-* package against a directory.

The command accepts an optional `workdir` parameter to specify the workspace root containing features/, specs/, infra/, and migrations/ directories. If not provided, the current directory is assumed.

The command accepts an optional `warn_ok` parameter that modifies exit behavior: when enabled, the process exits with code 0 (success) if only WARN-level verdicts occur, such as when optional tooling (terraform, LLM providers) is not configured. Without this flag, WARN verdicts cause non-zero exit codes.

The command discovers and executes all gates registered across all installed pickled-* packages, collecting and reporting their verdicts.

## What we want to verify

- When invoked without arguments, check-all runs against the current directory as workspace root
- When invoked with `workdir` argument, check-all runs against the specified directory
- When `warn_ok` is false or omitted, WARN verdicts cause non-zero exit code
- When `warn_ok` is true, WARN verdicts alone result in exit code 0
- The command discovers and executes gates from all installed pickled-* packages, not just pickled-core
- The command expects workspace structure containing features/, specs/, infra/, and/or migrations/ subdirectories
- Exit code 0 indicates all gates passed (or only warnings with warn_ok=true)
- Non-zero exit code indicates at least one gate failed or warned (when warn_ok=false)

## Inventory references

- Arguments:
- `workdir` (optional): Workspace root (features/, specs/, infra/, migrations/).
- `warn_ok` (optional): Exit 0 when only WARN verdicts occur (e.g. terraform or LLM not configured).
- Related gates: (none)
- Related ADRs:
- ADR 0004: Multi-ruleset workspace configuration (general) — Accepted

## Open questions

(none)

## Status

draft
