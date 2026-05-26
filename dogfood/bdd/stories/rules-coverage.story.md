# Story: pickled-rules verifies that strict rules are referenced

## Context

A rule set is a list of rules a team has decided to enforce on its own
artifacts — internal architectural invariants, AI dev tool best
practices, OSS hygiene checks, domain conventions. Each rule is either
strict (must be referenced somewhere), advisory (may or may not be
referenced), or informational (never required). Rules are written in
YAML; references are Gherkin tags of the shape `@<short_name>:<rule_id>`
on scenarios or features.

The coverage gate exists because rules-as-prose drift. Once a team has
ten or fifteen written rules and a few hundred scenarios, nobody knows
which rules are actually being tested and which were written, agreed,
and forgotten. The gate makes the forgetting visible: every strict
rule must have at least one scenario that claims to implement it, or
the gate fails. Conversely, every tag must point at a real rule, or
the gate fails — typos and stale tags after a rule rename get caught.

This is the gate pickled-spec turns on itself in the `dogfood/`
workspace. The rulesets there (`pickled-internal`, `best-practices`,
`oss-hygiene`, plus six per-package domain rulesets) compose via
`pickled.ruleset.yaml`'s plural `rulesets:` form introduced in PR #4.

## What pickled-spec does today

`coverage_gate_features(features, ruleset, ruleset_short_name=...)`
returns a `CoverageReport` containing the gate verdict, the set of
referenced rules, the set of unreferenced rules, and the set of
unknown references (tags with the right short_name prefix but a
rule_id not in the ruleset).

Coverage is computed as a **union** across the feature set: a strict
rule passes if any scenario in the union carries its tag. This is
intentional — splitting a behaviour across multiple feature files for
readability must not penalise coverage.

The workspace runner (`pickled-spec check-all --workdir <dir>`) reads
`pickled.ruleset.yaml`. When the file uses the singular `ruleset:`
form, the gate is named `rules.coverage` (one row in the output).
When it uses the plural `rulesets:` form, each ruleset becomes a
separately-named gate: `rules.coverage.<short_name>`. Mixing both
forms in one file is an error (ADR-0006).

`pickled-rules check` runs the same gate from the CLI with explicit
`--ruleset` and `--feature-glob` arguments; the MCP equivalent is
`rules_check_coverage`, which takes the YAML text plus a feature
list and returns the same `CoverageReport` shape.

## What we want to verify

Across the CLI and MCP surfaces, and across single- and multi-ruleset
configurations:

- A feature that references every strict rule in a ruleset yields
  PASS with `unreferenced_rules` empty of strict entries.
- A feature missing a tag for any strict rule yields FAIL with the
  missing rule ids enumerated in the gate notes.
- A feature carrying a tag `@short_name:bogus-id` not present in
  the ruleset yields FAIL with the unknown reference reported.
- Union semantics: two features each covering half the strict rules
  together yield PASS; neither alone would.
- Advisory rules without references do not cause FAIL but appear in
  the unreferenced list for visibility.
- The singular `ruleset:` form continues to produce a gate named
  exactly `rules.coverage` (no namespace), to preserve backward
  compatibility with the `examples/user-management-crud/` workspace.
- The plural `rulesets:` form produces N gates named
  `rules.coverage.<short_name>`, one per configured ruleset, each
  independently PASS/FAIL.
- Mixing both `ruleset:` and `rulesets:` in one file produces a
  FAIL verdict on workspace load (not a runtime crash).
- A ruleset file path that does not exist yields one FAIL gate
  while other configured rulesets continue to be evaluated.

## Inventory references

- CLI: `pickled-rules check --ruleset <X> --feature-glob <Y>`,
  `pickled-rules list-rules --ruleset <X>`
- MCP tools: `rules_check_coverage`, `rules_list_rules`
- Gates: `coverage_gate_features` (function), `rules.coverage` and
  `rules.coverage.<short_name>` (entry point names)
- ADRs: ADR-0006 (multi-ruleset workspace)

## Open questions

- Today, a tag whose short_name prefix matches no configured
  ruleset is silently ignored. This is permissive on purpose
  (mixed-tag environments where some scenarios cite external
  rule sets), but it means typos in the short_name silently
  disappear. Candidate for a `--strict-tag-prefixes` flag tracked
  under cross-ruleset-orphan-tag-detection in ADR-0006 future work.
- Rule IDs are matched case-sensitively but short_names are
  matched case-insensitively in `extract_references`. This is
  asymmetric and undocumented; either the asymmetry is principled
  (and we explain why) or it is a bug.

## Status

draft
