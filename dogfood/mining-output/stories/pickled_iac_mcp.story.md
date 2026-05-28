# Story: mcp

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-iac
- **Surface id:** pickled_iac_mcp
- **Code depth:** callgraph | **Units read:** 1 | **Unresolved:** 0

## Context

This is a CLI command group entry point for MCP (Model Context Protocol) server-related commands in the pickled-iac package. It serves as a parent command under which subcommands for MCP server operations are grouped. Callers are typically CLI users or the Click framework invoking this command from the command-line interface. Related surfaces include IaCAmbiguityGate.run, PlanDiffGate.run, SecurityBaselineGate.run, and run_all, suggesting this command group may organize gates or server operations under the MCP namespace.

## What the target does today

The surface is a no-op command group that accepts no parameters and produces no direct output or side effects. When invoked, it simply returns None. This command serves purely as a Click command group container; its purpose is to organize subcommands under the "mcp" namespace rather than to perform any action itself. 

If invoked directly without subcommands (assuming Click's default group behavior), the caller would observe either help text display or an error indicating that a subcommand is required, depending on Click's configuration. The function body itself performs no validation, raises no exceptions, and initiates no side effects.

## What we want to verify

- When invoked programmatically, the function returns None
- The function accepts no arguments
- The function raises no exceptions when called
- The function performs no file I/O, network operations, or state mutations
- The function executes and completes immediately without blocking
- When used as a Click command group, it organizes subcommands under the "mcp" namespace

## Inventory references

- Arguments:
- (none)
- Related gates: IaCAmbiguityGate.run, PlanDiffGate.run, SecurityBaselineGate.run, run_all
- Related ADRs:
- (none directly relevant)

## Open questions

- Docstring drift: The docstring states "MCP server commands" (plural) but the code implements only an empty container function with no commands, operations, or delegation to any server functionality; the actual server commands must be registered elsewhere as subcommands not visible in this surface

## Status

draft
