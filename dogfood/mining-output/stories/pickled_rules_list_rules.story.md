# Story: list-rules

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-rules
- **Surface id:** pickled_rules_list_rules

## Context

CLI users invoking `pickled-rules list-rules` to discover available rule identifiers from either a built-in rule set or a custom YAML file. This supports workflows where users need to reference specific rules by ID for filtering, reporting, or configuration purposes. The command accepts either a named built-in rule set or a file system path to a YAML rule set.

## What the target does today

Lists rule IDs from a YAML rule set. The command accepts a `ruleset` argument that can be either a built-in rule set name or a path to a YAML rule set file, and outputs the rule identifiers contained within that rule set.

## What we want to verify

- Invoked with a built-in rule set name, the command outputs rule IDs from that built-in set
- Invoked with a valid file path to a YAML rule set, the command outputs rule IDs from that file
- The output consists of rule IDs extracted from the specified rule set
- Invalid or non-existent rule set names/paths produce an appropriate error
- The command completes successfully (exit code 0) when given valid input

## Inventory references

- Arguments:
- `ruleset` (required): Built-in rule set name or path to a YAML rule set file.
- Related gates: coverage_gate, coverage_gate_features, run_all
- Related ADRs:
- (none directly relevant)

## Open questions

(none)

## Status

draft
