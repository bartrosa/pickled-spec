# Story: pickled-bdd flags ambiguous scenarios via the AmbiguityGate

## Context

A draft Gherkin feature can parse cleanly and still be useless. The
classic failure modes are: a scenario that conflates several behaviours
into one ("the user signs up and updates their profile and logs out"),
a scenario that asserts an implementation detail instead of an
observable outcome ("then the `users` table has one new row"), or a
scenario whose Given depends on the outcome of a previous scenario,
silently coupling the suite.

The AmbiguityGate exists to surface these failures before a feature
file goes into version control. It is one of pickled-spec's two
LLM-as-judge gates (the other being schema-coverage's tag inference),
and the design constraint is that the gate must be **skippable** —
because the gate's value depends on an LLM being available, and the
project must remain usable when it is not.

## What pickled-spec does today

`AmbiguityGate.evaluate(feature)` returns a `GateResult` with verdict
PASS, WARN, or FAIL. The gate is also reachable as the MCP tool
`bdd_validate_feature_ambiguity` and is registered as a workspace
gate so `pickled-spec check-all --workdir <dir>` runs it across
`features/**/*.feature`.

When no `LLMClient` is configured (no provider in
`pickled.config.yaml`, no `PICKLED_BDD_LLM_FACTORY` env var), the
gate emits `Verdict.PASS` with a note explaining that the LLM oracle
was unavailable. Critically, the verdict is PASS and not WARN: the
gate must not block work just because the project is being run
offline or in CI without API keys. The skipped state is observable
in the notes field, so an operator can see it happened.

When an LLM is configured, the gate sends each scenario to the
oracle with a fixed prompt that asks "is this scenario unambiguous
under standard Given-When-Then discipline; if not, why not". The
oracle returns one of `{pass, warn, fail}` plus a one-sentence
rationale per scenario. The gate aggregates: any FAIL → FAIL; any
WARN with no FAIL → WARN; otherwise PASS.

The gate respects the cache and budget guard from
`build_default_client`. Identical scenarios on the same feature are
deduplicated within a single gate run.

## What we want to verify

Across the CLI and MCP surfaces, and with and without an LLM:

- A canonical unambiguous feature (one Given, one When, one Then,
  observable outcome) yields PASS.
- A canonical ambiguous feature with a "and the database has X"
  Then clause yields FAIL with a finding pointing at the offending
  step.
- A feature with one ambiguous scenario and several clean ones
  yields WARN, not FAIL, when the bad scenario is borderline
  (configurable via the oracle's verdict).
- With no LLM configured, the gate emits PASS with a note
  containing the literal substring "LLM oracle unavailable".
- The gate is registered under the `pickled.gates` entry point and
  appears in `check-all` output as `bdd.ambiguity`.
- Cache hits on identical scenarios are observable (same gate run
  on the same input twice does not double-bill).
- The aggregated verdict obeys the documented precedence (any FAIL
  → FAIL; WARN with no FAIL → WARN; else PASS).

## Inventory references

- CLI: `pickled-bdd ambiguity --feature <PATH>`
- MCP tools: `bdd_validate_feature_ambiguity`
- Gates: `AmbiguityGate` (class), `bdd.ambiguity` (entry point name)
- ADRs: ADR-0005 (LLM resolution path)

## Open questions

- Should "LLM oracle unavailable" be PASS or WARN? Today it is PASS
  with an explanatory note, on the principle that a missing
  optional dependency must not block CI. Some users want WARN so
  the skipped state is visible at a glance in the output table.
  This is exactly the design tension `iac-validate.story` will face
  for missing terraform/tofu — the project should resolve it once
  and apply the same answer across all skippable gates. Tracked
  under `verifier-warn-not-fail-on-skippable` and
  `ambiguity-gate-skips-cleanly-without-llm`.
- Per-scenario verdicts are not exposed in the GateResult today,
  only the aggregate. A future refinement should attach a
  Trace-per-scenario for downstream tooling.

## Status

draft
