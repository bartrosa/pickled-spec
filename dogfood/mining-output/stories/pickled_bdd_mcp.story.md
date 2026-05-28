# Story: mcp

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-bdd
- **Surface id:** pickled_bdd_mcp
- **Code depth:** callgraph | **Units read:** 1 | **Unresolved:** 0

## Context

This is a CLI command entry point that serves as a parent group for MCP (Model Context Protocol) server-related subcommands. It is invoked directly by CLI users or by the Click framework when users run commands like `pickled-bdd mcp <subcommand>`. The surface provides organizational structure for MCP server operations within the pickled-bdd tool.

## What the target does today

The surface is a parameterless function that serves as a Click command group entry point. When invoked:

- Accepts no arguments or parameters
- Returns None
- Produces no observable side effects on its own (no file I/O, no state mutation, no output)
- Acts as a namespace/container for subcommands in the CLI hierarchy
- Expects to be decorated with Click's `@group` or similar decorator to provide actual CLI functionality (the function body is empty, suggesting decorator-driven behavior)

The surface does not perform validation, does not raise exceptions, and does not interact with any external systems. Its behavioral contract is essentially a no-op that delegates all actual functionality to the CLI framework's decorator system and any registered subcommands.

## What we want to verify

- Calling `mcp()` directly completes without raising exceptions
- Calling `mcp()` returns None
- Calling `mcp()` produces no console output
- Calling `mcp()` does not modify any global state
- Calling `mcp()` does not perform file system operations
- Calling `mcp()` does not make network calls
- The function signature accepts zero parameters

## Inventory references

- Arguments:
- (none)
- Related gates: AmbiguityGate.run, run_all
- Related ADRs:
- (none directly relevant)

## Open questions

- Docstring drift: The docstring claims "MCP server commands" (plural, suggesting multiple operations), but the function body is empty and performs no operations itself; the actual commands would be implemented as subcommands registered to this group, which is not reflected in the docstring

## Status

draft
