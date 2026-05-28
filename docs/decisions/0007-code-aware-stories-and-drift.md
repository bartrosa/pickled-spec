# ADR-0007: Code-aware stories and docstring drift detection

- **Status:** Accepted
- **Date:** 2026-05-28
- **Deciders:** pickled-spec contributors

## Context

Phase 8e added static code reading (`code-context/<surface-id>.md`).
Phase 8e-fix hardened the resolver so constructor-then-method patterns
(e.g. `FeatureDrafter(llm).draft_from_story(story)`) resolve to real
bodies, not just entry-point glue.

Docstring-only stories (Phase 8d) were too shallow and sometimes wrong.
On the real `pickled-bdd` draft surface, a hand-written story claimed the
drafter **validates** Gherkin output. Code-reading showed the opposite:
`draft_from_story`'s docstring states the drafter does **not** validate
(returned Gherkin is raw; `warnings=()`). Human peer review had introduced
that confabulation. The mine pipeline can now ground stories in extracted
source instead of inventory summaries alone.

## Decision

### Code-grounded story generation

When `code-context/<surface-id>.md` exists under the mining output directory,
the stories stage loads root and resolved callee bodies plus the unresolved
callee list and passes them to the story prompt together with the surface
docstring. The model writes **observable behavior** (contract), not
implementation mechanics.

### Decision B: drift detection

The code is the source of truth. If the docstring **contradicts** the code,
the model emits a `---DRIFT---` block; each bullet is rendered under Open
questions prefixed with `Docstring drift:`. We do not silently override the
docstring or show code and docstring side-by-side without synthesis.

When no code-context exists, behavior falls back to Phase 8d docstring-only
rules and DRIFT is always empty.

### Anti-implementation-leak

Stories must not mention line numbers, private method names, or call-chain
narration ("it calls X then Y"). A reader should understand the contract
without seeing source. The prompt enforces this; tests guard the render path.

### Unresolved-call honesty

Calls the resolver cannot pin (protocol dispatch, dynamic getattr, etc.)
remain listed in code-context. The prompt forbids inventing behavior behind
those calls; delegated behavior is stated as uncertain.

### Friction #15: unresolved noise filtering

Before reporting unresolved callees, the code reader drops:

- **Stdlib-surface methods** — e.g. `str.strip()`, `Path.read_text()` on
  receivers that are not resolvable intra-project types.
- **Decorator registration** — callee scan walks function **bodies** only,
  so `@main.command()` on the definition is not treated as a behavioral call.

**Limit:** a user-defined method whose name collides with a common builtin
method (e.g. `.strip()`) on an unresolved receiver is also dropped. That
would have been unresolved noise anyway; accepted trade-off.

### Provenance metadata

Each story's Metadata section records **Code depth**, **Units read**, and
**Unresolved** counts when code-context was present, so readers can see how
strong the grounding was (`signature` vs `callgraph`).

## Consequences

- `mine all` runs inventory → code → stories; stories auto-detect
  `code-context/` under `--output`.
- `mine stories` accepts optional `--code-context` to override the directory.
- Mine acts as a **docstring drift detector** when docstrings lie or lag code.
- Story quality scales with `--depth` and `--max-hops` on the code stage.
- Live LLM quality still depends on the model; tests use canned clients for
  wiring and anti-leak contracts.
