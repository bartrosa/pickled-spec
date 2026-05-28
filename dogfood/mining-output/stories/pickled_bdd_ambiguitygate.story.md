# Story: AmbiguityGate.run

## Metadata

- **Surface kind:** gate
- **Package:** pickled-bdd
- **Surface id:** pickled_bdd_ambiguitygate
- **Code depth:** callgraph | **Units read:** 4 | **Unresolved:** 5

## Context

This surface is a quality gate that analyzes BDD feature scenarios for ambiguity. It is invoked by a gate-runner framework as part of a quality checking pipeline. Callers pass a Feature object containing scenarios, and receive a structured GateResult that indicates whether scenarios are ambiguous (admit multiple implementations). The gate uses an LLM to assess each scenario, parsing structured JSON responses to identify ambiguity findings.

## What the target does today

**Input constraints:**
- Accepts a `target` (any object) and an optional `context` dict; the context parameter is accepted but ignored.
- If `target` is not a Feature instance, returns immediately with verdict FAIL and a note describing the type mismatch (e.g., "Expected Feature, got <TypeName>").

**Processing flow:**
- Iterates over all scenarios in the Feature's `scenarios` attribute.
- For each scenario, formats it as a multi-line string with "Scenario: <name>" followed by indented step lines.
- Renders a prompt using an unresolved template renderer (`self._template.render`), passing the formatted scenario text.
- Delegates to an unresolved collaborator (`complete_prompt`) to obtain an LLM response, instructing the LLM to return a single JSON object without markdown fences or extra commentary.
- Attempts to parse the response as JSON, applying best-effort extraction that strips leading/trailing whitespace and removes markdown code fences (detects triple-backtick blocks with optional language tags).
- If JSON parsing fails for a scenario, records the scenario name in a `parse_errors` list and skips further processing for that scenario.
- If the parsed JSON indicates ambiguity (`is_ambiguous` key is truthy), constructs an AmbiguityFinding with the scenario name, a tuple of alternative implementations (from the `alternatives` key, coerced to strings), and a suggested fix (from the `suggested_fix` key, coerced to string).

**Verdict logic:**
- If all scenarios produce parse errors (and at least one scenario exists), returns WARN verdict with an empty findings tuple and a note listing parse-error scenarios.
- Otherwise, computes a verdict based on ambiguous finding counts:
  - PASS if zero scenarios flagged ambiguous.
  - FAIL if all scenarios flagged ambiguous (and at least one scenario exists).
  - WARN if some but not all scenarios flagged ambiguous.
- If parse errors occurred and the verdict would otherwise be PASS, upgrades the verdict to WARN.

**Return value:**
- Always returns a GateResult with:
  - `gate_name`: the gate's name attribute.
  - `verdict`: one of PASS, WARN, or FAIL.
  - `findings`: a tuple of AmbiguityFinding objects (empty if all parses failed).
  - `notes`: a string summarizing the count of ambiguous scenarios over total scenarios, and listing parse errors if any occurred.

**Side effects:**
- None observable to the caller; LLM interaction is delegated to an unresolved collaborator.

## What we want to verify

- When target is not a Feature instance, verdict is FAIL and notes describe the actual type received.
- When target is a Feature with zero scenarios, verdict is PASS and notes indicate "0/0 scenarios flagged ambiguous."
- When all scenarios parse successfully and none are flagged ambiguous, verdict is PASS.
- When all scenarios parse successfully and all are flagged ambiguous, verdict is FAIL.
- When some but not all scenarios are flagged ambiguous, verdict is WARN.
- When all scenarios fail to parse (and at least one scenario exists), verdict is WARN, findings tuple is empty, and notes list parse-error scenario names.
- When some scenarios fail to parse and verdict would otherwise be PASS, verdict is upgraded to WARN and notes include parse-error scenario names.
- Each AmbiguityFinding contains the scenario name, a tuple of alternative implementation strings, and a suggested fix string.
- The notes field always includes a summary in the form "<N>/<M> scenarios flagged ambiguous" (except when all parses fail).
- JSON response parsing tolerates markdown code fences (triple backticks with optional language tags) and strips them before JSON parsing.
- The context parameter is accepted but has no effect on the result.

## Inventory references

- Arguments:
- (gate class)
- Related gates: AmbiguityGate.run
- Related ADRs:
- ADR 0005: `pickled-spec mine` staged mining pipeline — Accepted

## Open questions

- Docstring drift: The docstring states the gate "flags scenarios that admit multiple implementations" but does not describe the input type constraint (Feature only), the FAIL verdict for wrong input types, or the parse-error handling behavior (WARN verdict when all parses fail, parse-error notes appended, verdict upgrade to WARN).
- Docstring drift: The docstring does not mention that the gate uses an LLM to perform the ambiguity detection, nor that it relies on structured JSON responses.
- Docstring drift: The docstring does not describe the three-tier verdict logic (PASS/WARN/FAIL based on ambiguous-count thresholds) or the special case where parse errors upgrade a PASS to WARN.

## Status

draft
