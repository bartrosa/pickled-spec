# Stories index — pickled-spec dogfood

Eight stories describing pickled-spec's own behaviour, intended for
`dogfood/bdd/stories/` in the monorepo. Each story follows the same
shape: Context (narrative), What pickled-spec does today (concrete
implementation), What we want to verify (testable assertions),
Inventory references (CLI / MCP tools / Gates / ADRs touched), Open
questions (real, not synthetic), Status.

## Files

| # | File | Subject |
|---|------|---------|
| 1 | `bdd-drafter.story.md` | `bdd_draft_feature_from_story` — LLM-backed Gherkin drafter |
| 2 | `bdd-ambiguity-gate.story.md` | `bdd_validate_feature_ambiguity` — LLM-as-judge skippable gate |
| 3 | `rules-coverage.story.md` | `coverage_gate_features` — union coverage, single + multi-ruleset |
| 4 | `rules-drafter.story.md` | `rules_draft_ruleset_from_brief` — LLM-backed YAML drafter |
| 5 | `schema-validate.story.md` | `schema.openapi.validate` + `schema.coverage` — deterministic OpenAPI checks |
| 6 | `iac-validate.story.md` | `iac.validate` + `iac_security_baseline` — Terraform + Trivy |
| 7 | `data-drift.story.md` | `data.migration_drift` + `data_draft_sql_migration_from_intent` |
| 8 | `diff-oracle.story.md` | `DifferentialOracleGate` + `diff_draft_corpus_from_examples` |
| 9 | `check-all-orchestration.story.md` | `pickled-spec check-all` — entry-point gate runner |

## Conventions used

- **"What pickled-spec does today"** is deliberately stated in present
  tense, not "What pickled-spec will do". When the code changes, the
  story changes — these files are part of the version-controlled
  specification, not a wishlist.
- **"What we want to verify"** is a flat checklist of observable
  behaviours, each phrased so it can become one Gherkin `Scenario` in
  the feature file derived from this story (via
  `bdd_draft_feature_from_story`).
- **Open questions** are not TODOs. They are honest signals of
  unresolved design tension. A reader should be able to grep them
  across all stories and find a candidate backlog for v0.4.
- **Inventory references** pin each story to concrete surfaces in the
  current repo. If a tool name or entry point in this section is
  wrong, the story is stale.

## Status

All eight files are marked `draft` at the bottom. Promote to
`accepted` only after the feature file derived from a story has been
written, tagged, validated by AmbiguityGate, and run through
`check-all` cleanly.
