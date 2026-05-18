# Architecture Decision Records

This directory holds Architecture Decision Records (ADRs) following a
[MADR](https://adr.github.io/madr/)-inspired template.

Numbering is monotonic (`NNNN-kebab-case-title.md`) with leading zeros. ADRs are
immutable once accepted; subsequent decisions that change them get their own ADR
with `Supersedes: NNNN-...` in the Status section.

The older template-based ADRs under [`../decisions/`](../decisions/) remain valid
for lightweight decisions; **docs/adr/** is used for cross-cutting architecture
records with full MADR structure.

<!-- TODO: Backfill ADR-0001 for monorepo layout + uv workspaces (see plan.md);
     until then the row below is documented intent. -->

## Index

| #    | Title | Status |
|------|-------|--------|
| 0001 | Monorepo layout and uv workspaces | *Pending backfill* |
| 0002 | [Separate `pickled-law` package, not extension of `pickled-policy`](0002-pickled-law-package.md) | Superseded by 0003 |
| 0003 | [Merge rule-coverage packages into `pickled-rules`](0003-merge-into-pickled-rules.md) | Accepted |
