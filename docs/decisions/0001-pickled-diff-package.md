# ADR-0001: pickled-diff package

- **Status:** Proposed
- **Date:** 2026-05-19
- **Deciders:** pickled-spec contributors

## Context

LLM-assisted workflows often produce a **candidate** implementation that must be
checked against an existing **reference** program. The pickled-* family already
covers strong, medium, and weak oracles for DSL artifacts (Gherkin, OpenAPI,
Terraform, SQL, YAML rules), but none of them treat “agreement with a trusted
implementation on a finite input corpus” as a first-class oracle category.

Teams need deterministic, repeatable differential checks when replacing or
refactoring code, without embedding domain logic into shared core libraries.

## Decision

Add **`pickled-diff`** as a new leaf package introducing:

- The **reference oracle** category in `docs/pattern.md`.
- **`DifferentialOracleGate`** implementing `pickled_core.Gate`.
- Pluggable **`OracleRunner`**, **`Corpus`**, and **`Comparator`** protocols.
- CLI (`pickled-diff verify`, `pickled-diff serve`) and MCP tool
  `verify_against_oracle`.

Types such as `DifferentialFinding` and the runner/comparator protocols remain in
`pickled-diff` until a second consumer justifies promotion to `pickled-core`.

## Consequences

**Positive**

- Fills a documented gap in the oracle taxonomy.
- Reuses existing `Gate`, `Verdict`, `GateResult`, and MCP scaffolding without
  bloating `pickled-core`.
- Zero LLM dependency in the gate path keeps CI hermetic.

**Negative**

- One more workspace member to maintain and eventually add to CI mypy paths.
- Umbrella MCP does not mount `pickled-diff` until an entry point is added in a
  follow-up (out of scope for the initial package PR).

## Alternatives considered

**Add `DifferentialOracleGate` to `pickled-core`.** Rejected: no concrete gates
live in core today; adding domain-shaped findings and runner protocols would break
the “core stays small” rule before a second consumer exists.

**Separate repository.** Rejected: the gate shares protocols and MCP patterns with
sibling packages; monorepo keeps gate signature changes atomic.

**Embed in `pickled-bdd` or another leaf.** Rejected: differential verification is
orthogonal to Gherkin and other DSLs; a dedicated package keeps dependencies minimal
(no Gherkin stack).
