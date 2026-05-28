# Story: diff

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-iac
- **Surface id:** pickled_iac_diff
- **Code depth:** callgraph | **Units read:** 3 | **Unresolved:** 0

## Context

This CLI command is invoked by users (or automation) who want to compare two Terraform plan JSON files to understand what infrastructure changes differ between them. Typical use cases include CI/CD pipelines that validate plan changes between a baseline (e.g., main branch) and a proposed change (e.g., pull request), or operators manually auditing infrastructure drift.

## What the target does today

**Inputs:**
- Accepts two required arguments: `base_path` and `head_path`, both of type `Path`
- Expects both paths to point to files containing valid UTF-8 encoded JSON representing Terraform plan files
- The JSON files must be dictionaries containing a top-level `resource_changes` key (optional or null) with a list of resource change objects

**Core operation:**
- Reads and parses both JSON files from disk
- Compares the resource changes between base and head plans by:
  - Indexing changes by resource address and action type from the `resource_changes` array in each plan
  - Each resource change must be a dict with an `address` field and a `change` field containing an `actions` list
  - Identifying resources that have different actions between base and head, or appear only in head
  - Ignoring resources that appear only in base

**Outputs to stdout:**
- Emits a JSON object with the following structure:
  - `verdict`: string value from enumeration ("PASS", "WARN", or "FAIL")
  - `notes`: string describing the outcome
  - `findings`: array of objects, each with:
    - `address`: string resource address
    - `actions_before`: list of action strings from base plan
    - `actions_after`: list of action strings from head plan

**Exit behavior:**
- Exits with status 0 if verdict is PASS (no changes detected between plans)
- Exits with status 1 if verdict is WARN (only safe actions: create, update, read, no-op detected)
- Exits with status 2 if verdict is FAIL (destructive actions like delete or replace detected, or invalid input)
- Exits with status 2 if either plan is not a dictionary
- Exits with status 2 if `base_plan` is missing or not a dictionary in context

**Verdict logic:**
- PASS: No resource changes detected between base and head
- FAIL: Any action is "delete" or "replace"
- WARN: All actions are from the set {create, update, read, no-op}
- WARN: Default if actions exist but don't match the FAIL or safe-only criteria

**Error modes:**
- If file reading fails (missing file, permission denied, encoding errors), an exception propagates uncaught
- If JSON parsing fails in either file, an exception propagates uncaught
- Non-dict resource change entries in the `resource_changes` array are silently skipped
- Missing or non-dict `change` fields are handled gracefully (treated as no actions)
- Non-list `actions` values are handled gracefully (treated as no actions)
- Empty or missing `address` fields default to empty string

## What we want to verify

- When both plans contain identical resource changes, exits with status 0 and verdict "PASS"
- When both plans are empty (no resource_changes), exits with status 0 and verdict "PASS"
- When head plan contains a new resource with create action not in base, exits with status 1 and verdict "WARN"
- When head plan contains a resource with delete action, exits with status 2 and verdict "FAIL"
- When head plan contains a resource with replace action, exits with status 2 and verdict "FAIL"
- When a resource has different actions between base and head, it appears in findings with both actions_before and actions_after populated
- When a resource appears only in head (not in base) with non-empty actions, it appears in findings with empty actions_before
- When base_path or head_path does not exist, raises an exception (file not found)
- When either file contains invalid JSON, raises a JSON decode exception
- When head plan is not a dictionary, exits with status 2 and verdict "FAIL" with appropriate notes
- The stdout output is valid JSON with exactly the keys: verdict, notes, findings
- Each finding in the output contains exactly the keys: address, actions_before, actions_after
- Resources appearing only in base plan (removed in head) do not generate findings
- Non-dictionary entries in resource_changes arrays are silently ignored
- When all actions are from {create, update, read, no-op}, exits with status 1 and verdict "WARN"

## Inventory references

- Arguments:
- `base_path` (required): 
- `head_path` (required): 
- Related gates: IaCAmbiguityGate.run, PlanDiffGate.run, SecurityBaselineGate.run, run_all
- Related ADRs:
- (none directly relevant)

## Open questions

- Docstring drift: The docstring states "Compare two terraform plan JSON files" but omits several observable behaviors:
- Docstring drift: Does not mention it writes JSON-formatted comparison results to stdout
- Docstring drift: Does not mention the three distinct exit codes (0, 1, 2) based on verdict
- Docstring drift: Does not mention the specific verdict logic (FAIL for delete/replace, WARN for safe changes, PASS for no changes)
- Docstring drift: Does not mention the specific output schema with verdict, notes, and findings fields
- Docstring drift: Does not mention error handling behavior (uncaught exceptions for file/JSON errors vs. graceful handling of malformed resource entries)

## Status

draft
