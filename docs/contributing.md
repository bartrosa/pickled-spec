# Contributing to pickled-spec

This guide is the long-form companion to the short pointer in the repository
root [`CONTRIBUTING.md`](../CONTRIBUTING.md).

## Setup

1. Install [**uv**](https://docs.astral.sh/uv/) (recommended):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Clone and sync the workspace:

   ```bash
   git clone https://github.com/bartrosa/pickled-spec.git
   cd pickled-spec
   uv sync
   ```

3. Run tests:

   ```bash
   uv run pytest -q
   ```

Match CI locally before pushing:

```bash
uv run ruff check .
uv run mypy packages/pickled-core/src packages/pickled-bdd/src
uv run pytest -q
```

Optional: enforce **Conventional Commits** on a message file with
`uv run pre-commit run --hook-type commit-msg --commit-msg-filename <file>`.

## Repository layout

- **Workspace root** — `pyproject.toml` aggregates members under `packages/*`,
  shared dev dependencies (pytest, ruff, mypy, gitlint), and pytest defaults.
- **`packages/<name>/`** — each shippable package has its own `pyproject.toml`,
  `src/`, and usually `tests/`.
- **`docs/`** — cross-cutting architecture and process docs (pattern, gates,
  MCP, roadmap, ADRs).
- **`tests/`** at the repo root — optional smoke or integration tests; most
  coverage lives beside each package.

Placeholder directories (`pickled-schema`, …) hold READMEs only and are listed in
the workspace **`exclude`** until they gain a real package manifest.

## PR-driven workflow

Every PR should state:

1. **Goal** — one sentence.
2. **Definition of Done** — checkbox list.
3. **Verification** — commands you ran (and CI will run).

Split work so each PR stays reviewable: **one PR, one goal**. If a change spans
`pickled-core` and a consumer, land them together so `main` never has a broken
protocol split.

## Conventional Commits

Use prefixes such as `feat(bdd): …`, `fix(core): …`, `chore(ci): …`. Release
automation and gitlint in CI expect this shape.

## Code style

- **Python** 3.11+.
- **Ruff** for lint and import order; **line length 100** (see root
  `pyproject.toml`).
- **mypy --strict** on `packages/*/src` as configured; use `[[tool.mypy.overrides]]`
  only when a third-party library lacks types.

## Where code belongs

- **`pickled-core`** — protocols, shared types, MCP scaffolding, LLM boundaries
  used by **more than one** package.
- **Heuristic:** code used by **exactly one** package stays in that package until
  a second consumer appears.
- **Domain parsers, runners, product logic** — live in the leaf package
  (`pickled-bdd`, future `pickled-schema`, …), not in core.

See [`monorepo.md`](monorepo.md) for the full “core stays small” rationale.

## Tests

- Cover **happy paths** and **gate verdicts** (PASS / WARN / FAIL) where gates
  exist.
- Prefer fakes or factories (see `pickled_bdd.testing`) for LLM-dependent tests in
  CI; reserve real API keys for local or manual smoke runs.

## Documentation

**Docs travel with code.** A new compensating gate needs an entry in
[`gates.md`](gates.md) (and any package README affected) in the same PR.

Cross-cutting decisions that affect APIs or architecture belong in an **ADR** —
see [`decisions/README.md`](decisions/README.md).

## Architecture Decision Records

Non-trivial choices (core API, pattern taxonomy, cross-cutting tooling) are
captured under [`docs/decisions/`](decisions/). Copy `0000-template.md`, use the
next numeric prefix, open a PR, set **Accepted** when merged.

## Extracting a package out of the monorepo

Splitting a package into its own repository is **exceptional**. Per
[`monorepo.md`](monorepo.md), keep it in the workspace until **all** of these
hold:

1. The package has a **stable 1.0** public API.
2. It has **dedicated maintainers** not solely tied to `pickled-core`.
3. **Release cadence** has diverged meaningfully from the rest of the family.

Until then, synchronization cost stays lower in one repo.

## Out of scope

- Generic BDD or test tooling unrelated to the LLM-to-DSL pattern.
- New family members beyond the planned set — open a discussion issue first.
- Hard coupling to one LLM vendor; keep **`LLMClient`** swappable.

## Issues

Use package labels (`pkg:core`, `pkg:bdd`, …) and pattern labels (`pattern:*`)
so triage stays scoped.

## Sibling project

**kalinov-bridge** (Lean / formal methods) is separate. Do not file Lean or
theorem-mining issues here.
