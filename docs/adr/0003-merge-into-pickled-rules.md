# ADR-0003: Merge rule-coverage packages into `pickled-rules`

## Status

Accepted — 2026-05-17

Supersedes [ADR-0002](0002-pickled-law-package.md).

## Context

The monorepo had two near-identical engines aimed at the same abstract problem:
verifying that project artifacts (Gherkin features and scenarios) reference the
rules that apply to them. One package (`pickled-law`) loaded YAML rule corpora
with domain-specific field names; another placeholder (`pickled-policy`) was
planned for a separate policy DSL. Both would have shipped loaders, tag extraction,
coverage gates, Markdown reports, and CLIs.

Pre-alpha is the cheapest time to consolidate types, docs, and user-facing
wording before external adopters depend on package names.

## Decision drivers

- **One abstract problem.** Rule coverage analysis does not require two
  parallel type systems or two CLIs for v0.1.
- **Shared core already holds traces.** `SourceReference` and `Trace` in
  `pickled-core` are sufficient for any rule set the user brings.
- **Reduced surface.** One package, one schema, one set of example rule sets,
  one documentation trail — easier to review and demo.
- **Positional neutrality.** Public examples and docs should read as generic dev
  tooling (team conventions, checklists), not a specialised domain vertical.

## Considered options

### Option A — Keep separate packages

Continue with `pickled-law` for external rule sets and add `pickled-policy` for
internal policies later.

**Pros:** preserves ADR-0002 separation of concerns.

**Cons:** duplicated gate and report code; two CLIs; confusing discovery for
users who only need coverage checking.

### Option B — Single `pickled-rules` package

Replace both with one package using neutral terminology (`RuleSet`, `Rule`,
`enforcement`, `applies_to`, `SourceReference`).

**Pros:** one implementation path; smaller docs; example rule sets safe to
publish; same functional coverage as the old types (strict subset plus renamed
fields).

**Cons:** breaking rename for any early `pickled-law` consumers (acceptable
pre-1.0).

## Decision outcome

**Option B**: ship `pickled-rules` and remove `pickled-law` and the
`pickled-policy` placeholder from the workspace.

Rationale: maintaining two packages for the same gate pattern did not justify
the duplication cost at v0.1. Neutral naming keeps the framework reusable for
any YAML rule set without implying a product category.

## Consequences

### Positive

- One CLI (`pickled-rules check`), one README, one YAML schema.
- Example rule sets (API conventions, code-review checklist) demonstrate the
  pattern without sensitive domain content.
- `pickled-core` exposes `SourceReference` for all packages that need drift-aware
  pointers to rule artifacts.

### Negative

- ADR-0002 is superseded; historical text remains for audit.
- Any code that imported `pickled-law` or `Citation` must migrate (no aliases).

### Neutral

- `pickled-schema` and other family members are unchanged; they may register
  coverage-style gates using the same `Gate` protocol when needed.
