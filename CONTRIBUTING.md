# Contributing to pickled-spec

`pickled-spec` is a monorepo. PRs follow a small-batch convention: each
PR has a single Goal, a Definition of Done, and ends with green CI.

## Setup

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/bartrosa/pickled-spec.git
cd pickled-spec
uv sync
uv run pytest
```

## Working on a single package

```bash
# tests for one package only
uv run pytest packages/pickled-bdd/tests

# install in editable mode for ad-hoc experimentation
cd packages/pickled-bdd
uv pip install -e .
```

## Conventions

- Python 3.11+.
- Type-checked with `mypy --strict` for everything under `packages/*/src`.
- Formatted and linted with `ruff` (rules in root `pyproject.toml`).
- Line length 100.
- Conventional Commits in commit messages
  (e.g. `feat(bdd): add ambiguity gate`).

## PR rules

1. **One PR, one Goal.** If you can't say it in one sentence, split it.
2. **Green CI required.** No "fix in follow-up" merges into main.
3. **Cross-package consistency.** A PR that changes a `pickled-core`
   protocol should update all consumers in the same PR. If that makes
   the diff too big, split the protocol change into a backwards-compatible
   intermediate version first.
4. **Docs travel with code.** A new gate in code means a new entry in
   `docs/gates.md` in the same PR (`docs/gates.md` lands in PR-02).

## Out of scope

- Generic BDD/test-runner tooling unrelated to the LLM-to-DSL pattern.
- New family members beyond the five planned. Open a discussion issue
  first if you think one is missing.
- Coupling to a single LLM vendor. Anthropic is the reference client;
  contracts must remain swappable.

## Issues

File issues against the appropriate package label
(`pkg:core`, `pkg:bdd`, `pkg:schema`, ...) so triage stays scoped.
Pattern-level discussion goes under `pattern:*` labels.

## Sibling project

`kalinov-bridge` is a separate project. Issues about Lean, formal
verification, or theorem mining belong there, not here.
