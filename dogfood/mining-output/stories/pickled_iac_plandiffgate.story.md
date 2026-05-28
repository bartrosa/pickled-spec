# Story: PlanDiffGate.run

## Metadata

- **Surface kind:** gate
- **Package:** pickled-iac
- **Surface id:** pickled_iac_plandiffgate
- **Code depth:** callgraph | **Units read:** 2 | **Unresolved:** 0

## Context

This gate is used in infrastructure-as-code (IaC) pipelines to compare two Terraform plan JSON outputs (base vs. head) and determine whether the detected changes should pass, warn, or fail based on the type of actions involved. Callers provide the head plan as the `target` and the base plan via the `context` dictionary under the key "base_plan". The gate helps enforce safety policies by flagging destructive changes (delete, replace) as failures and non-destructive changes (create, update, read, no-op) as warnings.

## What the target does today

**Inputs:**
- `target`: Expected to be a dict representing the head Terraform plan JSON. If not a dict, the gate immediately fails.
- `context`: Optional dict that must contain a "base_plan" key with a dict value representing the base Terraform plan JSON. If absent, None, or not a dict, the gate fails.

**Processing:**
The gate extracts resource change information from both plans by looking for a top-level "resource_changes" key (expected to be a list). For each resource change entry (which must be a dict), it reads:
- "address": the resource address (coerced to string)
- "change.actions": a list of action strings

Non-dict entries in "resource_changes" are silently skipped. Missing or null "resource_changes", "change", or "actions" fields are tolerated (treated as empty).

The gate then compares changes between base and head:
- Resources present in head but not in base (and having non-empty actions) are recorded as findings with empty base actions.
- Resources present in both plans with different action lists are recorded as findings.
- Resources only in base (not in head) are ignored.

**Verdict logic:**
- If no findings exist AND no actions are detected across all head changes, verdict is PASS with notes "No plan changes between base and head."
- If any action is "delete" or "replace", verdict is FAIL.
- If all detected actions are in the set {"create", "update", "read", "no-op"}, verdict is WARN.
- Otherwise (any action outside the above sets), verdict is WARN.

**Outputs:**
Returns a `GateResult` with:
- `gate_name`: the name of this gate instance
- `verdict`: one of PASS, WARN, or FAIL
- `findings`: a tuple of `PlanDiffFinding` objects (empty for PASS cases), each containing (address, base_actions_tuple, head_actions_tuple)
- `notes`: either an error message (for input validation failures), "No plan changes between base and head." (for PASS), or "{count} resource change(s) detected." (for WARN/FAIL)

**Edge cases:**
- If "resource_changes" is missing, null, or not a list, it is treated as an empty list.
- If "change" is missing or not a dict, actions default to empty.
- If "actions" is missing or not a list, it is treated as empty.
- All actions are coerced to strings.
- The gate does not validate that action strings are valid Terraform actions.

## What we want to verify

- When `target` is not a dict, return FAIL verdict with notes indicating the actual type received
- When `context` is None or missing "base_plan" key, return FAIL verdict with notes about missing base_plan
- When "base_plan" in context is not a dict, return FAIL verdict
- When both plans have empty or missing "resource_changes", return PASS verdict with notes "No plan changes between base and head."
- When head plan contains a resource address not in base plan with non-empty actions, include a finding with empty base actions tuple
- When head plan contains a resource with different actions than base plan, include a finding showing both action tuples
- When resource exists only in base but not in head, do not generate any finding for that resource
- When any action in head changes is "delete" or "replace", return FAIL verdict
- When all actions in head changes are from {"create", "update", "read", "no-op"}, return WARN verdict
- When findings exist, notes should state "{count} resource change(s) detected." where count matches the findings length
- When "resource_changes" contains non-dict entries, skip those entries without error
- When "change" is missing or null, treat actions as empty list
- When "actions" is not a list, treat it as empty
- All action strings in findings are converted to tuples in the order they appear in the source lists

## Inventory references

- Arguments:
- (gate class)
- Related gates: PlanDiffGate.run
- Related ADRs:
- (none directly relevant)

## Open questions

- Docstring drift: The docstring states "Compare two terraform plan JSON outputs" but does not describe the return value shape (GateResult with verdict, findings, notes), the specific verdict rules (FAIL for delete/replace, WARN for safe changes), or the input validation behavior (type checking and required context key)
- Docstring drift: The docstring does not mention that resources present only in base (but not in head) are ignored in the comparison
- Docstring drift: The docstring does not specify that the base plan must be passed via context dict with key "base_plan" rather than as a direct parameter

## Status

draft
