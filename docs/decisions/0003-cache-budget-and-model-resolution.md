# ADR-0003: Cache, budget, and model resolution for leaf MCP and CLI

- **Status:** Accepted
- **Date:** 2026-05-25
- **Deciders:** pickled-spec contributors

## Context

`pickled-core` already ships disk-backed `LLMCache`, a `BudgetGuard`, and
per-provider `default_model` entries in `pickled.config.yaml`. Until this
change, leaf MCP servers and package CLIs called `build_client(...)` without
`cache=`, so cached completions were never reused. No bootstrap path installed
a budget guard, so agent-driven loops had no deterministic cost ceiling.

`complete_prompt` hardcoded `DEFAULT_MODEL = "claude-3-5-sonnet-20241022"`,
which is deprecated upstream. MCP-invoked drafters (`FeatureDrafter`,
`OpenAPIDrafter`, `IaCDrafter`) therefore 404ed even when the YAML named a
current model. The provider's `default_model` was parsed but not stored on the
client or consulted by `complete_prompt`.

## Decision drivers

- Reduce token spend on repeated dogfood runs without changing gate semantics.
- Provide an upper bound on runaway LLM loops in long-lived MCP processes.
- Honor `default_model` from configuration for every one-shot drafter.
- One construction path shared by bdd, schema, and iac (no duplicated factory
  parsing in each leaf).
- No new third-party dependencies; existing configs must keep working.
- Relative `cache.dir` should resolve against the loaded YAML directory.

## Considered options

1. **Env vars only** — cache and budget via `PICKLED_*` with no schema change.
   Rejected: easy to omit in docs; no checked-in defaults for dogfood.

2. **YAML schema extension + env overrides (chosen)** — optional `cache:` and
   `budget:` on `PickledConfig`, env wins on conflict; `build_default_client`
   composes cache, budget, and provider; `default_model` threaded through
   `build_client` to each provider client; `complete_prompt` resolves model
   from the client when not passed explicitly.

3. **Per-leaf YAML keys** — duplicate cache/budget blocks in each package.
   Rejected: four copies of the same parsing and drift risk.

## Decision

Extend `PickledConfig` with optional `cache:` and `budget:` blocks and
`source_path` when loading a file. Add `build_default_client` in
`pickled-core` that installs `BudgetGuard`, builds `LLMCache` unless mode is
`off`, and calls `build_client(provider, config=cfg, cache=cache)`.

Each provider client accepts `default_model` (with a package-local default).
`complete_prompt` resolves `model` as: explicit argument, then
`client.default_model`, then module `DEFAULT_MODEL`.

Leaf MCP CLIs and `pickled-bdd` CLI delegate `_build_llm_client()` to
`build_default_client` with package-specific `PICKLED_*_LLM_FACTORY` env vars.
Umbrella `build_server()` paths suppress `click.ClickException` so missing
optional deps or config still register deterministic tools.

## Consequences

**Positive**

- Large reduction in token spend on dogfood reruns when cache is enabled.
- Deterministic cost ceiling when `budget.max_cost_usd` or env cap is set.
- LLM drafters use the configured model; no stale hardcoded model string.
- Four duplicated `_build_llm_client()` implementations collapse to one helper
  pattern plus shared bootstrap.

**Negative**

- `PickledConfig.source_path` adds mild API surface growth.
- Long-lived MCP servers share one process-wide budget guard until reset
  (documented future work).
- Relative `PICKLED_CACHE_DIR` env override remains CWD-relative by design.

## Path semantics

Relative `cache.dir` in YAML resolves against `source_path.parent` (the
directory containing `pickled.config.yaml`). When `PICKLED_CACHE_DIR` is set,
relative values resolve against the process CWD. Absolute paths are unchanged.

## Future work

- Per-run budget reset for long-lived MCP servers.
- Programmatic cache invalidation API.
- Thread `build_default_client` through rules, data, and diff when those
  packages gain LLM-backed MCP tools.
