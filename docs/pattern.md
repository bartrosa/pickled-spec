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

- **Lean / Coq:** Dependently typed proof goals; false specs tend not to
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
  data; mis-encoded policy rules can still be internally consistent.
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
| `pickled-rules`  | YAML rule sets / Gherkin tags     | n/a (coverage)  |
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

## Rule-set coverage (`pickled-rules`)

`pickled-rules` applies the same four-part loop to **team-authored rule sets**
stored as YAML. The “DSL” is the rule set file; the artifact under check is
Gherkin (features and scenarios). Tags such as `@team-api-conv:naming.1` link
scenarios to rule IDs.

Coverage is checked before deeper solver-backed gates: the first question is
whether each **strict** rule is referenced at all. `SourceReference` metadata
(`source_version`, `active_from`) supports future drift gates when rule sets
change.

## See also

- [`monorepo.md`](monorepo.md) — workspace layout and core sizing rules.
- [`gates.md`](gates.md) — compensating gate taxonomy.
- [`mcp.md`](mcp.md) — exposing package capabilities as MCP tools.
