# Story: mine inventory

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-core
- **Surface id:** pickled_core_mine_inventory

## Context

The `mine inventory` command is invoked by developers, test engineers, or CI pipelines in the first stage of the pickled-spec mining pipeline (ADR 0005). It introspects a target project and produces an inventory.json file that catalogs discovered specifications, features, or test scenarios before subsequent mining stages process them further.

## What the target does today

Stage 1: introspect target and write inventory.json.

The command accepts a required `target` argument and optional parameters controlling output location (`output_dir`), verbosity (`verbose`), interaction mode (`quick`), MCP tool discovery (`no_mcp`, `mcp_timeout`).

## What we want to verify

- When invoked with a valid `target`, the command completes without error.
- An `inventory.json` file is created in the specified `output_dir` (or default location if not provided).
- The `inventory.json` file contains valid JSON and represents introspected elements from the target.
- Passing `--verbose` produces additional logging output to stderr.
- Passing `--no_mcp` skips any MCP tools/list operations.
- Passing `--quick` runs without interactive prompts (default behavior).
- The command fails with a clear error message if `target` is missing or invalid.

## Inventory references

- Arguments:
- `target` (required): 
- `output_dir` (optional): Mining output directory.
- `quick` (optional): Quick mode (default) or interactive prompts.
- `verbose` (optional): Extra logging to stderr.
- `no_mcp` (optional): Skip MCP tools/list.
- `mcp_timeout` (optional): 
- Related gates: (none)
- Related ADRs:
- ADR 0005: `pickled-spec mine` staged mining pipeline — Accepted
- ADR 0006: `pickled-spec mine code` static code reading — Accepted
- ADR 0007: Code-aware stories and docstring drift detection — Accepted

## Open questions

(none)

## Status

draft
