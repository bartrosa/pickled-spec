# Monorepo layout and release model

This repository hosts multiple Python packages under one revision graph so that
shared abstractions and cross-cutting protocol changes land atomically.

## Why a monorepo

**Shared `pickled-core`.** Gate interfaces, verdict enums, MCP server scaffolding,
and LLM client boundaries live in one place. Consumers import stable APIs without
coordinating separate releases for every signature tweak.

**Architectural consistency.** A change to the gate protocol or verdict lifecycle
must update every consumer in the same change set. The monorepo makes that
dependency explicit in CI and review.

## Workspace tooling

The workspace uses **uv** (`[tool.uv.workspace]` in the repo root). CI installs
a pinned Python matrix (see `.github/workflows/ci.yml`) and runs `uv sync` so
dependency resolution matches contributor machines.

Each package keeps its own `pyproject.toml` under `packages/<name>/` with its own
version and optional extras. The root aggregates workspace members and dev tools
(test runners, linters) used across the tree.

## Directory layout

```
pickled-spec/
  pyproject.toml          # workspace root; dev tooling
  uv.lock
  packages/
    pickled-core/
      pyproject.toml
      src/
      tests/
    pickled-bdd/
      ...
    ...
  docs/
  tests/                  # repo-level smoke or integration tests (optional)
```

Per-package tests live beside each package; cross-package integration tests may
live at the root when they genuinely span boundaries.

## Keeping `pickled-core` small

**Rule:** If code is used by **exactly one** package, it belongs in that package,
not in `pickled-core`.

**Heuristic:** Promote into core only when at least two distinct packages need
the same abstraction *and* the abstraction is stable enough to version together.

Core should contain protocols, shared types, MCP plumbing, and thin adapters.
Domain-specific helpers stay downstream unless sharing is real.

## Versioning and publishing

Each package carries **independent semver**. Releases go to PyPI per package;
installers depend only on what they need (`pip install pickled-bdd` does not pull
the entire monorepo).

Breaking changes in core propagate via coordinated version bumps and changelog
entries in consuming packages.

## Extracting a package to its own repository

Moving a package out is exceptional. **All** of the following should hold:

1. The package has reached **1.0** stable API for its public surface.
2. The package has **dedicated maintainers** who are not only maintaining
   `pickled-core`.
3. **Release cadence** has diverged meaningfully from the rest of the family
   (for example, monthly policy drops vs. quarterly core releases).

Until then, cost of synchronization stays lower inside one repo than across
multiple release trains.

## See also

- [`pattern.md`](pattern.md) — oracle strengths and gate rationale.
- [`gates.md`](gates.md) — gate taxonomy.
- [`mcp.md`](mcp.md) — MCP integration plan.
