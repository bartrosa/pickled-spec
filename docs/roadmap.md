# Roadmap — pickled-* family

Directional plan for the monorepo. No dates by design — priorities shift with
feedback and maintenance capacity.

## Current state (repository snapshot)

The following is **implemented in-tree** (pre-alpha / v0.1 dev):

| Area | Delivered |
|------|-----------|
| **Workspace** | Six packages under `packages/*`, uv workspace, CI (ruff, mypy, pytest) |
| **pickled-core** | Types, `Gate`, LLM clients, cost/telemetry, FastMCP umbrella, `pickled-spec check-all` |
| **pickled-bdd** | Gherkin parse, AmbiguityGate, draft CLI, MCP, `pickled.gates` runner |
| **pickled-rules** | YAML rule sets, CoverageGate (union across features), `gdpr-web-crud` example, MCP |
| **pickled-schema** | OpenAPI 3.x validate/draft, SchemaCoverageGate, JSON Schema, proto parse, MCP |
| **pickled-iac** | Terraform/tofu validate, plan diff gate, optional Trivy scan, MCP |
| **pickled-data** | SQL parse, SQLite oracle, MigrationDriftGate (nullable-tolerant), MCP |
| **MCP transport** | stdio + HTTP via FastMCP; umbrella mounts all leaf servers |
| **Integration** | [`examples/user-management-crud/`](../examples/user-management-crud/) + [`integration-example.md`](integration-example.md) |
| **pickled-diff** | Reference-oracle category; `DifferentialOracleGate`, CLI, MCP tool (parallel track, v0.1 dev) |

**Next likely increments:** DataContractGate and PlanDiffGate in `check-all`;
rules MCP parity; CI recipe publishing `check-all` on PRs; package 1.0 hardening.

---

## Versioning rule

Each package has **independent semver**. **`pickled-core` 1.0** does not ship until
**two consumer packages** have stable, reviewed public APIs.

---

## Phase 1 — Foundations and BDD (v0.1)

**Status: DONE.**

Monorepo bootstrap, `pickled-core`, `pickled-bdd`, `pickled-rules` coverage gate,
docs, examples, CI.

---

## Phase 2 — Schema and rules expansion (v0.1–v0.2)

**Status: DONE (dev).**

- **`pickled-schema`** in workspace: OpenAPI first, coverage gate, MCP.
- **`pickled-rules`:** example rule sets pivot, `list-rules`, union coverage, `gdpr-web-crud`.
- **`pickled-diff` (parallel track, non-blocking):** reference-oracle category and
  `DifferentialOracleGate`. Does not compete for the same review bandwidth as
  schema/rules expansion; ships as an independent leaf package.

Further v0.2 work: stabilise JSON report format, relation-aware coverage (below).

---

## Phase 3 — MCP transport (v0.2.x)

**Status: DONE (dev).**

stdio/HTTP via `mcp` + FastMCP; `pickled-spec mcp`; per-package `mcp serve`;
[`mcp.md`](mcp.md) and smoke script.

---

## Phase 4 — IaC and data (v0.3)

**Status: DONE (dev).**

- **`pickled-iac`:** validate, plan diff, security baseline (Trivy optional).
- **`pickled-data`:** migrations, drift gate, sandbox apply.
- **`pickled-spec check-all`:** `pickled.gates` entry points from all five leaves.

---

## Phase 5 — Drift and CI integration (v0.3.x)

**Status: PARTIAL.**

- Migration drift gate and schema coverage exist; workspace `check-all` documented.
- **Remaining:** reusable GitHub Actions workflows; ruleset version drift gate;
  broader “live system” drift connectors.

---

## Phase 6 — Robustness and external connectors (v0.4+)

**Intent:** Hardening and optional integrations (mutation testing, issue trackers,
GitLab/GitHub spec diff, cloud connectors for IaC).

**Status: NOT STARTED** (directional only).

---

## pickled-rules — rule coverage analysis

Tag convention: `@<ruleset>:<rule_id>`.

### v0.1 (current)

- Rule set loader and validation
- Example rule sets (`team-api-conventions`, `code-review-checklist`, `gdpr-web-crud`)
- Coverage gate (strict rules required; union across multiple feature files)
- Markdown/JSON reports, `pickled-rules check`, `list-rules`, MCP tools

### v0.2

- JSON report format stabilised for automation
- MCP tool parity with CLI edge cases

### v0.3

- Relation-aware coverage for `requires_implementation_of`

### v0.4

- Drift when `source_version` or rule `description` changes between revisions

---

## Non-goals

- Replacing domain experts — gates assist; they do not alone certify production.
- A generic “do anything” agent framework — scope stays DSL + deterministic loops.
- Vendor lock-in — Anthropic is the reference client; `LLMClient` stays swappable.

---

## How to read this roadmap

Directional only — no fixed dates. Prefer smaller correct increments. For the
historical PR sequence that built v0.1, see [`plan.md`](../plan.md) when present.
