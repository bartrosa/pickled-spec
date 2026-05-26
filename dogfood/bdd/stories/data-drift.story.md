# Story: pickled-data verifies migrations match the expected schema

## Context

A SQL migration is a unit of expected change to a database. The
problem isn't writing migrations — engineers write those routinely.
The problem is the gap that opens, over months, between what the
migrations cumulatively declare and what someone *thinks* the schema
looks like. The expected-schema document drifts. Someone adds a
nullable column to ship a feature, the migration goes in, the YAML
that documents the schema gets a TODO, the TODO never gets closed,
six months later a different engineer makes a decision based on a
mental model the YAML never reflected. The bug lands.

The drift gate exists to make that gap impossible to leave open. The
contract is simple: `expected_schema.yaml` declares what the database
should look like, the migration files declare changes that produced
that state, and the gate cross-checks. Any divergence is either a
bug in the YAML, a bug in the migrations, or a deliberate choice
that should be documented — and the gate forces the conversation.

The dialect matters. PostgreSQL DDL is not SQLite DDL is not MySQL
DDL, and sqlglot is the canonical parser because it understands all
three. The expected-schema YAML is dialect-agnostic in spirit but
the migration parser must be told which dialect to apply.

Nullable-only differences are treated specially. A column the
migration declares `NOT NULL DEFAULT now()` and the YAML declares
just `NOT NULL` are functionally equivalent — the default is a hint,
not a constraint divergence. The gate's job is to flag real drift,
not stylistic noise, so nullable/default differences produce PASS
with a note rather than FAIL.

## What pickled-spec does today

`pickled-data check-drift --migration <PATH> --expected <PATH>
--dialect <X>` reads one migration SQL file, parses it via sqlglot
for the named dialect, applies its DDL to an in-memory SQLite
sandbox, dumps the resulting schema, and compares to the
`expected_schema.yaml` document. The workspace gate
`data.migration_drift` runs the same check across every `*.sql`
file under `migrations/` against `expected_schema.yaml` at the
workspace root.

The YAML schema is a flat `tables → columns` structure: each table
lists its columns with `name`, `type`, `nullable` (boolean). No
constraints, no indexes, no foreign keys in v0.3 — those are
roadmap items for v0.4+. The gate compares column-by-column on
`name` (exact, case-sensitive) and `type` (case-insensitive,
normalised — `TEXT` and `text` are equivalent).

Verdicts:

- PASS: every column in the YAML matches a column in the sandbox
  schema on name and type. Nullable-only divergences yield PASS
  with a note enumerating them.
- FAIL: at least one column declared in the YAML is missing from
  the sandbox, or has a different type, or vice versa.
- WARN: no migrations found, or no `expected_schema.yaml` present.

The MCP surfaces are `data_parse_sql_migration`,
`data_apply_sql_to_sandbox`, `data_check_migration_drift`, and the
LLM-backed `data_draft_sql_migration_from_intent` from PR #2.

`data_draft_sql_migration_from_intent` follows the same drafter
pattern as `bdd` and `rules` drafters: temperature 0, output
validated by sqlglot post-completion, warnings on parse failure,
plus a destructive-operation flag — any `DROP TABLE` in the emitted
SQL produces a warning of shape `destructive operation on line N`,
visible to the user before they apply the migration.

## What we want to verify

Across the CLI and MCP surfaces:

- A migration that creates a table matching the YAML
  column-for-column yields PASS on `data.migration_drift`.
- A migration that adds a column not in the YAML, or omits a
  column the YAML declares, yields FAIL with the offending column
  name in the gate notes.
- A column whose type differs between migration and YAML
  (`INTEGER` vs `TEXT`) yields FAIL; case differences in the type
  string do not (`TEXT` == `text`).
- A column whose only difference is nullability or default value
  yields PASS with a note enumerating the nullable-tolerant
  divergences. The note is observable in the gate output, so a
  reviewer can spot accumulating tolerance.
- A workspace with no `migrations/*.sql` files yields WARN, not
  FAIL.
- A workspace with `migrations/` but no `expected_schema.yaml`
  yields WARN with `no expected_schema.yaml`, not FAIL.
- The dialect argument is respected: PostgreSQL-only syntax in a
  migration fails to parse under `--dialect sqlite` and produces a
  clear FAIL with the sqlglot error message; the same migration
  passes under `--dialect postgres`.
- The drafter's destructive-operation flag fires on any
  `DROP TABLE` (case-insensitive), and the warning includes the
  line number. The drafter still returns the SQL — it does not
  refuse — so the user can review and decide.
- Identical inputs to the drafter hit the disk cache.

## Inventory references

- CLI: `pickled-data check-drift --migration <X> --expected <Y>
  --dialect <Z>`, `pickled-data parse <PATH>`,
  `pickled-data draft --intent <PATH|-> --dialect <X>`
- MCP tools: `data_parse_sql_migration`,
  `data_apply_sql_to_sandbox`, `data_check_migration_drift`,
  `data_draft_sql_migration_from_intent`
- Gates: `data.parse.<filename>` and `data.migration_drift`
  (entry point names), `MigrationDriftGate` (class)
- ADRs: ADR-0005 (LLM resolution for the drafter)

## Open questions

- Migrations apply in lexical order today (`001_*.sql`,
  `002_*.sql`, ...). The order is unenforced — a migration named
  `002_a.sql` and one named `02_b.sql` would sort in an order
  that surprises most readers. Candidate for a `migration-
  filenames-numerically-ordered` strict rule promoted from
  advisory, plus a `--check-ordering` flag.
- The sandbox is always SQLite, regardless of `--dialect`. This is
  acceptable for shape verification (column names and types) but
  any constraint or trigger that behaves differently across
  dialects is invisible to the gate. Foreign keys, check
  constraints, and triggers are all v0.4 territory.
- Nullable tolerance is currently unconditional. There is no flag
  to make a particular column's nullability strict. A team that
  cares deeply about a specific column being `NOT NULL` cannot
  express that today; they get a PASS with a note that may go
  unread. Candidate for per-column strictness markers in the YAML.
- The drafter does not consult the existing `expected_schema.yaml`
  when generating new migrations. A `--current-schema` flag exists
  but is optional. Defaulting to "always read the expected schema
  when generating a migration in the workspace" would close a
  whole class of drafter-vs-actual-schema mistakes; arguably it
  should be the default with an opt-out.

## Status

draft
