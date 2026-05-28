# Story: mine features

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-core
- **Surface id:** pickled_core_mine_features

## Context

Developers working with pickled-core use this CLI command to draft features from user stories during stage 4 of the mined software verification pipeline. This follows ADR 0005's staged mining pipeline approach, where stories have already been generated in a previous stage and now need to be transformed into testable feature specifications.

## What the target does today

The inventory provides no docstring for this surface; behavior must be confirmed from source before specifying.

## What we want to verify

- Accepts a required `target` argument specifying what to mine
- Accepts an optional `output_dir` argument to specify where mining output should be written
- Accepts an optional `quick` flag that controls whether the command runs in quick mode (default) or uses interactive prompts
- Accepts an optional `verbose` flag to enable extra logging output to stderr
- Accepts an optional `surfaces` argument as a comma-separated filter on package name or surface-id substring
- Accepts an optional `max_parallel` argument to control maximum parallel LLM calls in quick mode for stories and features processing
- Accepts an optional `overwrite_features` flag
- Operates as part of the staged mining pipeline described in ADR 0005
- Runs as stage 4 of the mining process, specifically drafting features from previously generated stories

## Inventory references

- Arguments:
- `target` (required): 
- `output_dir` (optional): Mining output directory.
- `quick` (optional): Quick mode (default) or interactive prompts.
- `verbose` (optional): Extra logging to stderr.
- `surfaces` (optional): Comma-separated filter on package name or surface-id substring.
- `max_parallel` (optional): Max parallel LLM calls in quick mode (stories, features).
- `overwrite_features` (optional): 
- Related gates: (none)
- Related ADRs:
- ADR 0005: `pickled-spec mine` staged mining pipeline — Accepted

## Open questions

(none)

## Status

draft
