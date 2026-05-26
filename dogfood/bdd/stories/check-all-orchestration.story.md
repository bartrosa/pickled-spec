# Story: pickled-spec check-all orchestrates every workspace gate

## Context

Each leaf package — bdd, rules, schema, iac, data, diff — has its own
gates, its own CLI, its own MCP server. This is the right modular
design at the package level, but it is the wrong workflow at the
project level. No engineer wants to run six commands in sequence
and remember which exit codes mean what across six different tools.

`pickled-spec check-all` exists to be the one command. Point it at a
workspace, and it runs every gate every package has registered under
the `pickled.gates` entry point, in one process, with one unified
output table, one exit code, and one common policy for what counts
as PASS / WARN / FAIL.

This is also the gate runner pickled-spec turns on itself. The
`dogfood/` workspace declares ten rulesets, a few features, soon a
schema and migrations, and `check-all` is the one command that
verifies the project's internal claims about itself. If `check-all
--workdir dogfood/` ever fails on `main`, the project has shipped
broken self-verification — a regression worse than any feature bug,
because it means we no longer know whether the tools work.

The exit-code policy is deliberate. `--warn-ok` exists because a
workspace can legitimately have skippable gates (missing Terraform,
no Trivy, no LLM for AmbiguityGate) and CI configurations differ on
whether that should fail. The default exits 1 on any WARN; --warn-ok
collapses WARN to 0. FAIL is always 2. This three-state ladder
mirrors `Verdict`.

## What pickled-spec does today

`pickled-spec check-all --workdir <DIR> [--warn-ok]` discovers every
package that registers a callable under the `pickled.gates` entry
point group. Each callable receives the workspace `Path` and returns
a `list[GateResult]`. The runner collates results across packages,
prints them as a table (`package | gate | verdict | findings |
notes`), and exits with the aggregate code.

Entry points discovered today come from six packages:

- `pickled-bdd` → `bdd.parse.<filename>`, `bdd.ambiguity`
- `pickled-rules` → `rules.coverage` (single-ruleset form) or
  `rules.coverage.<short_name>` per ruleset (multi-ruleset form,
  ADR-0006)
- `pickled-schema` → `schema.openapi.validate.<filename>`,
  `schema.coverage`
- `pickled-iac` → `iac.validate`, `iac_security_baseline`
- `pickled-data` → `data.parse.<filename>`, `data.migration_drift`
- `pickled-diff` → `diff.config` (warns when no `pickled.diff.yaml`
  found)

Aggregation rules:

- Any FAIL anywhere → exit 2.
- Any WARN anywhere with no FAIL → exit 1, unless `--warn-ok`
  collapses to 0.
- All PASS (or no gates configured) → exit 0.

Output is plain text, tab-separated columns, designed to be
grep-able and to look the same in a CI log as on a terminal. There
is no `--format json` flag today.

Missing workspace files are handled per gate, not globally — a
workspace with no `features/` is not an error for the runner; it
just produces WARN rows from the gates that wanted features and
PASS rows from the gates that didn't.

## What we want to verify

- `check-all --workdir <DIR>` discovers every package registering
  under `pickled.gates` without the runner code needing to know
  package names statically. A new package that registers an entry
  point appears in the output without runner changes.
- An empty workspace (just `pickled.ruleset.yaml`, nothing else)
  yields a deterministic table of WARN rows — one per gate that
  required input it didn't find — and exits 1 (or 0 with
  `--warn-ok`), never 2.
- A workspace where one gate FAILs exits 2 regardless of other
  gates' verdicts. WARNs and PASSes from other gates still appear
  in the output; the runner does not short-circuit.
- A workspace where every gate PASSes exits 0.
- A workspace where every gate WARNs (no FAIL) exits 1 by
  default, 0 with `--warn-ok`.
- The single-ruleset `pickled.ruleset.yaml` form yields exactly
  one row named `rules.coverage` (preserves backward
  compatibility for `examples/user-management-crud/`).
- The multi-ruleset `rulesets:` form yields one row per ruleset,
  each named `rules.coverage.<short_name>`.
- Output column order is stable: `package`, `gate`, `verdict`,
  `findings`, `notes`. Tools downstream can grep on column
  position.
- The runner does not write to stdout from any gate's internal
  logging — gate progress and warnings go to stderr, the final
  table goes to stdout. (This is the project-wide stdio hygiene
  rule applied at the runner level.)
- A package whose entry-point callable raises does not crash the
  runner; the offending package's row in the table is FAIL with
  the exception message in notes, other packages continue.

## Inventory references

- CLI: `pickled-spec check-all --workdir <DIR> [--warn-ok]`
- MCP tools: none — `check-all` is intentionally CLI-only because
  its job is process-level orchestration, not a per-call
  primitive. Individual gates have MCP surfaces.
- Gates: discovered via `importlib.metadata.entry_points(group=
  "pickled.gates")`; one runner callable per package
- ADRs: ADR-0002 (entry point discovery), ADR-0006 (multi-ruleset)

## Open questions

- JSON output format. The table is grep-friendly but not
  machine-readable. CI integrations want `--format json` for
  programmatic inspection. Candidate for v0.4 with a stable
  schema published under `dogfood/inventory_schema.json` shape.
- Parallelism. Each gate is currently called sequentially. Gates
  that shell out (terraform validate, trivy config) dominate wall
  time. A `--workers N` flag would help, but introduces
  nondeterministic interleaving in stderr output and complicates
  cumulative cost reporting from LLM-backed gates. Tied to the
  similar question in `diff-oracle.story.md`.
- A package's entry-point callable raising must downgrade
  gracefully today — the runner catches it and FAILs only that
  package — but the exception type lost in stringification is a
  recurrent ergonomic complaint. Tracked under
  `llm-failure-modes-typed-not-stringly` even though the issue
  is broader than LLM gates.
- Gate ordering in the output is arbitrary today (insertion order
  from entry point discovery, which depends on import order).
  A deterministic sort (`package, gate`) would make CI diffs
  more readable but breaks any tool that depends on current
  order. Candidate for a flag and an eventual default change.

## Status

draft
