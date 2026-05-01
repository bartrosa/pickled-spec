# Gate taxonomy

**Gates** are compensating checks around the LLM-to-DSL loop. Weak-oracle
backends (BDD runners, browser harnesses, etc.) prove little about whether the
artifact captures stakeholder intent. Gates ask orthogonal questions: ambiguity,
coverage, drift, robustness, and domain-specific controls.

This document defines the taxonomy used across packages. **v0.1** implements
only **Ambiguity** (see PR-08); the others are specified here so later PRs extend
behavior without renaming concepts.

---

## Ambiguity

**Question:** Does the artifact admit multiple plausible implementations or
interpretations relative to the stated intent?

**Input:** Draft DSL artifact (and optionally the upstream intent text).

**Output:** Verdict plus structured findings (locations, alternative readings).

**Mechanism:** Primarily an **LLM critic** guided by prompts and rubrics; may
combine with deterministic lint rules where the DSL has finite choice points.

**Failure mode if absent:** The team ships a coherent artifact that still solves
the wrong problem; tests pass under the wrong semantics.

**Used by:** `pickled-bdd`, `pickled-schema`, `pickled-policy` (any weak-to-medium
oracle flow where intent is underspecified in natural language).

---

## Coverage

**Question:** Does the artifact exhaust the stated requirements (behaviors,
constraints, regulatory clauses)?

**Input:** Requirement corpus (stories, clauses, checklist) and the artifact.

**Output:** Coverage map and gaps (missing branches, orphan requirements).

**Mechanism:** **LLM-assisted mapping** from requirements to artifact fragments,
followed by **deterministic completeness checks** (every requirement ID referenced,
every scenario traced, etc.).

**Failure mode if absent:** Silent omission; passing runs despite missing rules.

**Used by:** `pickled-bdd`, `pickled-schema`.

---

## Drift

**Question:** After code or environment changes, does the artifact still describe
what the implementation does?

**Input:** Diff or snapshot of implementation plus current artifact.

**Output:** Drift report (stale scenarios, obsolete policies, mismatched routes).

**Mechanism:** **LLM judgment** over structured diffs plus deterministic anchors
(file paths, symbol renames, schema hashes).

**Failure mode if absent:** Documentation and automation diverge; failures surface
late as prod incidents.

**Used by:** All weak-oracle packages that keep living DSL beside code.

---

## Robustness

**Question:** Would the artifact’s automated checks fail if the implementation
regressed in ways stakeholders care about?

**Input:** Tests/scenarios derived from the artifact; implementation under test.

**Output:** Mutation-survival analysis or equivalent robustness score.

**Mechanism:** **Mutation testing** and related deterministic fault injection.

**Failure mode if absent:** Tests assert trivial conditions; regressions slip
through green CI.

**Used by:** `pickled-bdd` primarily (scenario suites tied to executable checks).

---

## Lawyer-in-the-loop (policy-specific)

**Question:** Has a qualified human explicitly approved encoding this regulation
into machine-checkable policy?

**Input:** Policy artifact and regulatory citation metadata.

**Output:** Approval record (identity, timestamp, scope).

**Mechanism:** **Required human reviewer** on the PR or controlled workflow;
not replaceable by LLM verdict alone.

**Failure mode if absent:** Automated compliance theater; liability and audit
failure.

**Used by:** `pickled-policy` only.

---

## Regression (policy-specific)

**Question:** When upstream regulation changes, which policy artifacts are
affected and require revision?

**Input:** Parsed regulation changelog or diff; dependency graph of policies.

**Output:** Impacted policy set and suggested review order.

**Mechanism:** **Deterministic dependency tracking** between citations, clauses,
and encoded rules.

**Failure mode if absent:** Silent stale policies after legal updates.

**Used by:** `pickled-policy` only.

---

## Implementation scope

| Gate               | Documented | First implementation target |
|--------------------|------------|-----------------------------|
| Ambiguity          | yes        | PR-08 (v0.1)                |
| Coverage           | yes        | later                       |
| Drift              | yes        | later                       |
| Robustness         | yes        | later                       |
| Lawyer-in-the-loop | yes        | later                       |
| Regression         | yes        | later                       |

## See also

- [`pattern.md`](pattern.md) — oracle strengths and why gates exist.
- [`mcp.md`](mcp.md) — exposing gate-assisted workflows as MCP tools.
