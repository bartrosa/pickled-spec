# Documentation index

Cross-cutting docs for the **pickled-spec** monorepo. Per-package usage lives in
[`packages/<name>/README.md`](../packages/).

## Start here

| If you want to… | Read |
|-----------------|------|
| Understand the architecture | [`pattern.md`](pattern.md) |
| Run all workspace checks on an example | [`integration-example.md`](integration-example.md) |
| Wire Cursor or Claude Desktop | [`mcp.md`](mcp.md) |
| Contribute a PR | [`contributing.md`](contributing.md) |

## Architecture and process

- [`pattern.md`](pattern.md) — intent → LLM → DSL → oracle → gates
- [`gates.md`](gates.md) — Ambiguity, Coverage, Drift, and related gate types
- [`monorepo.md`](monorepo.md) — uv workspace, `pickled-core` scope, releases
- [`roadmap.md`](roadmap.md) — phases, package plans, non-goals
- [`contributing.md`](contributing.md) — setup, style, PR expectations
- [`decisions/`](decisions/) — ADRs (template in `0000-template.md`)
- [`adr/`](adr/) — older ADR copies (see `decisions/README.md` for canonical process)

## Examples in the repo

| Path | Purpose |
|------|---------|
| [`examples/user-management-crud/`](../examples/user-management-crud/) | End-to-end: BDD + OpenAPI + Terraform + SQL + `gdpr-web-crud` rules |
| [`packages/pickled-bdd/examples/`](../packages/pickled-bdd/examples/) | Password reset and other BDD samples |
| [`packages/pickled-rules/rulesets/examples/`](../packages/pickled-rules/rulesets/examples/) | Neutral YAML rule sets (`team-api-conventions`, `gdpr-web-crud`, …) |

## Umbrella commands (from repo root)

```bash
uv sync --extra mcp

uv run pickled-spec check-all --workdir examples/user-management-crud/ --warn-ok
uv run pickled-spec mcp --transport stdio
uv run python scripts/smoke_mcp_stdio.py
```

## Package READMEs

- [`pickled-core`](../packages/pickled-core/README.md)
- [`pickled-bdd`](../packages/pickled-bdd/README.md)
- [`pickled-rules`](../packages/pickled-rules/README.md)
- [`pickled-schema`](../packages/pickled-schema/README.md)
- [`pickled-iac`](../packages/pickled-iac/README.md)
- [`pickled-data`](../packages/pickled-data/README.md)
