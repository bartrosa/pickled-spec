# ADR-0005: `pickled-spec mine` staged mining pipeline

- **Status:** Accepted
- **Date:** 2026-05-28
- **Deciders:** pickled-spec contributors

## Context

Hand-running the dogfood loop (inventory → story → feature → tag → gates)
did not scale across dozens of CLI commands, MCP tools, and packages.
We needed a generic extractor that works on arbitrary Python repos, not a
one-off script tied to this monorepo.

Early inventory runs missed umbrella MCP tools when `pickled-spec` lived
on a workspace member rather than the root `pyproject.toml`. Story
generation was initially sequential and could run for many minutes on a
large repo without scoping.

## Decision drivers

- Work on any Python repo with Click-discoverable CLIs, not only
  pickled-spec.
- Stage isolation: re-run one stage from files on disk.
- Graceful degradation without an LLM (placeholders, skip features).
- Actionable errors when stages run out of order.
- Performance controls (`--surfaces`, parallel quick mode, existing cache).

## Considered options

1. **Monolithic `mine` command** — single run, no intermediate artifacts.
   Rejected: hard to debug, expensive to repeat one step, poor fit for
   human review between stages.

2. **Staged pipeline with filesystem contract (chosen)** — each stage reads
   and writes under `--output`. Enables `mine all` and individual
   subcommands.

3. **MCP-first mining** — expose stages only as MCP tools. Deferred: CLI
   first; MCP surface for mine is future work.

## Decision outcome

Ship `pickled-spec mine` with six stages: inventory, stories, features,
tag, evaluate, report. Stages communicate via `inventory.json`,
`stories/`, `features/`, `tags-proposals.json`, and `evaluation/*.json`.
`mine all` orchestrates the chain; `--surfaces` filters work per stage.

MCP umbrella detection scans the target root and uv workspace members
for `pickled-spec` (or `pickled.mcp.subservers`). Rule set paths in
`--ruleset-config` resolve relative to the config file directory.

Ambiguity evaluation reuses `pickled_bdd.cli.run_ambiguity_gate`, the
same entry point as `pickled-bdd check --gate ambiguity` and the
`pickled-bdd ambiguity` alias.

## Consequences

**Positive**

- Mining is separate from dogfood: dogfood is one consumer of the same
  tools.
- Re-runnable stages and inspectable artifacts.
- Scoped runs via `--surfaces` keep LLM stages practical on monorepos.

**Negative**

- Disk layout is a public contract; changes need versioning care.
- Full monorepo mining without `--surfaces` remains LLM-heavy.
- Evaluate reports gate verdicts as-is; AmbiguityGate threshold tuning is
  out of scope for mine.

## Future work

- Multi-language inventory (non-Python CLIs).
- MCP tools wrapping mine stages.
- AmbiguityGate calibration as its own change set.
