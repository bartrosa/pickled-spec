# Story: coverage_gate_features

## Metadata

- **Surface kind:** gate
- **Package:** pickled-rules
- **Surface id:** pickled_rules_coverage_gate_features
- **Code depth:** callgraph | **Units read:** 4 | **Unresolved:** 2

## Context

`coverage_gate_features` is a gate function used to verify that a set of Gherkin feature files references all strict rules from a given ruleset. It extracts reference tags (e.g., `@REF:ruleset:rule-id`) from scenario tags across one or more features and compares them against the ruleset. It returns a coverage report with a pass/fail verdict, referenced/unreferenced rule lists, and traceability information. Callers use this to enforce that all mandatory (strict enforcement) rules have corresponding test scenarios in the feature suite.

## What the target does today

**Inputs:**
- `features`: A sequence of Feature objects to scan for rule references in their scenario tags
- `ruleset`: A RuleSet object containing rules with `id`, `enforcement`, and `description` attributes; must provide a `find(rule_id: str)` method that returns a Rule or None
- `ruleset_short_name`: A string filter used to match reference tags (case-insensitive on the ruleset side)
- `artifact_ref` (optional): A string identifying the artifact(s) being checked; defaults to a comma-separated list of feature paths or `"<features>"` if no paths are available

**Returns:**
A `CoverageReport` object containing:
- `referenced_rules`: A tuple of Rule objects from the ruleset that are referenced in the feature scenarios
- `unreferenced_rules`: A tuple of Rule objects from the ruleset that are not referenced
- `unknown_references`: A sorted tuple of (ruleset_name, rule_id) pairs for tags that do not match any rule in the provided ruleset
- `gate_result`: A `GateResult` object with:
  - `gate_name`: Always `"rules.coverage"`
  - `verdict`: `PASS` if all strict rules are referenced and no unknown references exist; otherwise `FAIL`
  - `findings`: Always an empty tuple
  - `notes`: A human-readable summary of the result
  - `traces`: A tuple of `Trace` objects, one per referenced rule, documenting the "implements" relationship between the artifact and each rule

**Pass/Fail Logic:**
- The gate passes if and only if:
  1. All rules with `enforcement == "strict"` are referenced in at least one scenario tag, AND
  2. No unknown references exist (references to rule IDs not found in the ruleset)
- Rules with non-strict enforcement do not cause failure if unreferenced

**Tag Extraction:**
- Scenario tags are parsed to extract references matching the `ruleset_short_name` filter
- For each extracted reference, the ruleset is queried using the rule ID
- If the rule ID is found, it is added to the referenced set
- If the rule ID is not found, the (ruleset_name, rule_id) pair is added to the unknown set

**Trace Generation:**
- Each referenced rule produces a `Trace` object with:
  - `source_reference` containing rule metadata from the ruleset (source_id, source_version, locator, description, active_from, applies_to, source_url)
  - `artifact_kind`: Always `"feature"`
  - `artifact_ref`: The provided or derived artifact reference
  - `relation`: Always `"implements"`
  - `confidence`: Always `"asserted"`

**Notes Field:**
- On pass: `"All strict rules in {ruleset.source_id} are referenced; no unknown reference tags."`
- On fail: A semicolon-separated list describing:
  - The count of strict unreferenced rules (if any)
  - The count of unknown references (if any)

## What we want to verify

- When all rules have `enforcement != "strict"`, the gate passes regardless of whether they are referenced
- When at least one rule has `enforcement == "strict"` and is not referenced, the gate fails and that rule appears in `unreferenced_rules`
- When a scenario tag references a rule ID not present in the ruleset, the gate fails and the (ruleset_name, rule_id) appears in `unknown_references`
- When all strict rules are referenced and no unknown references exist, the gate passes with verdict `PASS`
- The `unknown_references` tuple is sorted lexicographically
- Each rule in `referenced_rules` produces exactly one `Trace` in the gate result
- Rules in `unreferenced_rules` do not produce traces
- When `artifact_ref` is None and features have no paths, the artifact_ref defaults to `"<features>"`
- When `artifact_ref` is None and features have paths, the artifact_ref is a comma-separated list of those paths
- The `findings` field in `gate_result` is always an empty tuple
- The `gate_name` is always `"rules.coverage"`
- A rule is considered referenced if any scenario tag across any feature in the sequence references its ID
- The same rule can be referenced multiple times across scenarios, but appears only once in `referenced_rules` and produces only one trace

## Inventory references

- Arguments:
- (gate class)
- Related gates: coverage_gate_features
- Related ADRs:
- ADR 0004: Multi-ruleset workspace configuration — Accepted
- ADR 0005: `pickled-spec mine` staged mining pipeline — Accepted

## Open questions

- Docstring drift: The docstring states "union of scenario tags" but does not mention that only tags matching the `ruleset_short_name` filter are considered
- Docstring drift: The docstring does not describe the pass/fail criteria: that strict rules must all be referenced and no unknown references may exist
- Docstring drift: The docstring does not mention the `artifact_ref` parameter or its defaulting behavior
- Docstring drift: The docstring does not describe the return type structure (`CoverageReport`) or the contents of the gate result

## Status

draft
