# pickled-spec

> **LLM-to-DSL bridge with deterministic verification** — applied across
> software engineering, from BDD scenarios to compliance policies.

`pickled-spec` is a monorepo hosting a family of Python packages, each one
a specialized instance of the same architectural pattern: take
natural-language intent, draft an artifact in a structured DSL, then gate
it through a deterministic backend that decides whether the artifact is
valid within its own semantics.

**Status:** pre-alpha. APIs and scope subject to change.
**License:** Apache-2.0.
**Python:** 3.11+.

## The pattern

Natural language → LLM drafting → structured DSL artifact → deterministic
backend (oracle) plus compensating gates → feedback loop.

Different members of the family target different DSLs and different oracle
strengths. Weak-oracle members (BDD runners, OpenAPI validators) carry more
compensating gates; medium-oracle members (Terraform plan, OPA decisions)
need fewer.

The pattern itself, including the strong/weak oracle distinction and the
gate taxonomy, will be documented in `docs/pattern.md` (PR-02).

## Packages

| Package           | DSL / Domain                        | Oracle    | Status        |
|-------------------|-------------------------------------|-----------|---------------|
| `pickled-core`    | Shared types, Gate protocol, MCP    | n/a       | scaffolded    |
| `pickled-bdd`     | Gherkin / pytest-bdd                | weak      | v0.1 dev      |
| `pickled-schema`  | OpenAPI / JSON Schema / Protobuf    | medium    | planned v0.2  |
| `pickled-policy`  | Rego / OPA, Cedar                   | medium    | planned v0.2  |
| `pickled-iac`     | Terraform / OpenTofu                | medium    | planned v0.3  |
| `pickled-data`    | SQL / dbt / migrations              | medium    | planned v0.4  |

Each package publishes to PyPI independently. `pickled-core` is the only
shared dependency; everything else is opt-in.

## Why a monorepo

Two reasons:

1. **Shared core.** Every package uses the same `Gate` protocol, the same
   `Verdict` enum, the same MCP server scaffolding, the same LLM client
   abstraction. Releasing `pickled-core` from a separate repo would mean
   a release dance for every signature change.
2. **Architectural consistency.** A change to the gate protocol must
   update every consumer in the same PR. Monorepo enforces this.

The monorepo is **disciplined**, not maximalist. `pickled-core` stays
small. If something is used by only one package, it lives in that package.

## Quick start

```bash
# install uv (one-time)
curl -LsSf https://astral.sh/uv/install.sh | sh

# bootstrap the workspace
git clone https://github.com/bartrosa/pickled-spec.git
cd pickled-spec
uv sync

# run tests across the workspace
uv run pytest

# install one published package only (typical end-user)
pip install pickled-bdd
```

## Documentation

Full documentation lands across PR-02 and PR-11. Until then, see
`CONTRIBUTING.md` for development setup.

## Sibling project

`kalinov-bridge` is a separate project by the same author applying this
pattern with **Lean 4** as a strong oracle. It targets mathematical
research and theorem mining; `pickled-spec` targets software engineering.
The two projects share **only the conceptual pattern**, no code.

## License

Apache-2.0. See `LICENSE`.
