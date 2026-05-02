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
- **Placeholder directories** for **`pickled-schema`**, **`pickled-policy`**,
  **`pickled-iac`**, **`pickled-data`** (README only; excluded from the workspace
  until each gains a `pyproject.toml`).
- **Closing PR (this phase):** roadmap (this document), ADR template and process,
  full **contributing** guide, README polish.

**Definition of done:** CI green on `main`; a contributor can clone, `uv sync`,
run tests, draft/check the password-reset example with a configured LLM or fake
factory; MCP tools register in-process; stdio MCP transport explicitly still
out of scope for v0.1.

**Status:** DONE after the Phase 1 closing PR merges.

---

## Phase 2 — Second instance (v0.2)

**Intent:** Ship **exactly one** of **`pickled-schema`** or **`pickled-policy`**
first — not both in the same release train — so review bandwidth and narrative
stay focused.

| Option | Pros | Cons |
|--------|------|------|
| **pickled-schema** (OpenAPI / JSON Schema / Protobuf) | Broad adoption; clear deterministic backends (validators, contract tests); fits “weak oracle + gates” story. | Large surface area (formats, versions); easy to sprawl. |
| **pickled-policy** (Rego / OPA) | High leverage for compliance teams; strong story on compensating gates (lawyer-in-the-loop). | Regulatory risk and review burden; harder to demo safely in public examples. |

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

## pickled-law — regulatory traceability

Regulatory member of the family. Loads machine-readable corpora describing
regulations and verifies that project artifacts cover them.

### Status

- **v0.1** (current) — PoC slice. Coverage gate, HIPAA §164.312 corpus, Markdown
  RTM. Bootstrap sequence is tracked in [`plan.md`](../plan.md) alongside other
  packages.

### v0.2 — second corpus + MCP

- Add a second corpus to validate the schema beyond HIPAA. Likely candidates: 21 CFR
  Part 11 (FDA electronic records / signatures, used by every regulated lab and
  clinical trial system) or AI Act Annex III (high-risk classification rules).
  Choice depends on first user.
- MCP tools mirroring the pattern from `pickled-bdd`: `check_feature_coverage`,
  `list_corpora`, `validate_corpus`.
- Excel RTM export (`openpyxl`) for audit-friendly output.

### v0.3 — compliance gate

The first solver-backed gate.

- Gate signature: given a feature spec (or a more structured rule set) and a
  corpus, find combinations of inputs that satisfy the spec but violate a
  corpus rule.
- Backend: Z3 (free, open-source) as the default; documented extension point for
  Imandra (enterprise).
- Requires translating a subset of regulatory text into formal predicates. Initial
  corpora: PSD2 SCA exemptions, AI Act Annex III classifier rules. Each formalised
  rule must carry both the natural language `canonical_text` and the formal
  `predicate`, with a human-readable proof obligation linking them.

### v0.4 — conflict gate + drift gate

- **Conflict gate** detects contradictions between rules from different corpora
  (the GDPR-vs-HIPAA retention case is the canonical example). Output: regions of
  state space where one corpus mandates an action another forbids.
- **Drift gate** flips traces from `verified` to `drift_suspected` when a corpus's
  `source_version` changes and `canonical_text` differs. Generates a regression
  report.
- Corpus versioning infrastructure: each corpus YAML grows a `superseded_by` and
  `effective_until` set so traces against historical versions remain valid for
  audits of past behaviour.

### v0.5 — region decomposition / "regulatory gap" analysis

The differentiating feature. Most compliance tools answer "what do you violate?"
— `pickled-law` v0.5 also answers "what regions of your system's behaviour are
not constrained by any rule in your corpora?".

- Backend: Imandra (region decomposition) for full solution. Z3 fallback supports
  limited, finite-state cases.
- Output: list of state-space regions with no `constrains` relation from any loaded
  corpus. Compliance officers prioritize these for legal review.
- Hard caveat: "not constrained by my corpus" ≠ "not constrained legally".
  Documented prominently in CLI output and reports.
- Likely first commercial deal anchor.

### Corpora roadmap

Order is heuristic; pulled forward by user demand.

| Corpus                            | Domain          | Difficulty | Target |
|-----------------------------------|-----------------|------------|--------|
| HIPAA §164.312 Tech Safeguards    | US healthcare   | low        | v0.1 ✅ |
| HIPAA §164.308 Admin Safeguards   | US healthcare   | medium     | v0.2   |
| HIPAA Privacy Rule §164 Subpart E | US healthcare   | high       | v0.3   |
| HIPAA Breach Notification §164.400 | US healthcare  | medium     | v0.3   |
| 21 CFR Part 11 (FDA records)      | US life sci     | low        | v0.2   |
| 21 CFR Part 820 / QMSR (FDA QMS)  | US medtech      | high       | v0.4   |
| IEC 62304 (medical SW lifecycle)  | global medtech  | medium     | v0.3   |
| ISO 13485 (medtech QMS)           | global medtech  | high       | v0.4   |
| ISO 14971 (medtech risk mgmt)     | global medtech  | medium     | v0.4   |
| GDPR Articles 5-11                | EU privacy      | medium     | v0.2   |
| GDPR Article 9 (special categories) | EU privacy    | medium     | v0.2   |
| MDR 2017/745 (EU medical devices) | EU medtech    | high       | v0.4   |
| IVDR 2017/746 (EU IVDs)           | EU medtech      | high       | v0.4   |
| AI Act Annex III (high-risk)      | EU AI           | low        | v0.2   |
| AI Act Title III (high-risk obligations) | EU AI   | high       | v0.4   |
| DORA (digital operational resilience) | EU finance | medium     | v0.3   |
| PSD2 RTS on SCA                   | EU finance      | medium     | v0.3   |

ISO/IEC standards ship as **structural skeleton only** (rule IDs and titles, no
copyrighted text). Users supply licensed text via overlay files. This avoids
redistributing copyrighted material.

### Enterprise tier (separate roadmap)

Items not in the open-source release:

- Imandra solver backend with region decomposition
- Curated, lawyer-reviewed corpora with subscription updates (regulations change;
  community-maintained YAML drifts)
- Lawyer-in-the-loop workflow: every new compliance trace requires human approval
  before being marked `verified`
- Audit-grade reports with cryptographic signatures over the corpus version +
  feature commit hash + verdict
- SaaS deployment with multi-tenant corpus management

Pricing model: open core. Code Apache-2.0. Reference corpora (HIPAA §164.312, AI
Act Annex III) Apache-2.0 + CC0 for the YAML data. Curated corpora and enterprise
tier paid.

### Non-goals (`pickled-law`)

- **Replacing legal counsel.** `pickled-law` produces audit artifacts and catches
  mechanical mistakes. Interpretation of regulatory intent remains a human
  responsibility.
- **General theorem proving.** That's `kalinov-bridge` (separate project) and
  Imandra (separate vendor).
- **Code generation from regulations.** Catala already does that for France's tax
  code; we're not duplicating it. `pickled-law` verifies existing artifacts against
  regulations, not the other way around.
- **Real-time compliance monitoring.** Other tools (Drata, Vanta) own this niche.
  We're development-time / audit-time, not runtime.

---

## Non-goals

- **Replacing domain experts** — gates assist; they do not certify law, safety,
  or production readiness alone.
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
