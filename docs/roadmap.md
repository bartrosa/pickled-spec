# Roadmap (pickled-* family)

High-level delivery windows for planned packages. Details evolve with the
monorepo; see [`plan.md`](../plan.md) for the PR sequence.

| Package | Expected window | Notes |
|---------|-----------------|-------|
| **pickled-bdd** | Current focus | Validates the LLM-to-DSL pattern end-to-end. |
| **pickled-schema** | v0.2 candidate | Primary next bridge after BDD; may swap order with policy by demand. |
| **pickled-policy** | v0.2 candidate | Regulation-heavy; ships once lower-risk domains prove the pattern. |
| **pickled-iac** | v0.3+ | Terraform/OpenTofu; cloud auth and state add complexity. |
| **pickled-data** | v0.4+ | SQL/dbt; needs scoped dialect story (Postgres, Snowflake, …). |

Placeholders under `packages/pickled-*` track intent until each package gains a
real `pyproject.toml`.
