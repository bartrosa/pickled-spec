# The pickled-spec pattern

This document describes the structural pattern shared by every package in the
`pickled-*` family: how natural-language intent becomes a DSL artifact, how a
deterministic backend evaluates that artifact, and why oracle strength drives
how much compensating machinery you need around the loop.

## Four-part structure

Every member of the family instantiates the same coarse pipeline:

1. **Intent source.** Requirements, policy prose, user stories, or other
   informal input that states what should hold in the world.
2. **LLM drafter.** A language model (or orchestrated chain) proposes a
   concrete artifact in a **DSL** chosen for the domain (Gherkin, OpenAPI,
   Rego, Terraform HCL, SQL, etc.).
3. **DSL artifact.** The structured object under version control: features,
   schemas, policies, plans, migrations. It is the contract between humans,
   tools, and automation.
4. **Deterministic backend.** An engine that evaluates the artifact against
   fixed rules: test runners, validators, decision engines, parsers,
   model checkers. Its verdict is repeatable given the same artifact and
   environment.

The backend is the **oracle** for “does this artifact satisfy its own
syntax and operational semantics in this toolchain?” It does not, by itself,
answer “did we formalize the *right* intent?” That gap is where **gates**
and weaker oracles matter.

## Oracle strength: strong, medium, weak

We classify backends by how much *semantic* assurance they provide beyond
local consistency.

### Strong oracle

The backend can reject broad classes of incorrect or underspecified artifacts
with proofs or exhaustive search over meaningful state spaces. Wrong intent
often becomes **inconsistency** or **counterexample**, not a passing run.

Examples:

- **Lean / Coq:** Dependently typed proof obligations; false specs tend not to
  type-check or close goals.
- **TLA+ model checker:** Temporal properties checked over finite or bounded
  abstract models; invariant violations surface as traces.

Strong-oracle packages need fewer *compensating* checks because the backend
already constrains the artifact semantics tightly relative to the encoded theory.

### Medium oracle

The backend enforces **structured validity** and often **domain semantics** on
the artifact (types, policies evaluated on inputs, plans vs prior state), but
does not prove full correctness of the informal intent behind the artifact.

Examples:

- **OpenAPI / JSON Schema validators:** Syntactic and partial semantic checks;
  they do not prove the API matches product intent.
- **OPA / Cedar decision engines:** Deterministic evaluation of rules against
  data; mis-encoded regulation can still be internally consistent.
- **Terraform / OpenTofu plan:** Dependency graph and provider semantics;
  “planned destroy” can be wrong for the business yet valid as a plan.
- **SQL DDL parser / static checks:** Schema shape and constraints; not whether
  the schema matches business rules.

Medium-oracle flows benefit from **some** gates (especially around ambiguity and
coverage of requirements) but typically fewer than weak-oracle flows.

### Weak oracle

The backend checks **execution-shaped** behavior: examples pass, scenarios
green, properties hold on sampled inputs. Multiple distinct implementations
can satisfy the same artifact while implementing the wrong product behavior.

Examples:

- **Cucumber / pytest-bdd:** Steps match text and code binding; the feature can
  describe the wrong behavior coherently.
- **Playwright / browser automation:** Assertions hold on scripted flows; they do
  not certify completeness of intent.
- **Hypothesis (property-based testing):** Finds counterexamples to stated
  properties; properties can omit the behaviors stakeholders care about.

Weak-oracle members **must** add **compensating gates** beyond the runner.
The runner alone cannot catch **intent mismatches**: an LLM can produce a
feature file, steps, and implementation that are mutually consistent yet wrong
relative to the original story.

## Mapping pickled-* packages to oracle strength

The following table maps each planned package to its primary backend strength.
`pickled-core` supplies shared types and protocols; it is not an oracle for end
artifacts.

| Package          | Primary DSL / domain              | Oracle strength |
|------------------|-----------------------------------|-----------------|
| `pickled-core`   | Shared types, gates, MCP wiring   | n/a (library)   |
| `pickled-bdd`    | Gherkin / pytest-bdd              | weak            |
| `pickled-schema` | OpenAPI / JSON Schema / Protobuf  | medium          |
| `pickled-policy` | Rego / OPA, Cedar                 | medium          |
| `pickled-iac`    | Terraform / OpenTofu              | medium          |
| `pickled-data`   | SQL / dbt / migrations            | medium          |

Strength here refers to the **dominant** evaluation path for the artifact.
Packages may compose tools (e.g. policy plus tests); the table reflects the
main deterministic backend that accepts or rejects the DSL artifact.

## Structural pattern, not logical isomorphism

The family shares **architecture**: intent, draft, DSL, oracle, gates, feedback.
It does **not** share a single logical calculus or uniform correctness notion.
A Gherkin feature and an OpenAPI document admit different kinds of mistakes;
gates are tuned per domain.

Cross-package reuse lives in `pickled-core` (protocols, verdict types, MCP
registration). Semantic guarantees remain **per DSL** and **per oracle**.

## Regulated-domain DSLs

`pickled-law` introduces a wrinkle on the base pattern: the “structured DSL” is
authored by an external authority (legislator, regulator, standards body), not by
the project. This changes a few things:

1. **The DSL has its own version that the project does not control.** Drift
   detection becomes a first-class concern, not a future refinement.
2. **The verdict carries jurisdictional metadata.** A “pass” in one jurisdiction
   may be a “fail” in another with the same scenarios.
3. **The audit consumer is external.** RTM artifacts must be readable by auditors
   who do not know our toolchain. Markdown is the minimum; Excel and signed PDFs
   follow.
4. **Coverage matters before correctness.** “Did you address this regulation at
   all?” is a stronger first question than “is your address logically sound?”.
   This is why `pickled-law` ships a coverage gate before a compliance gate.

`pickled-policy` will share the verdict and trace machinery but does not carry
jurisdictional or external-version semantics — its DSL is internal.

## See also

- [`monorepo.md`](monorepo.md) — workspace layout and core sizing rules.
- [`gates.md`](gates.md) — compensating gate taxonomy.
- [`mcp.md`](mcp.md) — exposing package capabilities as MCP tools.
