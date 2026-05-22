# Monorepo layout and release model

This repository hosts multiple Python packages under one revision graph so that
shared abstractions and cross-cutting protocol changes land atomically.

## Why a monorepo

**Shared `pickled-core`.** Gate interfaces, verdict enums, MCP server scaffolding,
and LLM client boundaries live in one place.

**Architectural consistency.** A change to the gate protocol or verdict lifecycle
must update every consumer in the same change set.

## Workspace tooling

The workspace uses **uv** (`[tool.uv.workspace]` in the repo root). CI runs
`uv sync` so dependency resolution matches contributor machines.

All six packages are workspace **members** (no placeholder excludes):

| Package | Path |
|---------|------|
| pickled-core | `packages/pickled-core/` |
| pickled-bdd | `packages/pickled-bdd/` |
| pickled-rules | `packages/pickled-rules/` |
| pickled-schema | `packages/pickled-schema/` |
| pickled-iac | `packages/pickled-iac/` |
| pickled-data | `packages/pickled-data/` |
| pickled-diff | `packages/pickled-diff/` |

Each package has its own `pyproject.toml`, version, optional extras, and tests.

## Directory layout

```
pickled-spec/
  pyproject.toml          # workspace root; dev tooling
  uv.lock
  packages/
    pickled-core/         # also publishes pickled-spec CLI
    pickled-bdd/
    pickled-rules/
    pickled-schema/
    pickled-iac/
    pickled-data/
  examples/
    user-management-crud/ # cross-package integration workspace
  docs/
  scripts/
    smoke_mcp_stdio.py
```

Per-package tests live under `packages/<name>/tests/`. Cross-package checks use
`pickled-spec check-all` on `examples/*` workspaces.

## Entry points

| Group | Purpose |
|-------|---------|
| `project.scripts` | Per-package CLIs (`pickled-bdd`, …) and `pickled-spec` on core |
| `pickled.mcp.subservers` | Leaf MCP apps mounted by the umbrella |
| `pickled.gates` | `run_all(workdir)` runners consumed by `check-all` |

Adding a new leaf package should register both MCP and gates entry points when it
participates in workspace verification.

## Keeping `pickled-core` small

**Rule:** If code is used by **exactly one** package, it belongs in that package,
not in `pickled-core`.

**Heuristic:** Promote into core only when at least two packages need the same
abstraction and it is stable enough to version together.

## Versioning and publishing

Each package carries **independent semver** (mostly `0.1.0.dev0` today). Installers
depend only on what they need (`pip install pickled-bdd` does not pull siblings).

## Extracting a package to its own repository

Exceptional. See criteria in this document’s previous sections: stable 1.0 API,
dedicated maintainers, divergent release cadence.

## See also

- [`pattern.md`](pattern.md) — oracle strengths and gate rationale
- [`gates.md`](gates.md) — gate taxonomy
- [`mcp.md`](mcp.md) — MCP integration
- [`integration-example.md`](integration-example.md) — `examples/user-management-crud/`
