# Roadmap — pickled-* family

Directional plan for the monorepo. This is not a contractual schedule; there are
no dates by design — priorities shift with feedback and maintenance capacity.

## Versioning rule

Each package has **independent semver**. **`pickled-core` 1.0** does not ship until
**two consumer packages** (family members that depend on core) have reached stable,
reviewed public APIs — so core’s stability promises align with real downstream use,
not theory.

## Phase 1 — Foundations and BDD (v0.1)

**Intent:** Prove the LLM-to-DSL pattern on one weak-oracle domain end-to-end.

**Scope (PR-00 through PR-11):**

- Monorepo bootstrap with **uv** workspace, **GitHub Actions** CI (ruff, mypy,
  pytest, gitlint on Conventional Commits).
- Top-level and architecture docs: pattern, monorepo, gates, MCP plan.
- **`pickled-core`:** shared types, **`Gate`** protocol, **`LLMClient`** boundary,
  optional **Anthropic** client, **`PickledMCPServer`** registry (transport
  deferred).
- **`pickled-bdd`:** Gherkin adapter aligned with pytest-bdd, **FeatureDrafter**,
  **Ambiguity** compensating gate, CLI (**draft**, **check**, **serve**),
  **`mcp_tools.register`**, tests and examples.
- **Placeholder directories** for **`pickled-schema`**, **`pickled-iac`**,
  **`pickled-data`** (README only; excluded from the workspace until each gains a
  `pyproject.toml`).
- **`pickled-rules`:** YAML rule sets, coverage gate, Markdown report, CLI.
- **Closing PR (this phase):** roadmap (this document), ADR template and process,
  full **contributing** guide, README polish.

**Definition of done:** CI green on `main`; a contributor can clone, `uv sync`,
run tests, draft/check the password-reset example with a configured LLM or fake
factory; MCP tools register in-process; stdio MCP transport explicitly still
out of scope for v0.1.

**Status:** DONE after the Phase 1 closing PR merges.

---

## Phase 2 — Second instance (v0.2)

**Intent:** Ship **exactly one** of **`pickled-schema`** or expand
**`pickled-rules`** MCP/reporting first — not both in the same release train —
so review bandwidth and narrative stay focused.

| Option | Pros | Cons |
|--------|------|------|
| **pickled-schema** (OpenAPI / JSON Schema / Protobuf) | Broad adoption; clear deterministic backends (validators, contract tests); fits “weak oracle + gates” story. | Large surface area (formats, versions); easy to sprawl. |
| **pickled-rules** (YAML rule sets) | Simple deterministic backend; clean fit for the gate pattern; easy demo with neutral example rule sets. | Schema design needs care — generic enough to be reusable, specific enough to be useful. |

The choice will be recorded in **`docs/decisions/0001-second-package.md`** when
made.

**Definition of done:** Chosen package has `pyproject.toml`, parser/drafter path,
at least one compensating gate, CLI or MCP hooks consistent with v0.1 BDD; removed
from workspace **`exclude`**; published dev/pre-release workflow documented.

---

## Phase 3 — MCP transport (v0.2.x)

**Intent:** Wire the official **`mcp`** Python SDK so the same tool registry
serves **stdio** clients.

**Definition of done:** End-to-end validation with **Claude Desktop** and
**Cursor** (or equivalent); documented connection snippet in **`docs/mcp.md`**;
**`pickled-bdd serve`** (and siblings as they exist) runs without
**NotImplementedError** for transport.

---

## Phase 4 — Third package (v0.3)

**Intent:** Implement the **other** Phase 2 candidate (schema or policy) so both
contract and policy bridges exist.

**Definition of done:** Same bar as Phase 2 for the second package; no regression
to core **Gate** / **LLM** contracts without coordinated releases.

---

## Phase 5 — Drift gate and CI integration (v0.3.x)

**Intent:** **Drift**-style gates where artifacts can be compared to live systems
or golden files; reusable **GitHub Actions** recipes per package.

**Definition of done:** At least one package ships a Drift (or equivalent)
gate with documented inputs; example workflows in-repo for “gate on PR” that
don’t require proprietary secrets in CI logs.

---

## Phase 6 — Robustness and external connectors (v0.4+)

**Intent:** Hardening and product-adjacent integrations.

- **Mutation testing** (or similar) where it catches real gate gaps.
- **Issue trackers:** Jira / Linear connectors for **pickled-bdd** (link scenarios
  to work items).
- **Drift:** GitHub (or GitLab) diff connector for comparing specs to repo state.
- **pickled-iac:** cloud provider connectors once Phase 2–5 patterns are stable.

**Definition of done:** Scoped per connector (no big-bang); each integration is
optional and documented; secrets handled via env / OIDC patterns, not baked into
tools.

---

## pickled-rules — rule coverage analysis

Loads YAML rule sets and verifies that Gherkin features reference the rules that
apply. Tag convention: `@<ruleset>:<rule_id>`.

### v0.1 (current)

- Rule set loader and validation
- Two example rule sets (API conventions, code-review checklist)
- Coverage gate (strict rules must be referenced; unknown tags fail)
- Markdown coverage report and `pickled-rules check` CLI

### v0.2

- MCP tools mirroring `pickled-bdd` (`check_feature_coverage`, `list_rulesets`,
  `validate_ruleset`)
- JSON report format stabilised for automation

### v0.3

- Relation-aware coverage: flag missing targets for
  `requires_implementation_of` relations

### v0.4

- Drift detection when `source_version` or rule `description` changes between
  rule set revisions

---

## Non-goals

- **Replacing domain experts** — gates assist; they do not certify production
  readiness alone.
- **A generic “do anything” agent framework** — scope stays DSL drafting plus
  deterministic verification loops.
- **Vendor lock-in** — Anthropic is the reference client; the abstraction stays
  swappable.

---

## How to read this roadmap

This document is **directional**. It does not promise dates or ordering beyond the
broad version bands above. When trade-offs appear, prefer shipping a smaller,
correct increment over expanding simultaneous tracks. For the historical PR
sequence that built v0.1, see [`plan.md`](../plan.md).
