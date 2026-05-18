# ADR-0002: Separate `pickled-law` package, not extension of `pickled-policy`

## Status

Superseded by ADR-0003 — 2026-05-17

## Context

The pickled-* family already has a planned `pickled-policy` package for internal
business policies (access control, approval workflows, pricing rules). Regulatory
compliance shares some surface with internal policy: both are sets of rules, both
produce verdicts on artifacts, both need solver backends eventually.

The question: should regulatory corpora live inside `pickled-policy` (as a
“regulatory” subtype) or in a separate `pickled-law` package?

## Decision drivers

- **Provenance semantics differ.** Internal policies have a single authority (the
  company); regulations have layered authorities (legislator → regulator →
  guidance issuer → court).
- **Versioning semantics differ.** Internal policies follow git; regulations
  follow legislative effective dates and have legal significance for past behaviour
  (audits look at the rules in force at the time of an event, not the current
  version).
- **Jurisdiction matters for regulations, not internal policies.** Same feature can
  be compliant in PL but illegal in DE.
- **Corpus distribution model differs.** Internal policies stay in the company's
  repo. Regulatory corpora benefit from being shared (community + paid tiers).
- **Audit consumers differ.** Internal policy verdicts are read by engineering and
  product. Regulatory verdicts are read by compliance, legal, and external
  auditors who have specific RTM expectations.

## Considered options

### Option A — Extend `pickled-policy`

Single package handles both, with a `RuleSource` discriminant (internal vs
regulatory).

**Pros:** less code duplication; one package to maintain; users with mixed needs
get it in one install.

**Cons:** every type grows fields needed only in one mode (`jurisdiction` on
internal rules is awkward; `git_commit` on regulations is wrong). Harder to
license-segregate (internal policy code may go to one buyer, regulatory corpora
to another).

### Option B — Separate `pickled-law` package

`pickled-policy` handles internal policy; `pickled-law` handles regulatory
corpora; both depend on `pickled-core`.

**Pros:** clean type system per package; independent release cadence (regulatory
corpora update on legislative timelines, internal policy on sprint timelines);
cleaner business model (commercial corpora bundle under `pickled-law` without
affecting `pickled-policy`).

**Cons:** code duplication for shared concepts (gates, RTM-like reports will exist
in both eventually); two packages to discover.

### Option C — Wait and see

Delay the decision until both are partially built and refactor later.

**Pros:** more information.

**Cons:** users build on whichever ships first; refactoring becomes breaking; the
question gets harder, not easier.

## Decision outcome

**Option B**: separate `pickled-law` package.

Rationale: the semantic differences (provenance, versioning, jurisdiction, audit
consumer) are large enough that combining the two would either clutter both
abstractions or push the merge logic into runtime discriminants. The cost of mild
duplication is small compared to the cost of poor abstractions for a
load-bearing feature.

`pickled-core` will absorb anything genuinely shared (`Citation`, `Trace`,
`Verdict`). Anything that turns out to be needed by both packages migrates to
`pickled-core` later under semver discipline.

## Consequences

### Positive

- Clean type system per package.
- Independent release cycles aligned with their respective change sources.
- Clear license / distribution boundary between internal-policy and regulatory
  tooling.
- Easier to commercialize regulatory corpora without affecting policy.

### Negative

- Two CLIs (`pickled-policy check` and `pickled-law check`). May confuse early
  users. Mitigation: a thin `pickled-spec` umbrella CLI in v0.3 that dispatches to
  family members.
- Some code will be written twice before it migrates to core (gate scaffolding,
  RTM rendering). Mitigation: deliberately copy on first duplication, refactor to
  core on the second (rule of three).
- More PyPI surface area, more docs to write.

### Neutral

- The `pickled-policy` package is unaffected by this decision and continues toward
  its v0.2 milestone independently.
