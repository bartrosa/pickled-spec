# Story: verify

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-diff
- **Surface id:** pickled_diff_verify
- **Code depth:** callgraph | **Units read:** 4 | **Unresolved:** 4

## Context

This surface is the primary CLI command for differential testing. A user invokes it to compare two programs (oracle and candidate) across a corpus of test inputs, using a specified comparison strategy. The surface is used to verify that a candidate implementation produces equivalent output to a trusted oracle across many test cases, with configurable timeout and comparison logic.

## What the target does today

**Input Validation**

The surface reads a JSON file from the `corpus` path (UTF-8 encoded) and expects a top-level list. If the parsed JSON is not a list, the surface raises a `click.ClickException` with the message "Corpus JSON must be a list of {name, payload} objects". The surface filters the list to include only dictionary entries and extracts `name` and `payload` fields, coercing both to strings. Non-dictionary entries are silently ignored.

**Command Parsing and Execution**

The `oracle` and `candidate` strings are parsed as shell-quoted command-line arguments (via `shlex.split`). Each command is wrapped in a subprocess runner with the specified `timeout_seconds`. The surface does not validate that the commands exist or are executable before attempting to run the gate.

**Comparison Strategy**

The `comparator` parameter selects a comparison strategy:
- If `comparator` equals `"structural_json"`, a structural JSON comparator is used.
- For any other value (including empty string, None, or any unrecognized value), an exact equality comparator is used.

**Differential Testing Logic**

The surface delegates the actual testing to a `DifferentialOracleGate` through its `run` method, which:
- Returns a `FAIL` verdict if the target is not a recognized corpus type.
- Returns a `PASS` verdict with explanatory notes if the corpus is empty.
- For each corpus item, runs both oracle and candidate commands with the item's payload.
- Tracks oracle errors (oracle command failures), candidate errors (candidate command failures), and mismatches (outputs differ according to the comparator).
- Oracle errors cause the item to be skipped from comparison entirely (not counted as compared).
- Candidate errors are counted as both compared items and mismatches, and generate findings.
- Accumulates findings (up to an unspecified maximum) containing input name, both outputs, and a diff summary.
- Applies verdict logic:
  - `FAIL` if all inputs caused oracle errors (with special message).
  - `WARN` if no items were successfully compared.
  - `FAIL` if all compared items mismatched.
  - `WARN` if some mismatches or oracle errors occurred.
  - `PASS` if no mismatches and no oracle errors.

**Output**

The surface writes a JSON object to stdout containing:
- `gate`: the gate name
- `verdict`: string representation of the verdict enum value
- `notes`: textual summary including mismatch counts, corpus size, and error counts
- `findings`: list of objects with `input_repr`, `oracle_output`, `candidate_output`, and `diff_summary` fields

**Exit Behavior**

The surface calls `sys.exit` with:
- Exit code 0 for `PASS` verdict
- Exit code 1 for `WARN` verdict
- Exit code 2 for `FAIL` verdict

**Unresolved Behavior**

- The actual command execution (how subprocess runners handle timeouts, capture output, detect errors) is delegated to unresolved collaborators.
- The comparison logic (what "equal" means for each comparator, what diff summaries look like) is delegated to unresolved comparator implementations.
- The maximum number of findings collected is determined by an unresolved gate configuration parameter.

## What we want to verify

- Parse a corpus JSON file that is not a list and observe a `click.ClickException` with message containing "must be a list"
- Parse a corpus JSON containing `[{"name": "a", "payload": "b"}]` and verify both commands receive payload "b"
- Parse a corpus JSON containing `[{"name": 1, "payload": 2}]` and verify name and payload are coerced to strings "1" and "2"
- Parse a corpus JSON containing `[{"name": "x", "payload": "y"}, "not-a-dict", {"name": "z", "payload": "w"}]` and verify only the two dictionary entries are processed
- Invoke with `comparator="structural_json"` and verify a structural JSON comparator is selected
- Invoke with `comparator="exact"` (or any non-"structural_json" value) and verify an exact equality comparator is selected
- Provide an empty corpus list and verify exit code 0 (PASS) with notes mentioning "empty"
- Mock all items to produce oracle errors and verify exit code 2 (FAIL) with notes mentioning "Oracle failed on every input"
- Mock some compared items to mismatch and verify exit code 1 (WARN)
- Mock all compared items to mismatch and verify exit code 2 (FAIL)
- Mock all items to pass comparison and verify exit code 0 (PASS) with "0/N mismatches" in notes
- Verify JSON output contains keys `gate`, `verdict`, `notes`, and `findings`
- Verify each finding in JSON output contains `input_repr`, `oracle_output`, `candidate_output`, and `diff_summary`
- Parse a corpus JSON missing `name` or `payload` keys and observe a KeyError (no default handling)

## Inventory references

- Arguments:
- `oracle` (required): Reference command (shell-quoted argv).
- `candidate` (required): Candidate command (shell-quoted argv).
- `corpus` (required): JSON file: [{"name": "...", "payload": "..."}, ...]
- `comparator` (optional): 
- `timeout_seconds` (optional): 
- Related gates: run_all
- Related ADRs:
- ADR 0001: pickled-diff package — Proposed

## Open questions

- Docstring drift: The docstring states "Compare candidate vs reference" but does not mention: (1) the corpus must be a JSON list of specific shape, (2) the surface exits with specific codes based on verdict, (3) the surface outputs JSON to stdout, (4) non-dictionary corpus entries are silently filtered, (5) the comparator parameter exists and controls comparison strategy, (6) timeout behavior is configurable, (7) oracle errors cause items to be skipped rather than compared.
- Docstring drift: The docstring does not describe any error conditions, but the code raises `click.ClickException` for invalid corpus format.
- Docstring drift: The docstring does not mention the return value or exit behavior; the code calls `sys.exit` and functionally returns nothing (`-> None` is misleading since execution terminates).

## Status

draft
