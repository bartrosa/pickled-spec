# ADR-0004: Multi-ruleset workspace configuration

- **Status:** Accepted
- **Date:** 2026-05-25
- **Deciders:** pickled-spec contributors

## Context

`pickled.ruleset.yaml` was bound to a single rule set per workspace. That forced
any project with several independent concerns — architectural invariants, OSS
hygiene checks, and domain-specific best practices — to either merge everything
into one YAML file or run multiple `pickled-rules check` invocations outside
`pickled-spec check-all`.

The workspace gate runner (`pickled_rules.gates_runner.run_all`) read only a
singular `ruleset:` path and emitted one `rules.coverage` verdict. Dogfood and
multi-concern workspaces need composable rule sets without losing per-concern
visibility in the `check-all` table.

## Decision drivers

- Composability: reuse standalone ruleset files across repos and workspaces.
- Per-concern verdicts in `check-all` output when several rule sets apply.
- Backward compatibility with existing `ruleset:` configs (including
  `examples/user-management-crud/`).
- Minimal schema surface: one list, optional `short_name`, mutual exclusion with
  the legacy key.
- No CLI or MCP changes in this iteration.

## Considered options

1. **Single umbrella ruleset** — merge all rules into one file per workspace.
   Rejected: prevents reuse of shared rulesets (e.g. OSS hygiene) and blurs
   ownership of concerns.

2. **Per-ruleset YAML keys** (`ruleset_internal:`, `ruleset_hygiene:`, …).
   Rejected: not extensible; key names become part of the contract.

3. **`rulesets:` list with backward-compatible `ruleset:` (chosen)** — plural
   list of `{path, short_name?}` entries; singular form unchanged.

## Decision outcome

Option 3. `_resolve_ruleset_entries` validates and resolves paths relative to
the workspace root. `run_all` runs `coverage_gate_features` once per entry.
When exactly one entry is configured, the gate name remains `rules.coverage`.
When multiple entries are configured, gate names are `rules.coverage.<short_name>`.

Mixing `ruleset:` and `rulesets:` in the same file raises
`RuleSetValidationError`. Duplicate `short_name` values in a list are rejected.

## Consequences

**Positive**

- Workspaces can compose orthogonal rulesets in one `check-all` run.
- Per-ruleset pass/fail rows appear in the output table without CLI changes.
- Existing single-ruleset configs work without edits.

**Neutral**

- Small internal types (`_RulesetEntry`, `_resolve_ruleset_entries`) and
  validation messages to maintain.

**Negative**

- Two equivalent configuration shapes; authors must not combine them.
- Tags for rules not matching any configured `short_name` remain silently
  ignored (existing `ruleset_filter` behaviour).

## Compatibility

The single-ruleset gate name stays exactly `rules.coverage` (no namespace
suffix). Downstream tests and integrations that assert this string keep working.
Multi-ruleset configurations use `rules.coverage.<short_name>`.

## Future work

- `--ruleset-list` on `pickled-rules check` to mirror workspace runner behaviour.
- Cross-ruleset orphan-tag detection for prefixes that match no configured
  ruleset.
