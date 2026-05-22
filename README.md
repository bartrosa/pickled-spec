# pickled-spec

> **LLM-to-DSL bridge with deterministic verification** — applied across
> software engineering: from Gherkin scenarios to OpenAPI contracts, Terraform,
> SQL migrations, and YAML rule sets.

`pickled-spec` is a monorepo hosting a family of Python packages. Each package
applies the same pattern: take natural-language intent, draft an artifact in a
structured DSL, then gate it through a deterministic backend that decides whether
the artifact is valid within its own semantics.

**Status:** pre-alpha (v0.1 dev across packages). APIs and scope subject to change.  
**License:** Apache-2.0.  
**Python:** 3.11+.

## The pattern

Natural language → LLM drafting → structured DSL artifact → deterministic
backend (oracle) plus compensating gates → feedback loop.

Oracle strength varies by domain: weak (BDD runners), medium (OpenAPI validators,
`terraform plan`, SQL sandboxes). Weak oracles need more compensating gates.
See [`docs/pattern.md`](docs/pattern.md).

## Packages

| Package | DSL / domain | Oracle | v0.1 highlights |
|---------|----------------|--------|-----------------|
| [`pickled-core`](packages/pickled-core/) | Shared types, `Gate`, LLM, MCP | n/a | Umbrella CLI (`pickled-spec`), `check-all`, run telemetry |
| [`pickled-bdd`](packages/pickled-bdd/) | Gherkin / pytest-bdd | weak | Parse, `FeatureDrafter`, AmbiguityGate, MCP |
| [`pickled-rules`](packages/pickled-rules/) | YAML rule sets | n/a | CoverageGate, example rule sets incl. `gdpr-web-crud` |
| [`pickled-schema`](packages/pickled-schema/) | OpenAPI 3.x, JSON Schema, proto3 | medium | Validate, draft, SchemaCoverageGate, MCP |
| [`pickled-iac`](packages/pickled-iac/) | Terraform / OpenTofu HCL | medium | `validate`, plan JSON diff, Trivy baseline (optional), MCP |
| [`pickled-data`](packages/pickled-data/) | SQL DDL / migrations | medium | sqlglot parse, SQLite sandbox, MigrationDriftGate, MCP |
| [`pickled-diff`](packages/pickled-diff/) | Reference vs candidate outputs | reference | `DifferentialOracleGate`, runners, comparators, MCP |

Each package can publish to PyPI independently. `pickled-core` is the shared
dependency; leaf packages are opt-in.

## Umbrella CLI

Install the workspace (`uv sync`) or `pickled-core` with scripts enabled. The
**`pickled-spec`** command groups cross-package workflows:

```bash
# Run workspace gates on a directory (features/, specs/, infra/, migrations/)
uv run pickled-spec check-all --workdir examples/user-management-crud/

# Exit 0 when only optional WARN rows (no terraform, no LLM for ambiguity)
uv run pickled-spec check-all --workdir examples/user-management-crud/ --warn-ok

# MCP: all leaf tools in one stdio server (bdd_*, rules_*, schema_*, iac_*, data_*)
uv sync --extra mcp
uv run pickled-spec mcp --transport stdio
```

Gates are registered via the `pickled.gates` entry-point group in each leaf
package. `check-all` discovers them at runtime; it does not yet run every gate
class in each library (for example PlanDiffGate or DataContractGate).

## Integration example

[`examples/user-management-crud/`](examples/user-management-crud/) dogfoods all
five leaf packages on one fictional user API (registration, access, export,
erasure). Walkthrough: [`docs/integration-example.md`](docs/integration-example.md).

```bash
uv sync --extra mcp
uv run pickled-spec check-all --workdir examples/user-management-crud/ --warn-ok
```

## Quick start

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

git clone https://github.com/bartrosa/pickled-spec.git
cd pickled-spec
uv sync --extra mcp

uv run pytest -q
uv run python scripts/smoke_mcp_stdio.py
```

Install a single leaf from PyPI when published:

```bash
pip install pickled-bdd
```

## Per-package CLIs

| Command | Role |
|---------|------|
| `pickled-spec` | `check-all`, `mcp` (umbrella) |
| `pickled-bdd` | `draft`, `check`, `mcp serve` |
| `pickled-rules` | `check`, `list-rules`, `mcp serve` |
| `pickled-schema` | `validate`, `check`, `draft`, `mcp serve` |
| `pickled-iac` | `validate`, `plan-cmd`, `diff`, `scan`, `mcp serve` |
| `pickled-data` | `parse`, `apply`, `check-drift`, `mcp serve` |
| `pickled-diff` | `verify`, `serve` |

Details and environment variables: each [`packages/<name>/README.md`](packages/).

## Why a monorepo

1. **Shared core** — one `Gate` protocol, `Verdict`, MCP scaffolding, LLM client.
2. **Atomic protocol changes** — a gate signature change updates every consumer in one PR.

`pickled-core` stays small: domain logic lives in leaf packages. See
[`docs/monorepo.md`](docs/monorepo.md).

## Documentation

| Doc | Contents |
|-----|----------|
| [`docs/README.md`](docs/README.md) | Documentation index |
| [`docs/pattern.md`](docs/pattern.md) | LLM-to-DSL bridge, oracle strengths |
| [`docs/gates.md`](docs/gates.md) | Compensating-gate taxonomy |
| [`docs/mcp.md`](docs/mcp.md) | MCP servers, Cursor / Claude config |
| [`docs/integration-example.md`](docs/integration-example.md) | `user-management-crud` walkthrough |
| [`docs/monorepo.md`](docs/monorepo.md) | Workspace layout, versioning |
| [`docs/roadmap.md`](docs/roadmap.md) | Phases and non-goals |
| [`docs/contributing.md`](docs/contributing.md) | Contributor guide |
| [`docs/decisions/`](docs/decisions/) | Architecture decision records |

## Sibling project

[`kalinov-bridge`](https://github.com/bartrosa/kalinov-bridge) applies the same
**conceptual** pattern with Lean 4 as a strong oracle (mathematics / theorem
mining). No shared code with `pickled-spec`.

## License

Apache-2.0. See [`LICENSE`](LICENSE).
