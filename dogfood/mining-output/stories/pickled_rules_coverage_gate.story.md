# Story: coverage_gate

## Metadata

- **Surface kind:** gate
- **Package:** pickled-rules
- **Surface id:** pickled_rules_coverage_gate
- **Code depth:** callgraph | **Units read:** 3 | **Unresolved:** 0

## Context

This gate is used by test automation or compliance tooling to verify that a Gherkin feature file adequately covers the rules defined in a ruleset. Callers provide a single Feature and a RuleSet, along with a short name used to identify rule references in scenario tags. The gate determines whether all strict rules are referenced by at least one scenario and whether any unknown rule references exist. It produces a coverage report that includes both the gate verdict and traceability information for documentation or audit purposes.

## What the target does today

**Inputs accepted:**
- `feature`: a Feature object representing a Gherkin feature file
- `ruleset`: a RuleSet object containing zero or more rules, each with an `id`, `enforcement` level (e.g., "strict", "advisory", "informational"), and other metadata
- `ruleset_short_name` (keyword-only): a string used to match scenario tags in the format `<ruleset_short_name>:<rule_id>`

**Return value:**
Returns a `CoverageReport` object containing:
- `referenced_rules`: tuple of rules from the ruleset that were referenced by at least one scenario tag
- `unreferenced_rules`: tuple of rules from the ruleset that were not referenced by any scenario tag
- `unknown_references`: sorted tuple of (ruleset_name, rule_id) pairs for tags that reference rule IDs not found in the provided ruleset
- `gate_result`: a `GateResult` with:
  - `gate_name`: always "rules.coverage"
  - `verdict`: `Verdict.PASS` if all strict rules are referenced AND no unknown references exist; otherwise `Verdict.FAIL`
  - `findings`: always an empty tuple
  - `notes`: a human-readable string describing the pass/fail reason
  - `traces`: tuple of `Trace` objects, one per referenced rule, indicating that the feature "implements" each referenced rule with "asserted" confidence

**Reference extraction:**
- Scenario tags are extracted from the feature and filtered to those matching the `ruleset_short_name`
- Tags are normalized (the "@" prefix is removed during parsing/modeling, as mentioned in the docstring)
- A rule is considered "referenced" if its `id` appears in at least one matching tag

**Pass/fail logic:**
- The gate passes if and only if:
  1. Every rule with `enforcement == "strict"` is referenced by at least one scenario, AND
  2. No scenario tags reference rule IDs that do not exist in the ruleset (no unknown references)
- Advisory and informational rules may remain unreferenced without causing failure
- If any strict rule is unreferenced OR any unknown references exist, the gate fails

**Artifact reference in traces:**
- If the feature has a `path` attribute that is truthy, that path is used as the `artifact_ref` in all generated traces
- If the feature has no path or the path is falsy, the string `"<feature>"` is used instead

**Notes content:**
- On pass: states that all strict rules are referenced and no unknown tags exist
- On fail: enumerates the count of unreferenced strict rules and/or unknown references

**No exceptions or validation:**
The surface does not perform validation on inputs (e.g., checking for None, validating ruleset structure, or ensuring ruleset_short_name is non-empty). Invalid inputs would propagate as exceptions from delegated calls.

## What we want to verify

- When feature contains no scenarios, the gate returns a CoverageReport with empty referenced_rules, all rules in unreferenced_rules, and verdict FAIL if any rule has enforcement="strict"
- When all strict rules are referenced by scenario tags and no unknown references exist, the gate returns verdict PASS
- When at least one strict rule is unreferenced, the gate returns verdict FAIL regardless of whether advisory or informational rules are referenced
- When scenario tags reference rule IDs not present in the ruleset, the gate returns verdict FAIL and includes those references in unknown_references as sorted tuples
- When only advisory or informational rules are unreferenced and no unknown references exist, the gate returns verdict PASS
- The returned CoverageReport.gate_result.gate_name is always "rules.coverage"
- The returned CoverageReport.gate_result.findings is always an empty tuple
- Each rule appearing in referenced_rules has a corresponding Trace in gate_result.traces with relation="implements" and confidence="asserted"
- When feature.path is None or empty, the artifact_ref in all traces is "<feature>"
- When feature.path is truthy, the artifact_ref in all traces equals feature.path
- The notes field on pass states all strict rules are referenced and no unknown tags exist
- The notes field on fail includes the count of unreferenced strict rules if any exist
- The notes field on fail includes the count of unknown references if any exist
- The unknown_references tuple is sorted
- A rule is counted as referenced if it appears in any scenario tag with the pattern <ruleset_short_name>:<rule_id>

## Inventory references

- Arguments:
- (gate class)
- Related gates: coverage_gate
- Related ADRs:
- ADR 0004: Multi-ruleset workspace configuration — Accepted

## Open questions

- Docstring drift: The docstring states "normalized without `@` in the model" but does not explain where this normalization occurs; the code delegates tag extraction to `extract_references`, so the normalization behavior is not observable in the shown surface
- Docstring drift: The docstring does not mention that the gate will fail if unknown reference tags exist; it only describes the strict rule coverage requirement for passing

## Status

draft
